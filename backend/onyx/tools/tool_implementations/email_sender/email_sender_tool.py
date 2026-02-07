import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any
from typing import cast

from sqlalchemy.orm import Session
from typing_extensions import override

from onyx.chat.emitter import Emitter
from onyx.configs.app_configs import EMAIL_TOOL_FROM_ADDRESS
from onyx.configs.app_configs import EMAIL_TOOL_FROM_NAME
from onyx.configs.app_configs import EMAIL_TOOL_SMTP_PASSWORD
from onyx.configs.app_configs import EMAIL_TOOL_SMTP_PORT
from onyx.configs.app_configs import EMAIL_TOOL_SMTP_SERVER
from onyx.configs.app_configs import EMAIL_TOOL_SMTP_USER
from onyx.server.query_and_chat.placement import Placement
from onyx.server.query_and_chat.streaming_models import CustomToolDelta
from onyx.server.query_and_chat.streaming_models import CustomToolStart
from onyx.server.query_and_chat.streaming_models import Packet
from onyx.server.query_and_chat.streaming_models import SectionEnd
from onyx.tools.interface import Tool
from onyx.tools.models import CustomToolCallSummary
from onyx.tools.models import ToolResponse
from onyx.utils.logger import setup_logger

logger = setup_logger()


def _send_email(
    to: str,
    subject: str,
    body: str,
    smtp_server: str,
    smtp_port: int,
    smtp_user: str,
    smtp_password: str,
    from_address: str,
    from_name: str | None,
    cc: str | None = None,
) -> dict[str, Any]:
    """Send an email via SMTP (compatible with Gmail / Google Workspace SMTP relay)."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    if from_name:
        msg["From"] = f"{from_name} <{from_address}>"
    else:
        msg["From"] = from_address
    msg["To"] = to
    if cc:
        msg["Cc"] = cc

    # Add plain text and HTML versions
    plain_text = body
    html_body = body.replace("\n", "<br>")
    html_content = f"""<html>
<body>
<div style="font-family: Arial, sans-serif; font-size: 14px; color: #333;">
{html_body}
</div>
</body>
</html>"""

    msg.attach(MIMEText(plain_text, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    # Build recipient list
    recipients = [addr.strip() for addr in to.split(",")]
    if cc:
        recipients.extend([addr.strip() for addr in cc.split(",")])

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(smtp_user, smtp_password)
        server.sendmail(from_address, recipients, msg.as_string())

    return {
        "status": "sent",
        "to": to,
        "cc": cc,
        "subject": subject,
    }


class EmailSenderTool(Tool[None]):
    NAME = "send_email"
    DESCRIPTION = (
        "Send an email to one or more recipients. Use this when the user asks to "
        "send, compose, or deliver an email message."
    )
    DISPLAY_NAME = "Email Sender"

    def __init__(
        self,
        tool_id: int,
        emitter: Emitter,
    ) -> None:
        super().__init__(emitter=emitter)
        self._id = tool_id

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self.NAME

    @property
    def description(self) -> str:
        return self.DESCRIPTION

    @property
    def display_name(self) -> str:
        return self.DISPLAY_NAME

    @override
    @classmethod
    def is_available(cls, db_session: Session) -> bool:
        """Available if SMTP credentials are configured."""
        return bool(
            EMAIL_TOOL_SMTP_SERVER
            and EMAIL_TOOL_SMTP_USER
            and EMAIL_TOOL_SMTP_PASSWORD
            and EMAIL_TOOL_FROM_ADDRESS
        )

    def tool_definition(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "to": {
                            "type": "string",
                            "description": (
                                "Recipient email address(es). "
                                "For multiple recipients, separate with commas."
                            ),
                        },
                        "subject": {
                            "type": "string",
                            "description": "The email subject line.",
                        },
                        "body": {
                            "type": "string",
                            "description": (
                                "The email body content. Can include line breaks "
                                "for formatting."
                            ),
                        },
                        "cc": {
                            "type": "string",
                            "description": (
                                "Optional CC recipient email address(es). "
                                "For multiple, separate with commas."
                            ),
                        },
                    },
                    "required": ["to", "subject", "body"],
                },
            },
        }

    def emit_start(self, placement: Placement) -> None:
        self.emitter.emit(
            Packet(
                placement=placement,
                obj=CustomToolStart(tool_name=self.DISPLAY_NAME),
            )
        )

    def run(
        self,
        placement: Placement,
        override_kwargs: None = None,
        **llm_kwargs: Any,
    ) -> ToolResponse:
        to = cast(str, llm_kwargs["to"])
        subject = cast(str, llm_kwargs["subject"])
        body = cast(str, llm_kwargs["body"])
        cc = llm_kwargs.get("cc")

        logger.info(f"Sending email to: {to}, subject: '{subject}'")

        result = _send_email(
            to=to,
            subject=subject,
            body=body,
            smtp_server=EMAIL_TOOL_SMTP_SERVER or "",
            smtp_port=EMAIL_TOOL_SMTP_PORT,
            smtp_user=EMAIL_TOOL_SMTP_USER or "",
            smtp_password=EMAIL_TOOL_SMTP_PASSWORD or "",
            from_address=EMAIL_TOOL_FROM_ADDRESS or "",
            from_name=EMAIL_TOOL_FROM_NAME,
            cc=cc,
        )

        logger.info(f"Email sent successfully to: {to}")

        # Emit result to frontend
        self.emitter.emit(
            Packet(
                placement=placement,
                obj=CustomToolDelta(
                    tool_name=self.DISPLAY_NAME,
                    response_type="json",
                    data={
                        "status": "sent",
                        "to": to,
                        "cc": cc,
                        "subject": subject,
                        "message": f"Email sent successfully to {to}.",
                    },
                ),
            )
        )

        self.emitter.emit(
            Packet(
                placement=placement,
                obj=SectionEnd(),
            )
        )

        llm_facing_response = json.dumps(
            {
                "status": "success",
                "to": to,
                "cc": cc,
                "subject": subject,
                "message": f"Email with subject '{subject}' has been sent to {to}.",
            }
        )

        return ToolResponse(
            rich_response=CustomToolCallSummary(
                tool_name=self.NAME,
                response_type="json",
                tool_result=result,
            ),
            llm_facing_response=llm_facing_response,
        )
