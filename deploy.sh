#!/bin/bash

# Load only deployment-related environment variables
if [ -f .env ]; then
    # Only extract REMOTE_* variables for shell usage
    export $(grep '^REMOTE_' .env | sed 's/ *= */=/' | sed 's/"//g' | xargs)
fi

# Function to check if service exists
check_service_exists() {
    ssh ${REMOTE_USER}@${REMOTE_HOST} "systemctl list-unit-files | grep internet_connectivity_monitor" > /dev/null 2>&1
    return $?
}

# Function to setup virtual environment and install dependencies
setup_venv() {
    echo "Setting up virtual environment..."
    ssh ${REMOTE_USER}@${REMOTE_HOST} "cd ${REMOTE_APP_DIR} && \
        python3 -m venv .venv && \
        . .venv/bin/activate && \
        pip install --upgrade pip && \
        pip install -r requirements.txt && \
        echo 'Testing dotenv installation:' && \
        python -c 'import dotenv; print(dotenv.__file__)'"
}

# Function to verify installation
verify_installation() {
    echo "Verifying installation..."
    ssh ${REMOTE_USER}@${REMOTE_HOST} "cd ${REMOTE_APP_DIR} && \
        echo 'Python path:' && \
        .venv/bin/python3 -c 'import sys; print(sys.executable)' && \
        echo 'Installed packages:' && \
        .venv/bin/pip freeze | grep dotenv"
}

# Function to create systemd service
create_service() {
    echo "Creating systemd service..."
    
    # Create service file content - note the path to Python interpreter
    SERVICE_CONTENT="[Unit]
    Description=Internet Connectivity Monitor Service
    After=network.target

    [Service]
    Type=simple
    User=${REMOTE_USER}
    WorkingDirectory=${REMOTE_APP_DIR}
    Environment=PYTHONUNBUFFERED=1
    Environment=PYTHONPATH=${REMOTE_APP_DIR}
    ExecStart=${REMOTE_APP_DIR}/.venv/bin/python3 ${REMOTE_APP_DIR}/InternetConnectivityMonitor.py
    Restart=on-failure
    RestartSec=5s
    StartLimitIntervalSec=60
    StartLimitBurst=3

    [Install]
    WantedBy=multi-user.target"

    # Copy service file to remote system
    echo "${SERVICE_CONTENT}" | ssh ${REMOTE_USER}@${REMOTE_HOST} "sudo tee /etc/systemd/system/internet_connectivity_monitor.service > /dev/null"
    
    # Reload systemd, enable and start service
    ssh ${REMOTE_USER}@${REMOTE_HOST} "sudo systemctl daemon-reload && \
                                      sudo systemctl enable internet_connectivity_monitor"
}

# Create remote directory if it doesn't exist
ssh ${REMOTE_USER}@${REMOTE_HOST} "mkdir -p ${REMOTE_APP_DIR}"

# Copy files to remote server (excluding logs and git files)
rsync -av --exclude '*.log' \
         --exclude '.git/' \
         --exclude '__pycache__/' \
         --exclude 'deploy.sh' \
         --exclude '.venv/' \
         ./ ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_APP_DIR}/

# Setup virtual environment and install dependencies
setup_venv

# Verify installation
verify_installation

# Check if service exists and stop it if running
if check_service_exists; then
    echo "Service exists. Stopping service..."
    ssh ${REMOTE_USER}@${REMOTE_HOST} "sudo systemctl stop internet_connectivity_monitor"
fi

# Create/update service
create_service

# Start service
echo "Starting service..."
ssh ${REMOTE_USER}@${REMOTE_HOST} "sudo systemctl daemon-reload && \
                                  sudo systemctl start internet_connectivity_monitor && \
                                  sudo systemctl status internet_connectivity_monitor"

echo "Deployment completed successfully!"
