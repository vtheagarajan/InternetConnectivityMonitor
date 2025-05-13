
# Internet Connectivity Monitor

A Python service that monitors internet connectivity and logs outages.

## Features

- Continuous internet connectivity monitoring
- Detailed outage logging with duration tracking
- Email notifications for connectivity restoration
- CSV-based logging system
- Runs as a system service
- Automatic startup on system boot
- Configurable check intervals

## Setup

1. Clone the repository
2. Create virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```


### Install dependencies:

```
pip install -r requirements.txt
```

### Configure environment variables:

```
cp .env.example .env
```

### Edit the .env file with your settings:

CHECK_INTERVAL: Time between checks in seconds (default: 10)

SMTP_SERVER: Your SMTP server address

SMTP_PORT: SMTP server port

SMTP_USERNAME: Email username

SMTP_PASSWORD: Email password

NOTIFICATION_EMAIL: Email address to receive notifications

## Deployment
Make the deployment script executable:

```
chmod +x deploy.sh
```

Run the deployment script:

```
./deploy.sh
```

This will:

Create necessary directories

Set up the service

Start the monitoring service

## Service Management
The application runs as a Linux service, allowing for automatic startup and easy management.

## Service Commands
### Start the service
sudo systemctl start connectivity-monitor

### Stop the service
sudo systemctl stop connectivity-monitor

### Restart the service
sudo systemctl restart connectivity-monitor

### Check service status
sudo systemctl status connectivity-monitor

### Enable service to start on boot
sudo systemctl enable connectivity-monitor

### Disable service from starting on boot
sudo systemctl disable connectivity-monitor


## Service Logs
### View service logs using:

journalctl -u connectivity-monitor

## Command Line Arguments
--sim_fail or -s: Enable simulation mode to randomly fail 1 in 10 connectivity checks (default: False)

### Output Files
The script creates a Logs directory with the following files:

#### outage_log.csv: Records details of each outage including:

- Date

- Start Time

- End Time

- Duration (seconds)

#### connection_log.csv: Records all connectivity checks including:

- Log Time

- Connection Status

#### email.txt: Logs all email notifications sent

## How It Works
The script performs regular connectivity checks to the specified URL

When an outage is detected:

- The start time is recorded

- The outage is logged

When connectivity is restored:

- An email notification is sent with outage details

- The outage duration is calculated and logged

All connection checks are continuously logged

#### Error Handling
- Failed email notifications are logged to console

- CSV writing errors are captured and reported

- Network timeout is set to 5 seconds for connectivity checks

- Service failures are logged to systemd journal

## Configuration
### Environment Variables
The following environment variables can be configured in the .env file:

| Variable            | Description                 | Default  |
|---------------------|-----------------------------|----------|
| CHECK_INTERVAL      | Time between checks (seconds) | 10       |
| SMTP_SERVER         | SMTP server address         | None     |
| SMTP_PORT           | SMTP server port            | None     |
| SMTP_USERNAME       | Email username              | None     |
| SMTP_PASSWORD       | Email password              | None     |
| NOTIFICATION_EMAIL  | Notification recipient

## Service Configuration
The service configuration file is located at:

```
/etc/systemd/system/connectivity-monitor.service
```

## Notes
- Email notifications are only sent when connectivity is restored

- The script requires proper SMTP server configuration for email notifications

- Logs are automatically created in a Logs directory

- The service runs with system privileges

- Log rotation is handled automatically by the system

- Service configuration files are located in /etc/systemd/system/

## Troubleshooting
If the service fails to start:

- Check the service logs using journalctl

- Verify environment variables in .env

- Ensure proper permissions on directories

If email notifications aren't working:

- Verify SMTP settings in .env

- Check email.txt for error logs

- Ensure network access to SMTP server

For permission issues:

- Verify the service user has write access to the Logs directory

- Check file ownership and permissions

Common service issues:

- Service won't start: Check system logs and verify dependencies

- Service crashes: Check for Python exceptions in journal logs

- Email failures: Verify SMTP settings and network connectivity

## Security Considerations
- SMTP credentials are stored securely in .env file

- Service runs with limited system privileges

- All sensitive data is accessed via environment variables

- Network timeouts prevent hanging processes

- Error logging excludes sensitive information

## Contributing
- Fork the repository

- Create a feature branch

- Commit your changes

- Push to the branch

- Create a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details

