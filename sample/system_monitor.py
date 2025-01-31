#!/usr/bin/env python3

import psutil
import datetime
import os
import sys
import json
import yaml
import requests
import syslog
import argparse
import signal
from pathlib import Path
from typing import Dict, List, Tuple, Union, Optional
from dataclasses import dataclass

# Configuration
BASE_DIR = Path("/usr/local/api")
CONFIG_DIR = Path("/etc/system-monitor")
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "system_usage.log"
JSON_LOG_FILE = LOG_DIR / "system_usage.json"
ALERT_FILE = LOG_DIR / "system_alerts.log"
CONFIG_FILE = CONFIG_DIR / "config.yaml"

# Default configuration
DEFAULT_CONFIG = {
    'thresholds': {
        'cpu': 80,    # Alert if CPU > 80%
        'memory': 90, # Alert if Memory > 90%
        'disk': 85,   # Alert if Disk > 85%
        'iowait': 20  # Alert if IO Wait > 20%
    },
    'interval': 60,  # Monitoring interval in seconds
    'webhook_url': None,  # Optional webhook URL for alerts
    'log_retention_days': 7,
    'aggregation_window': 5  # minutes
}

@dataclass
class Alert:
    """Data class for alert information."""
    level: str  # 'WARNING', 'CRITICAL'
    message: str
    timestamp: datetime.datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.datetime.now()

    @property
    def syslog_priority(self) -> int:
        """Convert alert level to syslog priority."""
        return {
            'WARNING': syslog.LOG_WARNING,
            'CRITICAL': syslog.LOG_CRIT
        }.get(self.level, syslog.LOG_INFO)

    def to_dict(self) -> dict:
        """Convert alert to dictionary for JSON serialization."""
        return {
            'level': self.level,
            'message': self.message,
            'timestamp': self.timestamp.isoformat()
        }

class SystemMetrics:
    """Class to handle system metric collection and monitoring."""
    
    @staticmethod
    def get_cpu_metrics() -> Dict[str, float]:
        """Get detailed CPU metrics without blocking."""
        try:
            cpu_times = psutil.cpu_times_percent(interval=0)
            usage = psutil.cpu_percent(interval=0)  # Non-blocking
            return {
                'usage': usage,
                'iowait': cpu_times.iowait if hasattr(cpu_times, 'iowait') else 0,
                'user': cpu_times.user,
                'system': cpu_times.system,
                'error': None
            }
        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def get_memory_metrics() -> Dict[str, Union[float, int]]:
        """Get detailed memory metrics."""
        try:
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            return {
                'usage_percent': mem.percent,
                'available_gb': round(mem.available / (1024 ** 3), 2),
                'total_gb': round(mem.total / (1024 ** 3), 2),
                'swap_percent': swap.percent,
                'swap_used_gb': round(swap.used / (1024 ** 3), 2),
                'error': None
            }
        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def get_disk_metrics() -> Dict[str, Union[float, int]]:
        """Get detailed disk metrics."""
        try:
            disk = psutil.disk_usage('/')
            io = psutil.disk_io_counters()
            return {
                'usage_percent': disk.percent,
                'available_gb': round(disk.free / (1024 ** 3), 2),
                'total_gb': round(disk.total / (1024 ** 3), 2),
                'read_mb': round(io.read_bytes / (1024 ** 2), 2),
                'write_mb': round(io.write_bytes / (1024 ** 2), 2),
                'error': None
            }
        except Exception as e:
            return {'error': str(e)}

