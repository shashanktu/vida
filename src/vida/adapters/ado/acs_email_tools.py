"""
Azure Communication Services (ACS) email tool.

Install:
    pip install azure-communication-email azure-identity pydantic

Environment variables:
    ACS_ENDPOINT            https://<resource>.communication.azure.com  (required)
    ACS_SENDER_ADDRESS      e.g. DoNotReply@xxxxxxxx.azurecomm.net      (required)

Authentication uses the shared get_credential() helper (Managed Identity when
hosted, DefaultAzureCredential otherwise), same as the Foundry client.
"""
import logging
import os
import re
from typing import Annotated, Optional

from azure.communication.email import EmailClient
from azure.core.exceptions import HttpResponseError
from pydantic import Field

# Adjust these imports to match your project
from agent_framework import tool
from vida.utils.clientConnection import get_credential  # the module where your get_credential() lives

from vida.utils.config import Azure_communication_service_config as acsc

logger = logging.getLogger(__name__)

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_SEND_TIMEOUT_SECONDS = 60


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
_client: Optional[EmailClient] = None


def _get_client() -> EmailClient:
    """Create (once) and return an EmailClient authenticated via get_credential()."""
    global _client
    if _client is None:
        endpoint = acsc.ACS_ENDPOINT or os.getenv("ACS_ENDPOINT")
        if not endpoint:
            raise ValueError("ACS_ENDPOINT environment variable is not set.")
        _client = EmailClient(endpoint, get_credential())
    return _client


def _clean_addresses(addresses: Optional[list[str]], field_name: str) -> list[dict]:
    """Validate addresses and convert to the ACS recipient format."""
    result = []
    for addr in addresses or []:
        addr = addr.strip()
        if not _EMAIL_RE.match(addr):
            raise ValueError(f"Invalid email address in '{field_name}': '{addr}'")
        result.append({"address": addr})
    return result


def acs_send_email(
    to: list[str],
    subject: str,
    body: str,
    is_html: bool = False,
    cc: Optional[list[str]] = None,
    bcc: Optional[list[str]] = None,
    reply_to: Optional[list[str]] = None,
) -> dict:
    
    sender = acsc.ACS_SENDER_ADDRESS or os.getenv("ACS_SENDER_ADDRESS")
    if not sender:
        raise ValueError("ACS_SENDER_ADDRESS environment variable is not set.")

    to_list = _clean_addresses(to, "to")
    if not to_list:
        raise ValueError("At least one recipient is required in 'to'.")

    recipients = {"to": to_list}
    cc_list = _clean_addresses(cc, "cc")
    bcc_list = _clean_addresses(bcc, "bcc")
    if cc_list:
        recipients["cc"] = cc_list
    if bcc_list:
        recipients["bcc"] = bcc_list

    message = {
        "senderAddress": sender,
        "recipients": recipients,
        "content": {
            "subject": subject,
            # ACS requires plainText or html (or both)
            "html" if is_html else "plainText": body,
        },
    }
    reply_to_list = _clean_addresses(reply_to, "reply_to")
    if reply_to_list:
        message["replyTo"] = reply_to_list

    client = _get_client()
    try:
        poller = client.begin_send(message)
        result = poller.result(timeout=_SEND_TIMEOUT_SECONDS)
    except HttpResponseError as e:
        raise RuntimeError(f"ACS rejected the email: {e.message}") from e

    return {
        "message_id": result.get("id"),
        "status": result.get("status"),  # "Succeeded" means ACS accepted + queued it
        "to": [r["address"] for r in to_list],
        "subject": subject,
    }


# --------------------------------------------------------------------------- #
# Tool
# --------------------------------------------------------------------------- #
@tool(
    name="acs_send_email",
    description="Send an email using Azure Communication Services.",
    approval_mode="never_require",
)
def send_email(
    to: Annotated[list[str], Field(description="List of recipient email addresses.")],
    subject: Annotated[str, Field(description="Subject line of the email.")],
    body: Annotated[str, Field(description="Body of the email. Plain text by default, or HTML if is_html is true.")],
    is_html: Annotated[bool, Field(description="Set to true if the body is HTML.")] = False,
    cc: Annotated[Optional[list[str]], Field(description="Optional list of CC email addresses.")] = None,
    bcc: Annotated[Optional[list[str]], Field(description="Optional list of BCC email addresses.")] = None,
    reply_to: Annotated[Optional[list[str]], Field(description="Optional list of reply-to email addresses.")] = None,
) -> dict:
    logger.info(f"[acs_tools] [send_email] Tool called. to={to}, subject='{subject}', is_html={is_html}")
    try:
        return acs_send_email(
            to=to, subject=subject, body=body, is_html=is_html, cc=cc, bcc=bcc, reply_to=reply_to
        )
    except Exception as e:
        logger.error(
            f"[acs_tools] [send_email] Tool failed. to={to}, subject='{subject}'. Error: {e}",
            exc_info=True,
        )
        raise


if __name__ == "__main__":
    # Quick manual test: python acs_email_tools.py you@example.com
    import sys

    logging.basicConfig(level=logging.INFO)
    print(acs_send_email(to=[sys.argv[1]], subject="ACS test", body="Hello from Azure Communication Services!"))
