# [OPS-XXX] Implement DNS Watchdog Email and Slack Notifications

## Description
Configure email notifications for the DNS watchdog monitoring system and set up Slack integration through email-to-Slack forwarding. This will enable immediate operational awareness of DNS resolution issues through standard communication channels.

## Technical Requirements
- Configure the CloudWatch alarm to send notifications to an SNS email topic
- Set up email subscription with proper confirmation
- Configure email format to be compatible with Slack's email integration
- Implement appropriate alarm evaluation parameters:
  - Period: 300 seconds (5 minutes)
  - EvaluationPeriods: 2 (for errors and DNS failures)
  - EvaluationPeriods: 1 (for persistent failures)
  - Appropriate thresholds for each alarm type

## Implementation Details
1. Create an SNS topic for email notifications named "DNS-Watchdog-Email-Alerts"
2. Set up email subscription to the operations team email address
3. Configure Slack's email integration to forward alerts to the #dns-monitoring channel
4. Test the notification workflow to ensure proper formatting in Slack
5. Document the email and Slack notification configuration

## Acceptance Criteria
- [ ] CloudWatch alarms successfully send notifications to the SNS email topic
- [ ] Email subscription is confirmed and receiving test alerts
- [ ] Slack channel receives properly formatted DNS watchdog alerts
- [ ] Different alarm types (errors, DNS failures, persistent failures) are distinguishable in notifications
- [ ] Documentation is updated with email/Slack notification details
- [ ] Recovery steps and troubleshooting information are included in alert messages

## Dependencies
- DNS watchdog script and systemd service implementation
- CloudWatch metric filters configuration

## Estimated Story Points
2


# [OPS-XXX] Implement DNS Watchdog Jira Service Management Integration

## Description
Set up integration between DNS watchdog CloudWatch alarms and Jira Service Management to automatically create and update incident tickets when DNS resolution issues occur. This will provide structured incident management and historical tracking of DNS incidents.

## Technical Requirements
- Set up CloudWatch Events integration in Jira Service Management
- Configure AWS SNS topic with proper HTTPS subscription to the JSM endpoint
- Implement appropriate alarm evaluation parameters:
  - Period: 300 seconds (5 minutes)
  - EvaluationPeriods: 2 (for errors and DNS failures)
  - EvaluationPeriods: 1 (for persistent failures)
  - Appropriate thresholds for each alarm type

## Implementation Details
1. Configure Jira Service Management integration:
   - Go to your team's operations page
   - Select "Integrations" from the left navigation panel, then "Add integration"
   - Search for and select "Amazon CloudWatch Events"
   - Enter "DNS Watchdog Monitoring" as the integration name
   - Select the appropriate assignee team (optional)
   - Click "Continue" to save the integration
   - Expand "Steps to configure the integration" and copy the endpoint URL
   - Turn on the integration

2. Configure AWS resources:
   - Create a dedicated SNS topic named "Jira-Service-Management"
   - Add HTTPS subscription using the JSM endpoint URL
   - Verify the subscription is confirmed
   - Configure CloudWatch alarms to send notifications to this SNS topic
   - Format alarm descriptions to include actionable information

3. Test and document:
   - Test the bidirectional integration (alert creation and resolution)
   - Document the integration configuration and workflow
   - Create runbook for troubleshooting integration issues

## Acceptance Criteria
- [ ] Jira Service Management CloudWatch Events integration is properly configured
- [ ] AWS SNS topic successfully sends notifications to JSM endpoint
- [ ] CloudWatch alarms for DNS watchdog trigger JSM ticket creation
- [ ] Tickets include all relevant information from the DNS watchdog alerts
- [ ] Tickets are assigned to the correct team based on JSM configuration
- [ ] Alarm resolution automatically updates/resolves JSM tickets
- [ ] Documentation includes specific JSM integration steps with screenshots
- [ ] Different alarm types (error, DNS failure, persistent failure) create appropriate tickets

## Dependencies
- DNS watchdog script and systemd service implementation
- CloudWatch metric filters configuration
- Access to Jira Service Management team operations page

## Estimated Story Points
3
