"""
Single-file OpenTelemetry demo — emits traces, metrics, and logs to SigNoz Cloud.

Usage:
    pip install opentelemetry-api opentelemetry-sdk \
        opentelemetry-exporter-otlp-proto-grpc

    export SIGNOZ_ENDPOINT="ingest.in.signoz.cloud:443"   # or your region
    export SIGNOZ_INGESTION_KEY="your-ingestion-key-here"

    python otel_signoz_demo.py
"""

import os
import sys
import time
import random
import logging

# ── OpenTelemetry imports ────────────────────────────────────────────────────
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter

# ── Configuration ────────────────────────────────────────────────────────────
ENDPOINT = os.environ.get("SIGNOZ_ENDPOINT", "")
INGESTION_KEY = os.environ.get("SIGNOZ_INGESTION_KEY", "")
SERVICE_NAME = os.environ.get("OTEL_SERVICE_NAME", "otel-signoz-demo")
INTERVAL_SEC = int(os.environ.get("EMIT_INTERVAL", "5"))

if not ENDPOINT or not INGESTION_KEY:
    sys.exit(
        "ERROR: Set SIGNOZ_ENDPOINT and SIGNOZ_INGESTION_KEY env vars.\n"
        "  export SIGNOZ_ENDPOINT='ingest.in.signoz.cloud:443'\n"
        "  export SIGNOZ_INGESTION_KEY='<your-key>'"
    )

HEADERS = {"signoz-ingestion-key": INGESTION_KEY}

# ── Shared resource (attached to every signal) ──────────────────────────────
resource = Resource.create({"service.name": SERVICE_NAME})

# ── Traces ───────────────────────────────────────────────────────────────────
trace_exporter = OTLPSpanExporter(endpoint=ENDPOINT, headers=HEADERS)
tracer_provider = TracerProvider(resource=resource)
tracer_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)

# ── Metrics ──────────────────────────────────────────────────────────────────
metric_exporter = OTLPMetricExporter(endpoint=ENDPOINT, headers=HEADERS)
metric_reader = PeriodicExportingMetricReader(metric_exporter, export_interval_millis=5000)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter(__name__)

request_counter = meter.create_counter(
    name="demo.requests",
    description="Total fake requests processed",
    unit="1",
)
latency_histogram = meter.create_histogram(
    name="demo.latency",
    description="Fake request latency",
    unit="ms",
)

# ── Logs ─────────────────────────────────────────────────────────────────────
log_exporter = OTLPLogExporter(endpoint=ENDPOINT, headers=HEADERS)
logger_provider = LoggerProvider(resource=resource)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))

otel_handler = LoggingHandler(level=logging.DEBUG, logger_provider=logger_provider)
logger = logging.getLogger("demo")
logger.setLevel(logging.DEBUG)
logger.addHandler(otel_handler)
logger.addHandler(logging.StreamHandler())  # also print to console

# ── Main loop ────────────────────────────────────────────────────────────────
ENDPOINTS = ["/api/users", "/api/orders", "/api/products", "/api/health"]
STATUSES = ["ok", "ok", "ok", "ok", "error"]  # 80 % success


def simulate_request():
    """Produce one trace with child spans, bump metrics, and emit logs."""
    endpoint = random.choice(ENDPOINTS)
    status = random.choice(STATUSES)
    latency = random.uniform(20, 500) if status == "ok" else random.uniform(500, 2000)

    with tracer.start_as_current_span("handle_request", attributes={"http.route": endpoint}) as span:
        logger.info("Incoming request to %s", endpoint)

        # Simulate some "work"
        with tracer.start_as_current_span("validate_input"):
            time.sleep(random.uniform(0.01, 0.05))

        with tracer.start_as_current_span("call_database"):
            time.sleep(random.uniform(0.01, 0.1))
            if status == "error":
                span.set_status(trace.StatusCode.ERROR, "simulated failure")
                span.set_attribute("error", True)
                logger.error("Request to %s failed! (simulated)", endpoint)

        # Record metrics
        request_counter.add(1, {"endpoint": endpoint, "status": status})
        latency_histogram.record(latency, {"endpoint": endpoint, "status": status})

        logger.info("Completed %s → %s (%.0f ms)", endpoint, status, latency)


def main():
    print(f"\n✦  OTel demo running — sending to {ENDPOINT}")
    print(f"   Service: {SERVICE_NAME}")
    print(f"   Emitting every {INTERVAL_SEC}s  (Ctrl+C to stop)\n")

    try:
        while True:
            simulate_request()
            time.sleep(INTERVAL_SEC)
    except KeyboardInterrupt:
        print("\nShutting down…")
    finally:
        tracer_provider.shutdown()
        meter_provider.shutdown()
        logger_provider.shutdown()
        print("Done ✓")


if __name__ == "__main__":
    main()
