# Systemd Service Documentation

## Why Systemd Timers Instead of Cron

We migrated from traditional cron jobs to systemd timers for several important advantages:

- **Integrated logging**: All output is captured in the systemd journal, making it easy to view logs with `journalctl`
- **Service dependencies**: Timers can depend on network availability and other system conditions before executing
- **Accurate scheduling**: Handles system sleep/resume more reliably than cron
- **Real-time monitoring**: Provides detailed status reporting and statistics with `systemctl status`
- **Missed execution handling**: Can run missed jobs after system downtime with the `Persistent=true` option
- **Centralized management**: Consistent interface for managing, monitoring, and troubleshooting scheduled tasks
- **Detailed error reporting**: Better visibility into failures with organized error logs

These advantages provide more robust scheduling, improved monitoring capabilities, and easier debugging for our automated tasks.

## Service Overview

Our infrastructure includes four automated services:

| Service | Description | Schedule |
|---------|-------------|----------|
| **Zendesk IT Glue Integration** | Synchronizes data between Zendesk and IT Glue | Every hour at :15 (e.g., 1:15, 2:15) |
| **IT Glue Export Backup** | Creates backups of IT Glue data | Every Monday at 08:00 AM |
| **Jamf Pro Notifications** | Processes notifications from Jamf Pro | Every hour at :30 (e.g., 1:30, 2:30) |
| **Zendesk Statusio Integration** | Integrates Zendesk with Status.io | Every hour on the hour |

Each service consists of two components:
- A **service file** that defines what to execute
- A **timer file** that controls when the service is triggered

## Service Configuration Details

### 1. Zendesk IT Glue Integration
- **Service name**: zendesk-it-glue.service
- **Timer name**: zendesk-it-glue.timer
- **Schedule**: 15 minutes past every hour
- **Purpose**: Keeps IT Glue data in sync with Zendesk ticketing data

### 2. IT Glue Export Backup
- **Service name**: it-glue-backup.service  
- **Timer name**: it-glue-backup.timer
- **Schedule**: Every Monday at 08:00 AM
- **Purpose**: Creates weekly exports of IT Glue data for disaster recovery

### 3. Jamf Pro Notifications
- **Service name**: jamf-pro-notifications.service
- **Timer name**: jamf-pro-notifications.timer
- **Schedule**: 30 minutes past every hour
- **Purpose**: Processes device management notifications from Jamf Pro

### 4. Zendesk Statusio Integration
- **Service name**: zendesk-statusio.service
- **Timer name**: zendesk-statusio.timer
- **Schedule**: Every hour on the hour
- **Purpose**: Keeps Status.io status pages in sync with Zendesk incidents

## Detailed Example: IT Glue Backup Service

### Configuration Files

#### it-glue-backup.service
```ini
[Unit]
Description=IT Glue Export Backup
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 /usr/local/dotmobi-tools/scripts/it_glue_export_backup.py
WorkingDirectory=/usr/local/dotmobi-tools/scripts
User=root
StandardOutput=journal+console
StandardError=journal+console
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=default.target
```

#### it-glue-backup.timer
```ini
[Unit]
Description=Runs IT Glue Export Backup Every Monday at 08:00 AM

[Timer]
Unit=it-glue-backup.service
OnCalendar=Mon *-*-* 08:00:00
AccuracySec=1s
Persistent=true

[Install]
WantedBy=timers.target
```

### Configuration Options Explained

#### Service File Options

| Option | Description |
|--------|-------------|
| `Description` | Human-readable description of the service displayed in status output |
| `After=network-online.target` | Ensures the service starts only after network connectivity is established |
| `Wants=network-online.target` | Soft dependency on network connectivity (will not fail if network is unavailable) |
| `Type=oneshot` | Indicates that this service runs once then exits, rather than running continuously |
| `ExecStart` | The command to execute when the service runs |
| `WorkingDirectory` | The directory from which the script will be executed |
| `User=root` | The user account under which the script runs |
| `StandardOutput/StandardError` | Output is sent to both systemd journal and console for easier debugging |
| `Environment` | Sets environment variables for the script; PYTHONUNBUFFERED ensures real-time output logging |
| `WantedBy` | Determines which target will trigger this service |

#### Timer File Options

