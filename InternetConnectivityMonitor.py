import smtplib
import requests
import csv
from time import sleep
from datetime import datetime, timedelta
import random
from argparse import ArgumentParser
import os
import dotenv

dotenv.load_dotenv()

#check if dotenv is loaded
if os.environ.get("URL_TO_CHECK") is None:
    print("dotenv not loaded")
    exit(1)

# Configuration
CHECK_INTERVAL = 2  # seconds
URL_TO_CHECK = os.environ.get("URL_TO_CHECK")
EMAIL_FROM = os.environ.get("EMAIL_FROM")
EMAIL_TO = os.environ.get("EMAIL_TO")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
SMTP_SERVER = os.environ.get("SMTP_SERVER")
SMTP_PORT = os.environ.get("SMTP_PORT")
OUTAGE_LOG_FILE = "./Logs/outage_log.csv"  # Path to CSV file
CONNECTION_LOG_FILE = "./Logs/connection_log.csv"
SIMULATE_FAILURE_FOR_TESTING = False

#create Logs directory if it doesn't exist
if not os.path.exists("./Logs"):
    os.makedirs("./Logs")

#track time when outage started
outage_start = None
#track if we are currently in an outage
outage_reported = False

# Function to send email
def send_email(subject, body):
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(EMAIL_FROM, EMAIL_TO, message)
        message = f"Subject: {subject} Body: {body}\n"
        open("./Logs/email.txt", "a").write(message)
    except Exception as e:
        print(f"Failed to send email: {e}")

# Function to check internet connectivity
def is_connected():
    try:
        requests.get(URL_TO_CHECK, timeout=5)
        #randomly once out 10 times, return  a false for testing
        if SIMULATE_FAILURE_FOR_TESTING == True:
            if random.randint(1,10) == 1:
                print("Simulating internet failure")
                return False
            else:
                return True
        else:
            return True
        
    except requests.ConnectionError:
        return False

# Function to log outage details to CSV
def log_outage_to_csv(start, end, duration):
    try:
        with open(OUTAGE_LOG_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            if file.tell() == 0:  # If file is empty, write the header
                writer.writerow(["Date", "Start Time", "End Time", "Duration (seconds)"])
            writer.writerow([start.date(), start.time().strftime('%H:%M:%S'), end.time().strftime('%H:%M:%S'), f"{duration:.2f}"])

    except Exception as e:
        print(f"Failed to write to CSV: {e}")

def log_connection_to_csv(log_time, isConnected):
    try:
        with open(CONNECTION_LOG_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            if file.tell() == 0:
                writer.writerow(["Log Time", "Connected"])
            writer.writerow([log_time.strftime('%Y-%m-%d %H:%M:%S'), isConnected])

    except:
        print("Failed to write to connection log")

def main():
    global outage_start, outage_reported

    # Main loop
    while True:
        isConnected = is_connected()
        if isConnected:
            if outage_reported:
                # Outage ended, send email and log details
                outage_end = datetime.now()
                outage_duration = (outage_end - outage_start).total_seconds()
                send_email(
                    "Internet Restored",
                    f"Internet was down from {outage_start} to {outage_end}.\n"
                    f"Total downtime: {outage_duration:.2f} minutes."
                )
                log_outage_to_csv(outage_start, outage_end, outage_duration)
                outage_start = None
                outage_reported = False
        else:
            if not outage_reported:
                # Outage started, send email
                outage_start = datetime.now()
                
                #No point in trying to send email if the connectivity is down - it will not go through anyway
                #send_email(
                #    "Internet Outage Detected",
                #    f"Internet connectivity lost at {outage_start}."
                #)
                outage_reported = True

        log_connection_to_csv(datetime.now(), isConnected)
        print(f"Connection status at {datetime.now()}: {isConnected}")

        sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    parser = ArgumentParser(description="Internet Connectivity Monitor")
    parser.add_argument("--sim_fail", "-s", default=SIMULATE_FAILURE_FOR_TESTING, help="Randomly fail 1 in 10 connectivity checks for testing")
    parser.add_argument("--check_interval", "-c", type=int, default=CHECK_INTERVAL, help="Interval between checks in seconds")

    args = parser.parse_args()
    SIMULATE_FAILURE_FOR_TESTING = args.sim_fail
    CHECK_INTERVAL = args.check_interval

    print(f"Simulate failure: {SIMULATE_FAILURE_FOR_TESTING}")
    print(f"Check interval: {CHECK_INTERVAL}")

    main()
