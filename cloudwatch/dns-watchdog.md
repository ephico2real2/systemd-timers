# Monitor DNS logs for errors

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'CloudWatch Alarms for DNS Watchdog Service with JSM Integration'

Parameters:
  LogGroupName:
    Type: String
    Description: 'Name of the CloudWatch Log Group to monitor'
    Default: 'dns-watchdog-logs'
  EmailEndpoint:
    Type: String
    Description: 'Email address for notifications'
    Default: 'alerts@example.com'
  JSMEndpoint:
    Type: String
    Description: 'Jira Service Management endpoint URL'
    Default: 'https://your-instance.atlassian.net/rest/servicedeskapi/...'
  ErrorThreshold:
    Type: Number
    Description: 'Threshold for DNS Watchdog Errors'
    Default: 1
    MinValue: 1
  ErrorEvaluationPeriods:
    Type: Number
    Description: 'Number of periods over which to evaluate the Error threshold'
    Default: 3
    MinValue: 1
  DNSFailureThreshold:
    Type: Number
    Description: 'Threshold for DNS Resolution Failures'
    Default: 3
    MinValue: 1
  DNSFailureEvaluationPeriods:
    Type: Number
    Description: 'Number of periods over which to evaluate the DNS Failure threshold'
    Default: 3
    MinValue: 1
  PersistentFailureThreshold:
    Type: Number
    Description: 'Threshold for Persistent Failures After Restart'
    Default: 1
    MinValue: 1
  PersistentFailureEvaluationPeriods:
    Type: Number
    Description: 'Number of periods over which to evaluate the Persistent Failure threshold'
    Default: 1
    MinValue: 1

Metadata:
  AWS::CloudFormation::Interface:
    ParameterGroups:
      - Label:
          default: "Monitoring Configuration"
        Parameters:
          - LogGroupName
      - Label:
          default: "Notification Configuration"
        Parameters:
          - EmailEndpoint
          - JSMEndpoint
      - Label:
          default: "Error Alarm Configuration"
        Parameters:
          - ErrorThreshold
          - ErrorEvaluationPeriods
      - Label:
          default: "DNS Failure Alarm Configuration"
        Parameters:
          - DNSFailureThreshold
          - DNSFailureEvaluationPeriods
      - Label:
          default: "Persistent Failure Alarm Configuration"
        Parameters:
          - PersistentFailureThreshold
          - PersistentFailureEvaluationPeriods

Resources:
  DNSWatchdogErrorMetricFilter:
    Type: AWS::Logs::MetricFilter
    Properties:
      LogGroupName: !Ref LogGroupName
      FilterPattern: '"ERROR"'
      MetricTransformations:
        - MetricName: DNSWatchdogErrors
          MetricNamespace: DNSWatchdog
          MetricValue: '1'
          DefaultValue: 0

  DNSWatchdogDNSFailureMetricFilter:
    Type: AWS::Logs::MetricFilter
    Properties:
      LogGroupName: !Ref LogGroupName
      FilterPattern: '"DNS resolution for" "FAILED"'
      MetricTransformations:
        - MetricName: DNSWatchdogDNSFailures
          MetricNamespace: DNSWatchdog
          MetricValue: '1'
          DefaultValue: 0

  DNSWatchdogPersistentFailureMetricFilter:
    Type: AWS::Logs::MetricFilter
    Properties:
      LogGroupName: !Ref LogGroupName
      FilterPattern: '"DNS resolution for" "still FAILED after network restart"'
      MetricTransformations:
        - MetricName: DNSWatchdogPersistentFailures
          MetricNamespace: DNSWatchdog
          MetricValue: '1'
          DefaultValue: 0

  DNSWatchdogEmailTopic:
    Type: AWS::SNS::Topic
    Properties:
      DisplayName: "DNS Watchdog Email Alerts"
      TopicName: "DNS-Watchdog-Email-Alerts"

  DNSWatchdogEmailSubscription:
    Type: AWS::SNS::Subscription
    Properties:
      TopicArn: !Ref DNSWatchdogEmailTopic
      Protocol: "email"
      Endpoint: !Ref EmailEndpoint

  DNSWatchdogJSMTopic:
    Type: AWS::SNS::Topic
    Properties:
      DisplayName: "Jira Service Management"
      TopicName: "Jira-Service-Management"

  DNSWatchdogJSMSubscription:
    Type: AWS::SNS::Subscription
    Properties:
      TopicArn: !Ref DNSWatchdogJSMTopic
      Protocol: "https"
      Endpoint: !Ref JSMEndpoint

  DNSWatchdogErrorAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: "DNS Watchdog - Error Detected"
      AlarmDescription: "Alarm if any error is detected in DNS Watchdog service"
      MetricName: DNSWatchdogErrors
      Namespace: DNSWatchdog
      Statistic: Sum
      Period: 300
      EvaluationPeriods: !Ref ErrorEvaluationPeriods
      Threshold: !Ref ErrorThreshold
      ComparisonOperator: GreaterThanThreshold
      TreatMissingData: notBreaching
      AlarmActions:
        - !Ref DNSWatchdogJSMTopic
        - !Ref DNSWatchdogEmailTopic

  DNSWatchdogDNSFailureAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: "DNS Watchdog - Multiple DNS Failures"
      AlarmDescription: "Alarm if multiple DNS resolution failures are detected in DNS Watchdog service"
      MetricName: DNSWatchdogDNSFailures
      Namespace: DNSWatchdog
      Statistic: Sum
      Period: 300
      EvaluationPeriods: !Ref DNSFailureEvaluationPeriods
      Threshold: !Ref DNSFailureThreshold
      ComparisonOperator: GreaterThanOrEqualToThreshold
      TreatMissingData: notBreaching
      AlarmActions:
        - !Ref DNSWatchdogJSMTopic
        - !Ref DNSWatchdogEmailTopic

  DNSWatchdogPersistentFailureAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: "DNS Watchdog - Persistent Failures After Restart"
      AlarmDescription: "Alarm if DNS resolution continues to fail even after network service restart"
      MetricName: DNSWatchdogPersistentFailures
      Namespace: DNSWatchdog
      Statistic: Sum
      Period: 300
      EvaluationPeriods: !Ref PersistentFailureEvaluationPeriods
      Threshold: !Ref PersistentFailureThreshold
      ComparisonOperator: GreaterThanThreshold
      TreatMissingData: notBreaching
      AlarmActions:
        - !Ref DNSWatchdogJSMTopic
        - !Ref DNSWatchdogEmailTopic

Outputs:
  JiraSNSTopicARN:
    Description: "ARN of the SNS topic for Jira Service Management integration. Use this to send notifications to Jira tickets."
    Value: !Ref DNSWatchdogJSMTopic

  EmailSNSTopicARN:
    Description: "ARN of the SNS topic for email notifications. Use this to send notifications to email addresses."
    Value: !Ref DNSWatchdogEmailTopic

  MonitoredLogGroupName:
    Description: "Name of the CloudWatch Log Group being monitored for DNS watchdog events."
    Value: !Ref LogGroupName
```
