"""add_pdf_generator_tool

Revision ID: b5e7f2a8d3c1
Revises: 03d710ccf29c
Create Date: 2026-02-07 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b5e7f2a8d3c1"
down_revision = "03d710ccf29c"
branch_labels = None
depends_on = None


PDF_GENERATOR_TOOL = {
    "name": "PDFGeneratorTool",
    "display_name": "PDF Generator",
    "description": (
        "Generate a PDF document from text content and upload it to cloud storage. "
        "Returns a shareable download link."
    ),
    "in_code_tool_id": "PDFGeneratorTool",
    "enabled": True,
}


def upgrade() -> None:
    conn = op.get_bind()

    # Check if tool already exists
    existing = conn.execute(
        sa.text("SELECT id FROM tool WHERE in_code_tool_id = :in_code_tool_id"),
        {"in_code_tool_id": PDF_GENERATOR_TOOL["in_code_tool_id"]},
    ).fetchone()

    if existing:
        conn.execute(
            sa.text(
                """
                UPDATE tool
                SET name = :name,
                    display_name = :display_name,
                    description = :description
                WHERE in_code_tool_id = :in_code_tool_id
                """
            ),
            PDF_GENERATOR_TOOL,
        )
    else:
        conn.execute(
            sa.text(
                """
                INSERT INTO tool (name, display_name, description, in_code_tool_id, enabled)
                VALUES (:name, :display_name, :description, :in_code_tool_id, :enabled)
                """
            ),
            PDF_GENERATOR_TOOL,
        )


def downgrade() -> None:
    conn = op.get_bind()

    conn.execute(
        sa.text(
            """
            DELETE FROM tool
            WHERE in_code_tool_id = :in_code_tool_id
            """
        ),
        {"in_code_tool_id": "PDFGeneratorTool"},
    )
