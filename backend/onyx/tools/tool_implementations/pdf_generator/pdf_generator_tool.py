import json
import uuid
from typing import Any
from typing import cast

from sqlalchemy.orm import Session
from typing_extensions import override

from onyx.chat.emitter import Emitter
from onyx.configs.app_configs import GCS_BUCKET_NAME
from onyx.configs.app_configs import GCS_PROJECT_ID
from onyx.configs.app_configs import GCS_SERVICE_ACCOUNT_JSON
from onyx.configs.app_configs import GCS_SIGNED_URL_EXPIRY_HOURS
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


def _sanitize_text(text: str) -> str:
    """Replace Unicode characters unsupported by Helvetica with ASCII equivalents,
    then strip any remaining non-latin1 characters."""
    replacements = {
        "\u2014": "-",   # em dash
        "\u2013": "-",   # en dash
        "\u2018": "'",   # left single quote
        "\u2019": "'",   # right single quote
        "\u201c": '"',   # left double quote
        "\u201d": '"',   # right double quote
        "\u2026": "...", # ellipsis
        "\u2011": "-",   # non-breaking hyphen
        "\u00ab": "<<",  # left guillemet
        "\u00bb": ">>",  # right guillemet
        "\u0153": "oe",  # oe ligature
        "\u0152": "OE",  # OE ligature
        "\u2194": "<->", # left-right arrow
        "\u2192": "->",  # right arrow
        "\u2190": "<-",  # left arrow
        "\u2022": "-",   # bullet
        "\u25cf": "-",   # black circle
        "\u2023": ">",   # triangular bullet
        "\u00a0": " ",   # non-breaking space
        "\u200b": "",    # zero-width space
        "\u2003": " ",   # em space
        "\u2002": " ",   # en space
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    # Strip any remaining characters outside latin-1 range
    text = text.encode("latin-1", errors="replace").decode("latin-1")
    return text


def _generate_pdf(title: str, content: str) -> bytes:
    """Generate a PDF from title and content using fpdf2."""
    from fpdf import FPDF

    # Sanitize text for Helvetica font compatibility
    title = _sanitize_text(title)
    content = _sanitize_text(content)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(10)

    # Content
    pdf.set_font("Helvetica", "", 12)
    pdf.multi_cell(0, 7, content)

    return bytes(pdf.output())


def _upload_to_gcs(
    pdf_bytes: bytes,
    filename: str,
    bucket_name: str,
    project_id: str | None,
    credentials_json: str | None,
    expiry_hours: int,
) -> str:
    """Upload PDF to Google Cloud Storage and return a signed URL."""
    from google.cloud import storage
    from google.oauth2 import service_account
    import datetime

    if credentials_json:
        info = json.loads(credentials_json)
        credentials = service_account.Credentials.from_service_account_info(info)
        client = storage.Client(project=project_id, credentials=credentials)
    else:
        client = storage.Client(project=project_id)

    bucket = client.bucket(bucket_name)
    blob = bucket.blob(f"pdf-exports/{filename}")
    blob.upload_from_string(pdf_bytes, content_type="application/pdf")

    # Generate a signed URL
    signed_url = blob.generate_signed_url(
        version="v4",
        expiration=datetime.timedelta(hours=expiry_hours),
        method="GET",
    )

    return signed_url


class PDFGeneratorTool(Tool[None]):
    NAME = "generate_pdf"
    DESCRIPTION = (
        "Generate a PDF document from text content and upload it to cloud storage. "
        "Returns a shareable download link. Use this when the user asks to create, "
        "export, or download a PDF document."
    )
    DISPLAY_NAME = "PDF Generator"

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
        """Available if GCS bucket name is configured."""
        return bool(GCS_BUCKET_NAME)

    def tool_definition(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The title of the PDF document.",
                        },
                        "content": {
                            "type": "string",
                            "description": (
                                "The text content to include in the PDF document. "
                                "Can be plain text with line breaks."
                            ),
                        },
                    },
                    "required": ["title", "content"],
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
        title = cast(str, llm_kwargs["title"])
        content = cast(str, llm_kwargs["content"])

        logger.info(f"Generating PDF: '{title}'")

        # Generate the PDF
        pdf_bytes = _generate_pdf(title, content)

        # Create a unique filename
        filename = f"{uuid.uuid4().hex}_{title.replace(' ', '_')[:50]}.pdf"

        # Upload to GCS
        signed_url = _upload_to_gcs(
            pdf_bytes=pdf_bytes,
            filename=filename,
            bucket_name=GCS_BUCKET_NAME or "",
            project_id=GCS_PROJECT_ID,
            credentials_json=GCS_SERVICE_ACCOUNT_JSON,
            expiry_hours=GCS_SIGNED_URL_EXPIRY_HOURS,
        )

        logger.info(f"PDF uploaded successfully: {signed_url}")

        # Emit result to frontend
        self.emitter.emit(
            Packet(
                placement=placement,
                obj=CustomToolDelta(
                    tool_name=self.DISPLAY_NAME,
                    response_type="json",
                    data={
                        "title": title,
                        "download_url": signed_url,
                        "message": f"PDF '{title}' generated and uploaded successfully.",
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
                "title": title,
                "download_url": signed_url,
                "message": f"PDF document '{title}' has been generated and is available for download.",
            }
        )

        return ToolResponse(
            rich_response=CustomToolCallSummary(
                tool_name=self.NAME,
                response_type="json",
                tool_result={
                    "title": title,
                    "download_url": signed_url,
                },
            ),
            llm_facing_response=llm_facing_response,
        )
