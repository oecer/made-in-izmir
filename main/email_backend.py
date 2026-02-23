"""
Custom Django email backend using Microsoft Graph API + OAuth2 (Modern Auth).

Instead of SMTP Basic Auth (which Microsoft is disabling), this backend:
  1. Acquires an OAuth2 token from Azure AD using client credentials.
  2. Sends emails via POST /v1.0/users/{sender}/sendMail on the Graph API.

Required settings (loaded from environment):
  AZURE_CLIENT_ID      – App Registration Application (client) ID
  AZURE_CLIENT_SECRET  – App Registration client secret
  AZURE_TENANT_ID      – Your Azure AD / Entra ID tenant ID
  EMAIL_HOST_USER      – The mailbox to send FROM (e.g. info@madeinizmir.com)
  DEFAULT_FROM_EMAIL   – Display "From" address (can be an alias/noreply)

Required Azure App Registration permissions (Application, not Delegated):
  Mail.Send
"""

import json
import logging
import msal
import requests

from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings

logger = logging.getLogger(__name__)


class MicrosoftGraphEmailBackend(BaseEmailBackend):
    """Send emails via Microsoft Graph API using OAuth2 client credentials."""

    GRAPH_SEND_URL = "https://graph.microsoft.com/v1.0/users/{sender}/sendMail"
    SCOPES = ["https://graph.microsoft.com/.default"]

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.client_id = settings.AZURE_CLIENT_ID
        self.client_secret = settings.AZURE_CLIENT_SECRET
        self.tenant_id = settings.AZURE_TENANT_ID
        self.sender = settings.EMAIL_HOST_USER  # The licensed mailbox used to send

    def _get_access_token(self):
        """Acquire an OAuth2 access token using client credentials flow."""
        authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=authority,
            client_credential=self.client_secret,
        )
        result = app.acquire_token_for_client(scopes=self.SCOPES)

        if "access_token" not in result:
            error = result.get("error_description", result.get("error", "Unknown error"))
            raise RuntimeError(f"Failed to acquire Microsoft access token: {error}")

        return result["access_token"]

    def _build_message(self, email_message):
        """Convert a Django EmailMessage into the Graph API JSON format."""
        to_recipients = [
            {"emailAddress": {"address": addr}} for addr in email_message.to
        ]
        cc_recipients = [
            {"emailAddress": {"address": addr}} for addr in (email_message.cc or [])
        ]
        bcc_recipients = [
            {"emailAddress": {"address": addr}} for addr in (email_message.bcc or [])
        ]

        # Determine content type (HTML or plain text)
        content_type = "HTML"
        body_content = email_message.body

        # Handle EmailMultiAlternatives (emails with HTML alternative)
        if hasattr(email_message, "alternatives"):
            for content, mimetype in email_message.alternatives:
                if mimetype == "text/html":
                    body_content = content
                    content_type = "HTML"
                    break

        message = {
            "message": {
                "subject": email_message.subject,
                "body": {
                    "contentType": content_type,
                    "content": body_content,
                },
                "toRecipients": to_recipients,
                "from": {
                    "emailAddress": {
                        "address": email_message.from_email or self.sender
                    }
                },
            },
            "saveToSentItems": "false",
        }

        if cc_recipients:
            message["message"]["ccRecipients"] = cc_recipients
        if bcc_recipients:
            message["message"]["bccRecipients"] = bcc_recipients

        return message

    def send_messages(self, email_messages):
        """Send a list of EmailMessage objects. Returns the number sent successfully."""
        if not email_messages:
            return 0

        try:
            token = self._get_access_token()
        except Exception as exc:
            if not self.fail_silently:
                raise
            logger.exception("Microsoft Graph: failed to acquire token: %s", exc)
            return 0

        sent_count = 0
        url = self.GRAPH_SEND_URL.format(sender=self.sender)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        for email_message in email_messages:
            try:
                payload = self._build_message(email_message)
                response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)

                if response.status_code == 202:
                    sent_count += 1
                    logger.debug("Graph API: email sent to %s", email_message.to)
                else:
                    logger.error(
                        "Graph API: failed to send email to %s — %s %s",
                        email_message.to,
                        response.status_code,
                        response.text,
                    )
                    if not self.fail_silently:
                        response.raise_for_status()

            except Exception as exc:
                logger.exception("Graph API: error sending email to %s: %s", email_message.to, exc)
                if not self.fail_silently:
                    raise

        return sent_count
