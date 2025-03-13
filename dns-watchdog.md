# DNS Watchdog Service Setup Guide

This guide explains how to set up a DNS watchdog service that monitors DNS resolution for a specific domain and takes corrective action when it fails. The service uses `resolvectl` for DNS diagnostics and automatically attempts to restore connectivity.

## 1. Create the Watchdog Script

Create the script file at `/usr/local/bin/dns_watchdog.sh`:

```bash
#!/bin/bash
# dns_watchdog.sh
# This script checks if a specific URL resolves.
# If it fails, it restarts the networking service.

# The URL (or subdomain) to check.
TARGET_URL="your.subdomain.example.com"

# How often to check (in seconds)
CHECK_INTERVAL=60

# Log file location
LOG_FILE="/usr/local/api/logs/dns_watchdog_service.log"

# Make sure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Function to log messages
log_message() {
    echo "$(date): $1" | tee -a "$LOG_FILE"
}

# Function to check DNS resolution using resolvectl
check_dns_resolution() {
    # Check the exit status of resolvectl query, not its output
    resolvectl query "$TARGET_URL" > /dev/null 2>&1
    return $?
}

# Log script startup
log_message "DNS Watchdog service started. Monitoring $TARGET_URL every $CHECK_INTERVAL seconds."

while true; do
    # Check DNS resolution using the function
    if ! check_dns_resolution; then
        log_message "DNS resolution for $TARGET_URL FAILED."
        
        # Get DNS statistics before taking action
        DNS_STATS=$(resolvectl statistics)
        log_message "Current DNS statistics: $DNS_STATS"
        
        # Try flushing DNS caches first
        log_message "Attempting to flush DNS caches..."
        resolvectl flush-caches
        
        # Wait a moment for the flush to take effect
        sleep 2
        
        # Check if flushing caches fixed the issue
        if check_dns_resolution; then
            log_message "DNS resolution for $TARGET_URL SUCCESSFUL after cache flush."
        else
            log_message "Cache flush didn't resolve the issue. Attempting to restart networking service..."
            
            # Restart systemd-networkd (the system's network service)
            systemctl restart systemd-networkd
            
            # Log the restart status
            if [ $? -eq 0 ]; then
                log_message "Network service restart completed successfully."
                
                # Wait a moment for network to fully initialize
                sleep 5
                
                # Test DNS resolution again after network restart
                if check_dns_resolution; then
                    log_message "DNS resolution for $TARGET_URL SUCCESSFUL after network restart."
                else
                    log_message "DNS resolution for $TARGET_URL still FAILED after network restart."
                fi
            else
                log_message "ERROR: Failed to restart network service!"
            fi
        fi
    else
        # Enable successful resolution logging with CloudWatch friendly format
        log_message "DNS resolution for $TARGET_URL SUCCESSFUL."
    fi
    sleep "$CHECK_INTERVAL"
done
```

## 2. Make the Script Executable

```bash
sudo chmod +x /usr/local/bin/dns_watchdog.sh
```

## 3. Create the SystemD Service File

Create a service file at `/etc/systemd/system/dns-watchdog.service`:

```
[Unit]
Description=DNS Watchdog Service
After=network-online.target

[Service]
ExecStart=/usr/local/bin/dns_watchdog.sh
Restart=always
User=root
# Ensure service has access to create and write logs
WorkingDirectory=/
StandardOutput=append:/usr/local/api/logs/dns_watchdog_service.log
StandardError=append:/usr/local/api/logs/dns_watchdog_service.log

[Install]
WantedBy=default.target
```

## 4. Configure the Service

1. **Customize the script**: Edit `/usr/local/bin/dns_watchdog.sh` and change the `TARGET_URL` to the domain you want to monitor. Adjust the `CHECK_INTERVAL` if needed.

2. **Create log directory**: Make sure the log directory exists:
   ```bash
   sudo mkdir -p /usr/local/api/logs
   ```

## 5. Enable and Start the Service

```bash
# Reload systemd to recognize the new service file
sudo systemctl daemon-reload

# Enable the service to start at boot
sudo systemctl enable dns-watchdog.service

# Start the service
sudo systemctl start dns-watchdog.service
```

## 6. Check Service Status

```bash
# Check if the service is running
sudo systemctl status dns-watchdog.service

# View logs
sudo journalctl -u dns-watchdog.service -f
```

## 7. Monitor Logs in CloudWatch

If you're using CloudWatch for log monitoring:

1. Configure your CloudWatch agent to collect logs from: `/usr/local/api/logs/dns_watchdog_service.log`

2. Create filters:
   - For successful resolutions: `DNS resolution for * SUCCESSFUL`
   - For failed resolutions: `DNS resolution for * FAILED`

## Troubleshooting

- **Service won't start**: Check permissions on the script file and log directory
- **Network doesn't restart properly**: Double check systemd-networkd service status with `systemctl status systemd-networkd`
- **Logs not appearing**: Check the log file permissions and that the directory exists

## Advanced Configuration

- **Monitor multiple domains**: Modify the script to check multiple domains in a loop
- **Add email notifications**: Add code to send email alerts when failures occur
- **Custom recovery actions**: Modify the script to take different recovery actions specific to your environment
