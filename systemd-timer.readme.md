### **✅  Systemd Service & Timer Files with `journal+console`, `StartLimitIntervalSec=0`, and `RestartSec=1`**
These **service and timer files** should be placed inside the **`systemd-timer`** folder in your **GitHub repository**.  

---

### **📌 `systemd-timer/zendesk-it-glue.service`**
```sh
cat <<EOF > systemd-timer/zendesk-it-glue.service
[Unit]
Description=Zendesk IT Glue Integration
After=network.target

[Service]
ExecStart=/usr/bin/python3 /usr/local/dotmobi-tools/scripts/zendesk_it_glue_integration.py
WorkingDirectory=/usr/local/dotmobi-tools/scripts
User=root
Restart=always
RestartSec=1
StartLimitIntervalSec=0
StandardOutput=journal+console
StandardError=journal+console
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
EOF
```

---

### **📌 `systemd-timer/zendesk-it-glue.timer`**
```sh
cat <<EOF > systemd-timer/zendesk-it-glue.timer
[Unit]
Description=Runs Zendesk IT Glue Integration at 15 minutes past every hour

[Timer]
OnCalendar=*-*-* *:15:00
Persistent=true

[Install]
WantedBy=timers.target
EOF
```

---

### **📌 `systemd-timer/it-glue-backup.service`**
```sh
cat <<EOF > systemd-timer/it-glue-backup.service
[Unit]
Description=IT Glue Export Backup
After=network.target

[Service]
ExecStart=/usr/bin/python3 /usr/local/dotmobi-tools/scripts/it_glue_export_backup.py
WorkingDirectory=/usr/local/dotmobi-tools/scripts
User=root
Restart=always
RestartSec=1
StartLimitIntervalSec=0
StandardOutput=journal+console
StandardError=journal+console
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
EOF
```

---

### **📌 `systemd-timer/it-glue-backup.timer`**
```sh
cat <<EOF > systemd-timer/it-glue-backup.timer
[Unit]
Description=Runs IT Glue Export Backup Every Monday at 08:00 AM

[Timer]
OnCalendar=Mon *-*-* 08:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF
```

---

### **📌 `systemd-timer/jamf-pro-notifications.service`**
```sh
cat <<EOF > systemd-timer/jamf-pro-notifications.service
[Unit]
Description=Jamf Pro Get Notifications
After=network.target

[Service]
ExecStart=/usr/bin/python3 /usr/local/dotmobi-tools/scripts/jamf_pro_get_notifications.py
WorkingDirectory=/usr/local/dotmobi-tools/scripts
User=root
Restart=always
RestartSec=1
StartLimitIntervalSec=0
StandardOutput=journal+console
StandardError=journal+console
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
EOF
```

---

### **📌 `systemd-timer/jamf-pro-notifications.timer`**
```sh
cat <<EOF > systemd-timer/jamf-pro-notifications.timer
[Unit]
Description=Runs Jamf Pro Get Notifications at 30 minutes past every hour

[Timer]
OnCalendar=*-*-* *:30:00
Persistent=true

[Install]
WantedBy=timers.target
EOF
```

---

### **📌 `systemd-timer/zendesk-statusio.service`**
```sh
cat <<EOF > systemd-timer/zendesk-statusio.service
[Unit]
Description=Zendesk Statusio Integration
After=network.target

[Service]
ExecStart=/usr/bin/python3 /usr/local/dotmobi-tools/scripts/zendesk_statusio_integration.py
WorkingDirectory=/usr/local/dotmobi-tools/scripts
User=root
Restart=always
RestartSec=1
StartLimitIntervalSec=0
StandardOutput=journal+console
StandardError=journal+console
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
EOF
```

---

### **📌 `systemd-timer/zendesk-statusio.timer`**
```sh
cat <<EOF > systemd-timer/zendesk-statusio.timer
[Unit]
Description=Runs Zendesk Statusio Integration Hourly

[Timer]
OnCalendar=hourly
Persistent=true

[Install]
WantedBy=timers.target
EOF
```

---

## **📌 How to Commit These Files to Git**
Run the following **Git commands** in your **Git repository root** to commit and push them:

```sh
git add systemd-timer/*.service systemd-timer/*.timer
git commit -m "Updated systemd services with RestartSec=1, StartLimitIntervalSec=0, and journal+console output"
git push origin main
```

This ensures **GitHub Actions will pick up these files and deploy them to the remote host**.

---

## **📌 Why These Changes Matter?**
| **Setting** | **Purpose** |
|------------|------------|
| `RestartSec=1` | If the service fails, systemd waits **1 second** before restarting it. |
| `StartLimitIntervalSec=0` | Ensures systemd does **not limit how often the service restarts**. Prevents rate limiting. |
| `StandardOutput=journal+console` | Logs output **to both journal logs and the system console**. |
| `StandardError=journal+console` | Logs **errors to both journal logs and the system console**. |

---

## **🚀 What’s Next?**
### **1️⃣ Verify That GitHub Actions Correctly Deploys These Files**
After pushing the changes, confirm the **workflow copies them to `/etc/systemd/system/` on the remote host**.

### **2️⃣ Manually Test Timers on EC2**
Run the following commands to **test timers manually**:
```sh
sudo systemctl start zendesk-it-glue.timer
sudo systemctl list-timers --all
```

### **3️⃣ Monitor Logs for Debugging**
Use the following commands to **check logs**:
```sh
sudo journalctl -u zendesk-it-glue --no-pager -n 50
```
```sh
sudo journalctl -u jamf-pro-notifications --no-pager -n 50
```
