"""add_email_sender_tool

Revision ID: a9c3d7e1f5b2
Revises: b5e7f2a8d3c1
Create Date: 2026-02-07 00:00:01.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a9c3d7e1f5b2"
down_revision = "b5e7f2a8d3c1"
branch_labels = None
depends_on = None


EMAIL_SENDER_TOOL = {
    "name": "EmailSenderTool",
    "display_name": "Email Sender",
    "description": (
        "Send an email to one or more recipients. "
        "Use this when the user asks to send, compose, or deliver an email message."
    ),
    "in_code_tool_id": "EmailSenderTool",
    "enabled": True,
}


def upgrade() -> None:
    conn = op.get_bind()

    # Check if tool already exists
    existing = conn.execute(
        sa.text("SELECT id FROM tool WHERE in_code_tool_id = :in_code_tool_id"),
        {"in_code_tool_id": EMAIL_SENDER_TOOL["in_code_tool_id"]},
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
            EMAIL_SENDER_TOOL,
        )
    else:
        conn.execute(
            sa.text(
                """
                INSERT INTO tool (name, display_name, description, in_code_tool_id, enabled)
                VALUES (:name, :display_name, :description, :in_code_tool_id, :enabled)
                """
            ),
            EMAIL_SENDER_TOOL,
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
        {"in_code_tool_id": "EmailSenderTool"},
    )