| Option | Description |
|--------|-------------|
| `Description` | Human-readable description of the timer |
| `Unit` | Specifies which service to activate when the timer triggers |
| `OnCalendar` | Determines when the timer activates (Mondays at 8:00 AM) |
| `AccuracySec` | How precise the timing should be (1 second accuracy) |
| `Persistent` | If true, a missed trigger (e.g., if system was off) will run once when system starts |
| `WantedBy` | Determines which target will include this timer when enabled |

## Manual Testing Procedures

These testing procedures can be applied to any of the four services by substituting the appropriate service name.

### 1. Check All Service Timers

```bash
# View all active timers
sudo systemctl list-timers --all | grep -E "zendesk|it-glue|jamf"
```

### 2. Check Specific Service Status

```bash
# Replace SERVICE_NAME with:
# - zendesk-it-glue
# - it-glue-backup
# - jamf-pro-notifications
# - zendesk-statusio

# Check timer status
sudo systemctl status SERVICE_NAME.timer

# Check service status
sudo systemctl status SERVICE_NAME.service
```

### 3. Run Service Manually

```bash
# Example for IT Glue Backup (replace with any service name)
sudo systemctl start it-glue-backup.service

# Monitor the output in real-time
sudo journalctl -fu it-glue-backup.service
```

### 4. Test Timer Configuration

```bash
# Example for checking the Zendesk IT Glue integration timer
systemd-analyze calendar "*-*-* *:15:00"

# Examples for other services:
# IT Glue Backup
systemd-analyze calendar "Mon *-*-* 08:00:00"

# Jamf Pro Notifications
systemd-analyze calendar "*-*-* *:30:00"

# Zendesk Statusio
systemd-analyze calendar "hourly" # or "*-*-* *:00:00"
```

### 5. Check Recent Logs

```bash
# View recent logs for a specific service
sudo journalctl -u SERVICE_NAME.service --since "1 hour ago"

# Check for errors only
sudo journalctl -u SERVICE_NAME.service -p err
```

## Troubleshooting

If any service fails to run properly, follow these steps:

1. **Check service status**:
   ```bash
   sudo systemctl status SERVICE_NAME.service
   ```

2. **Examine script errors**:
   ```bash
   sudo journalctl -u SERVICE_NAME.service -p err
   ```

3. **Verify script exists and has correct permissions**:
   ```bash
   # Example for IT Glue Backup
   sudo ls -la /usr/local/dotmobi-tools/scripts/it_glue_export_backup.py
   ```

4. **Reset failed status** (if service is in failed state):
   ```bash
   sudo systemctl reset-failed SERVICE_NAME.service
   ```

5. **Verify script manually**:
   ```bash
   cd /usr/local/dotmobi-tools/scripts
   # Replace with appropriate script name
   sudo /usr/bin/python3 it_glue_export_backup.py
   ```

## Maintenance Tasks

### Modifying Service Schedules

To change when a service runs:

1. Edit the timer file:
   ```bash
   sudo nano /etc/systemd/system/SERVICE_NAME.timer
   ```

2. Modify the `OnCalendar` line with a new schedule using systemd calendar format.

3. Reload systemd and restart the timer:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl restart SERVICE_NAME.timer
   ```

### Common Calendar Formats

| Pattern | Description | Example |
|---------|-------------|---------|
| `*-*-* HH:MM:SS` | Specific time every day | `*-*-* 04:00:00` (4 AM daily) |
| `hourly` | Every hour at minute 0 | Same as `*-*-* *:00:00` |
| `daily` | Every day at midnight | Same as `*-*-* 00:00:00` |
| `weekly` | Every Monday at midnight | Same as `Mon *-*-* 00:00:00` |
| `monthly` | First day of month at midnight | Same as `*-*-01 00:00:00` |
| `Fri *-*-* 19:00:00` | Every Friday at 7 PM | |
| `*-01-01 00:00:00` | January 1st of each year | |

### Viewing Log Files

All services write logs to:
```bash
/usr/local/api/logs/
```

You can check the most recent logs with:
```bash
ls -la /usr/local/api/logs/ | tail -n 10
```

---

This guide should help you understand, test, and maintain our systemd services. If you encounter any issues not covered here, please contact the IT infrastructure team.
