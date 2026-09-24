from __future__ import annotations

import json
import os
import smtplib
from email.message import EmailMessage
from typing import Dict, Optional

import requests


class AlertRouter:
    """Email and Slack alert router for incident notifications."""

    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.smtp_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
        self.default_recipient = os.getenv("ALERT_EMAIL_TO", "ops@example.com")
        self.slack_webhook = os.getenv("SLACK_WEBHOOK_URL")

    def send_alert(self, incident_id: str, title: str, message: str, recipient: Optional[str] = None) -> Dict[str, str]:
        response: Dict[str, str] = {
            "status": "simulated",
            "message": f"Alert queued for {incident_id}: {title} - {message}",
            "recipient": recipient or self.default_recipient,
        }

        if self.slack_webhook:
            try:
                payload = {"text": f"*{title}*\nIncident: {incident_id}\n{message}"}
                requests.post(self.slack_webhook, data=json.dumps(payload), timeout=10)
                response["slack_status"] = "sent"
            except Exception as exc:  # pragma: no cover - runtime networking
                response["slack_status"] = f"failed: {exc}"

        if self.smtp_host and self.smtp_user and self.smtp_password:
            msg = EmailMessage()
            msg["Subject"] = f"Incident Alert: {incident_id}"
            msg["From"] = self.smtp_user
            msg["To"] = recipient or self.default_recipient
            msg.set_content(f"{title}\n\n{message}")

            try:
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    if self.smtp_tls:
                        server.starttls()
                    if self.smtp_user and self.smtp_password:
                        server.login(self.smtp_user, self.smtp_password)
                    server.send_message(msg)
                response["status"] = "sent"
                response["message"] = "Email alert sent successfully"
                response["recipient"] = msg["To"]
            except Exception as exc:  # pragma: no cover - runtime env dependency
                response["status"] = "failed"
                response["message"] = str(exc)
                response["recipient"] = msg["To"]

        return response
