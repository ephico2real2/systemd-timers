# Run once
---

python3 system_monitor.py --once

# Run continuously with default interval (60s)
python3 system_monitor.py

# Run with custom interval
python3 system_monitor.py --interval 30
---


## DNS Watchdog Implementation: Automated DNS Resolution Monitoring

**Type:** Story  
**Priority:** High  
**Points:** 5  
**Components:** Infrastructure, Networking  
**Epic Link:** System Reliability Improvements  

### Description
Implement a DNS watchdog service to monitor and automatically recover from DNS resolution failures on our production servers. The service will provide proactive remediation, reducing downtime caused by temporary DNS issues.

### Acceptance Criteria
- [ ] Create a DNS watchdog bash script that monitors resolution for critical domains
- [ ] Implement a progressive recovery approach (cache flush before network restart)
- [ ] Properly log all actions with CloudWatch-compatible format
- [ ] Create a systemd service to manage the watchdog
- [ ] Test failure recovery in development environment
- [ ] Document the implementation and troubleshooting procedures

### Technical Requirements
- The service must use `resolvectl` for DNS operations
- Primary domain monitoring: `your.subdomain.example.com`
- Check interval: Every 60 seconds
- Recovery steps:
  1. Flush DNS caches
  2. If that fails, restart network service
  3. Verify resolution after each recovery step
- All events must be properly logged for monitoring
- The service must start automatically at boot

### Business Value
DNS resolution issues contribute to approximately 15% of our unplanned downtime incidents. This watchdog service will automatically detect and resolve these issues, reducing the mean time to recovery (MTTR) and improving overall service availability.

### Testing Notes
Include tests for:
- Normal operation
- DNS failure scenarios
- Recovery verification
- Service persistence across system reboots

### Dependencies
- Access to production servers
- Systemd service management permissions
- Network restart privileges

### Documentation Requirements
- System architecture diagram showing the watchdog's role
- Installation and configuration guide
- CloudWatch logging and alerting instructions
- Troubleshooting procedures
