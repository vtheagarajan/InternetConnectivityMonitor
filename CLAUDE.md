# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Internet Connectivity Monitor is a Python service that continuously monitors internet connectivity, logs outages to CSV files, and sends email notifications when connectivity is restored. It runs as a systemd service on Linux (typically deployed to a Raspberry Pi).

## Commands

### Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # then edit with your settings
```

### Run Locally
```bash
python InternetConnectivityMonitor.py
python InternetConnectivityMonitor.py --sim_fail  # simulate random failures
python InternetConnectivityMonitor.py --check_interval 30  # custom interval
```

### Run Tests
```bash
pytest test_internet_connectivity_monitor.py
pytest test_internet_connectivity_monitor.py -v  # verbose
pytest test_internet_connectivity_monitor.py::test_get_last_30_days_outages  # single test
```

### Deploy to Remote Server
```bash
./deploy.sh  # deploys to remote host configured in .env (REMOTE_HOST, REMOTE_USER, REMOTE_APP_DIR)
```

### Service Management (on deployed server)
```bash
sudo systemctl start/stop/restart/status internet_connectivity_monitor
journalctl -u internet_connectivity_monitor  # view logs
```

## Architecture

Single-file Python application (`InternetConnectivityMonitor.py`) with these core functions:

- **`main()`**: Main loop that runs connectivity checks at `CHECK_INTERVAL` seconds, tracks outage state with global variables (`outage_start`, `outage_reported`), and triggers daily reports at `DAILY_REPORT_TIME`
- **`is_connected()`**: HTTP GET to `URL_TO_CHECK` with 5-second timeout
- **`send_email()`**: SMTP email with HTML body using MIMEMultipart
- **`log_outage_to_csv()` / `log_connection_to_csv()`**: Append to CSV files in `./Logs/`
- **`getLast24HrReport()`**: Counts connection checks, archives the connection log, returns last 30 days of outages
- **`get_last_30_days_outages()`**: Reads outage CSV and filters to recent records

### Log Files
- `./Logs/outage_log.csv` - Date, start time, end time, duration for each outage
- `./Logs/connection_log.csv` - Timestamp and connection status for every check
- `./Logs/error_log.txt` - Error messages with timestamps
- `./Logs/email.txt` - Sent email log
- `./Logs/archive_connection_logs/` - Daily archived connection logs

### Environment Variables
All config via `.env`: `CHECK_INTERVAL`, `URL_TO_CHECK`, `EMAIL_FROM`, `EMAIL_TO`, `EMAIL_PASSWORD`, `SMTP_SERVER`, `SMTP_PORT`, `DAILY_REPORT_TIME`, and remote deployment vars (`REMOTE_HOST`, `REMOTE_USER`, `REMOTE_APP_DIR`).
