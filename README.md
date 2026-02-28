# OpenTelemetry → SigNoz Demo

A single-file Python application that sends **traces**, **metrics**, and **logs** to [SigNoz Cloud](https://signoz.io/) using OpenTelemetry. No frameworks, no traffic generators — just one script that produces realistic telemetry data you can explore in the SigNoz UI.

## What It Does

Every few seconds the app simulates an HTTP request and emits:

| Signal | Details |
|--------|---------|
| **Traces** | A parent `handle_request` span with `validate_input` and `call_database` child spans |
| **Metrics** | A `demo.requests` counter and a `demo.latency` histogram, both tagged by endpoint and status |
| **Logs** | Structured log lines (info + occasional errors) with trace context automatically correlated |

~20% of simulated requests produce errors so you get interesting data to investigate.

---

## Prerequisites

- **Python 3.9+**
- **Git** — needed to download this repo (install instructions in step 1 below)
- **Access to the SigNoz demo account** — login credentials and your ingestion key will be provided in a separate email from your interviewer

---

## Getting Started

### 1. Install Git (if you don't have it)

Open a terminal and check if Git is already installed:

```bash
git --version
```

If you see something like `git version 2.39.0`, you're good — skip to step 2.

**macOS**

Run `git --version` in your terminal. If Git isn't installed, macOS will automatically prompt you to install it via Xcode Command Line Tools — click Install and wait for it to finish.

**Windows**

Download and install from [git-scm.com/downloads](https://git-scm.com/downloads). Use the default options during installation. After installing, open a new Command Prompt or PowerShell window and verify with `git --version`.

**Linux (Ubuntu / Debian)**

```bash
sudo apt update
sudo apt install git
```

### 2. Install Python (if you don't have it)

Open a terminal and check if Python is already installed:

```bash
python3 --version
```

If you see something like `Python 3.11.5`, you're good — skip to step 2.

If the command is not found, follow the instructions for your operating system:

**macOS**

The easiest way is to install via [Homebrew](https://brew.sh/). If you don't have Homebrew, install it first by pasting this into your terminal:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Then install Python:

```bash
brew install python
```

**Windows**

Download the installer from [python.org/downloads](https://www.python.org/downloads/). Run it, and **make sure to check the box that says "Add Python to PATH"** before clicking Install. After installation, open a new Command Prompt or PowerShell window and verify with:

```bash
python --version
```

> Note: On Windows the command may be `python` instead of `python3`. Use whichever one works throughout the rest of these steps.

**Linux (Ubuntu / Debian)**

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### 3. Clone the repo

```bash
git clone <repo-url>
cd otel-signoz-demo
```

### 4. Create a virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate   # macOS / Linux
# venv\Scripts\activate    # Windows
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Create an ingestion key

Log in to the SigNoz demo account and create a new ingestion key by following the steps here: [SigNoz — Ingestion Keys](https://signoz.io/docs/ingestion/signoz-cloud/keys/)

### 7. Set your SigNoz credentials

```bash
export SIGNOZ_ENDPOINT="ingest.in.signoz.cloud:443"
export SIGNOZ_INGESTION_KEY="<your-ingestion-key>"
```

> **Note:** Make sure to replace the entire `<your-ingestion-key>` placeholder, including the `<` and `>` characters, so only the bare key remains between the quotes. For example: `export SIGNOZ_INGESTION_KEY="abc123xyz"`

### 8. Run the app

```bash
python otel_signoz_demo.py
```

You should see output like:

```
✦  OTel demo running — sending to ingest.us.signoz.cloud:443
   Service: otel-signoz-demo
   Emitting every 5s  (Ctrl+C to stop)

Incoming request to /api/orders
Completed /api/orders → ok (132 ms)
```

### 9. View your data in SigNoz

Open your SigNoz Cloud dashboard. Within a minute or two you should see:

- **Services → `otel-signoz-demo`** — the service will appear in the services list
- **Traces** — filter by service name to see request traces with child spans
- **Dashboards / Metrics** — query for `demo.requests` or `demo.latency`
- **Logs** — filter by `service.name = otel-signoz-demo` to see correlated log entries

---

## Stopping the App

Press `Ctrl+C`. The app will gracefully flush any remaining telemetry data before exiting.
