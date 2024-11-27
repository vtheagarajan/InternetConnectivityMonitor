
### Command Line Arguments

- `--check_interval` or `-c`: Set the interval between checks in seconds (default: 2)
- `--sim_fail` or `-s`: Enable simulation mode to randomly fail 1 in 10 connectivity checks (default: False)

## Output Files

The script creates a `Logs` directory with the following files:

- `outage_log.csv`: Records details of each outage including:
  - Date
  - Start Time
  - End Time
  - Duration (seconds)
  
- `connection_log.csv`: Records all connectivity checks including:
  - Log Time
  - Connection Status

- `email.txt`: Logs all email notifications sent

## How It Works

1. The script performs regular connectivity checks to the specified URL
2. When an outage is detected:
   - The start time is recorded
   - The outage is logged
3. When connectivity is restored:
   - An email notification is sent with outage details
   - The outage duration is calculated and logged
4. All connection checks are continuously logged

## Error Handling

- Failed email notifications are logged to console
- CSV writing errors are captured and reported
- Network timeout is set to 5 seconds for connectivity checks

## Notes

- Email notifications are only sent when connectivity is restored
- The script requires proper SMTP server configuration for email notifications
- Logs are automatically created in a `Logs` directory