class SystemMonitor:
    """Main system monitoring class."""

    def __init__(self, config: dict):
        self.config = config
        self.setup_logging()
        self.metrics = SystemMetrics()
        syslog.openlog('system-monitor', syslog.LOG_PID, syslog.LOG_DAEMON)
        signal.signal(signal.SIGTERM, self.handle_signal)
        signal.signal(signal.SIGINT, self.handle_signal)

    def handle_signal(self, signum, frame):
        """Handle shutdown signals gracefully."""
        print(f"\nReceived signal {signum}. Shutting down...")
        syslog.syslog(syslog.LOG_INFO, "System monitor shutting down")
        sys.exit(0)

    def setup_logging(self):
        """Ensure all required directories exist."""
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    def log_metrics_json(self, metrics: Dict, alerts: List[Alert]):
        """Log metrics in JSON format."""
        try:
            entry = {
                "timestamp": datetime.datetime.now().isoformat(),
                "hostname": os.uname().nodename,
                "metrics": metrics,
                "alerts": [alert.to_dict() for alert in alerts]
            }
            with open(JSON_LOG_FILE, "a") as f:
                json.dump(entry, f)
                f.write("\n")
        except Exception as e:
            syslog.syslog(syslog.LOG_ERR, f"Failed to write JSON log: {e}")

    def check_thresholds(self, metrics: Dict) -> List[Alert]:
        """Check if any metrics exceed thresholds."""
        alerts = []
        thresholds = self.config['thresholds']
        
        if metrics['cpu']['usage'] > thresholds['cpu']:
            alerts.append(Alert(
                'CRITICAL' if metrics['cpu']['usage'] > 90 else 'WARNING',
                f"HIGH CPU USAGE: {metrics['cpu']['usage']}%"
            ))

        if metrics['memory']['usage_percent'] > thresholds['memory']:
            alerts.append(Alert(
                'CRITICAL' if metrics['memory']['usage_percent'] > 95 else 'WARNING',
                f"HIGH MEMORY USAGE: {metrics['memory']['usage_percent']}%"
            ))

        if metrics['disk']['usage_percent'] > thresholds['disk']:
            alerts.append(Alert(
                'CRITICAL' if metrics['disk']['usage_percent'] > 95 else 'WARNING',
                f"HIGH DISK USAGE: {metrics['disk']['usage_percent']}%"
            ))

        return alerts

    def report_alerts(self, alerts: List[Alert]):
        """Report alerts through all available channels."""
        if not alerts:
            return

        for alert in alerts:
            # Log to syslog
            syslog.syslog(alert.syslog_priority, alert.message)

            # Log to alert file
            try:
                with open(ALERT_FILE, "a") as f:
                    f.write(f"[{alert.timestamp}] {alert.level}: {alert.message}\n")
            except Exception as e:
                syslog.syslog(syslog.LOG_ERR, f"Failed to write alert: {e}")

            # Send to webhook if configured
            if self.config.get('webhook_url'):
                try:
                    requests.post(
                        self.config['webhook_url'],
                        json={"text": f"🚨 {alert.level}: {alert.message}"},
                        timeout=5
                    )
                except Exception as e:
                    syslog.syslog(syslog.LOG_ERR, f"Failed to send webhook: {e}")

    def log_metrics(self, metrics: Dict):
        """Log metrics to standard log file."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            log_message = (
                f"[{timestamp}] "
                f"CPU: {metrics['cpu']['usage']}% (User: {metrics['cpu']['user']}%, System: {metrics['cpu']['system']}%), "
                f"Memory: {metrics['memory']['usage_percent']}% ({metrics['memory']['available_gb']}GB free), "
                f"Disk: {metrics['disk']['usage_percent']}% ({metrics['disk']['available_gb']}GB free)\n"
            )
            with open(LOG_FILE, "a") as f:
                f.write(log_message)
        except Exception as e:
            syslog.syslog(syslog.LOG_ERR, f"Failed to write to log file: {e}")

    def cleanup_old_logs(self):
        """Remove logs older than configured retention period."""
        retention_days = self.config.get('log_retention_days', 7)
        cutoff = datetime.datetime.now() - datetime.timedelta(days=retention_days)
        
        for log_file in [LOG_FILE, JSON_LOG_FILE, ALERT_FILE]:
            if log_file.exists() and log_file.stat().st_mtime < cutoff.timestamp():
                try:
                    log_file.unlink()
                except Exception as e:
                    syslog.syslog(syslog.LOG_ERR, f"Failed to cleanup {log_file}: {e}")

    def run_once(self):
        """Single monitoring run."""
        try:
            # Collect metrics
            metrics = {
                'cpu': self.metrics.get_cpu_metrics(),
                'memory': self.metrics.get_memory_metrics(),
                'disk': self.metrics.get_disk_metrics()
            }

            # Check for and report alerts
            alerts = self.check_thresholds(metrics)
            if alerts:
                self.report_alerts(alerts)

            # Log metrics
            self.log_metrics(metrics)
            self.log_metrics_json(metrics, alerts)

            # Cleanup old logs
            self.cleanup_old_logs()

        except Exception as e:
            error_msg = f"Monitoring run failed: {e}"
            print(error_msg, file=sys.stderr)
            syslog.syslog(syslog.LOG_ERR, error_msg)

def load_config() -> dict:
    """Load configuration from file or return defaults."""
    config = DEFAULT_CONFIG.copy()
    
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                file_config = yaml.safe_load(f)
                if file_config:
                    config.update(file_config)
        except Exception as e:
            syslog.syslog(syslog.LOG_ERR, f"Failed to load config: {e}")

    # Override with environment variables if present
    if webhook_url := os.getenv('ALERT_WEBHOOK_URL'):
        config['webhook_url'] = webhook_url

    return config

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="System Resource Monitor")
    parser.add_argument('--interval', type=int, help="Override monitoring interval in seconds")
    parser.add_argument('--once', action='store_true', help="Run once and exit")
    args = parser.parse_args()

    config = load_config()
    if args.interval:
        config['interval'] = args.interval

    monitor = SystemMonitor(config)
    
    if args.once:
        monitor.run_once()
    else:
        import time
        print(f"System Monitor starting with {config['interval']}s interval...")
        while True:
            monitor.run_once()
            time.sleep(config['interval'])

if __name__ == "__main__":
    main()
