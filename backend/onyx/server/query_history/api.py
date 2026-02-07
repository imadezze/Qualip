from datetime import datetime
from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from sqlalchemy.orm import Session

from onyx.auth.users import current_admin_user
from onyx.auth.users import get_display_email
from onyx.chat.chat_utils import create_chat_history_chain
from onyx.configs.constants import MessageType
from onyx.configs.constants import QAFeedbackType
from onyx.configs.constants import SessionType
from onyx.db.chat import get_chat_session_by_id
from onyx.db.engine.sql_engine import get_session
from onyx.db.enums import ChatSessionSharedStatus
from onyx.db.models import ChatSession
from onyx.db.models import User
from onyx.db.query_history import get_page_of_chat_sessions
from onyx.db.query_history import get_total_filtered_chat_sessions_count
from onyx.server.documents.models import PaginatedReturn
from onyx.server.query_history.models import ChatSessionMinimal
from onyx.server.query_history.models import ChatSessionSnapshot
from onyx.server.query_history.models import MessageSnapshot

router = APIRouter(prefix="/admin")


def snapshot_from_chat_session(
    chat_session: ChatSession,
    db_session: Session,
) -> ChatSessionSnapshot | None:
    try:
        # Older chats may not have the right structure
        messages = create_chat_history_chain(
            chat_session_id=chat_session.id, db_session=db_session
        )
    except RuntimeError:
        return None

    flow_type = SessionType.SLACK if chat_session.onyxbot_flow else SessionType.CHAT

    return ChatSessionSnapshot(
        id=chat_session.id,
        user_email=get_display_email(
            chat_session.user.email if chat_session.user else None
        ),
        name=chat_session.description,
        messages=[
            MessageSnapshot.build(message)
            for message in messages
            if message.message_type != MessageType.SYSTEM
        ],
        assistant_id=chat_session.persona_id,
        assistant_name=chat_session.persona.name if chat_session.persona else None,
        time_created=chat_session.time_created,
        flow_type=flow_type,
    )


@router.get("/chat-session-history")
def get_chat_session_history(
    page_num: int = Query(0, ge=0),
    page_size: int = Query(10, ge=1),
    feedback_type: QAFeedbackType | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    _: User | None = Depends(current_admin_user),
    db_session: Session = Depends(get_session),
) -> PaginatedReturn[ChatSessionMinimal]:
    page_of_chat_sessions = get_page_of_chat_sessions(
        page_num=page_num,
        page_size=page_size,
        db_session=db_session,
        start_time=start_time,
        end_time=end_time,
        feedback_filter=feedback_type,
    )

    total_filtered_chat_sessions_count = get_total_filtered_chat_sessions_count(
        db_session=db_session,
        start_time=start_time,
        end_time=end_time,
        feedback_filter=feedback_type,
    )

    minimal_chat_sessions: list[ChatSessionMinimal] = []

    for chat_session in page_of_chat_sessions:
        minimal_chat_session = ChatSessionMinimal.from_chat_session(chat_session)
        minimal_chat_sessions.append(minimal_chat_session)

    return PaginatedReturn(
        items=minimal_chat_sessions,
        total_items=total_filtered_chat_sessions_count,
    )


@router.get("/chat-session-history/{chat_session_id}")
def get_chat_session_admin(
    chat_session_id: UUID,
    _: User | None = Depends(current_admin_user),
    db_session: Session = Depends(get_session),
) -> ChatSessionSnapshot:
    try:
        chat_session = get_chat_session_by_id(
            chat_session_id=chat_session_id,
            user_id=None,  # view chat regardless of user
            db_session=db_session,
            include_deleted=True,
        )
    except ValueError:
        raise HTTPException(
            HTTPStatus.BAD_REQUEST,
            f"Chat session with id '{chat_session_id}' does not exist.",
        )
    snapshot = snapshot_from_chat_session(
        chat_session=chat_session, db_session=db_session
    )

    if snapshot is None:
        raise HTTPException(
            HTTPStatus.BAD_REQUEST,
            f"Could not create snapshot for chat session with id '{chat_session_id}'",
        )

    return snapshot


@router.post("/chat-session-history/{chat_session_id}/share")
def share_chat_session_admin(
    chat_session_id: UUID,
    _: User | None = Depends(current_admin_user),
    db_session: Session = Depends(get_session),
) -> dict[str, str]:
    """Admin endpoint to share a chat session (set shared_status to PUBLIC)."""
    try:
        chat_session = get_chat_session_by_id(
            chat_session_id=chat_session_id,
            user_id=None,  # admin can share any chat
            db_session=db_session,
            include_deleted=False,
        )
    except ValueError:
        raise HTTPException(
            HTTPStatus.BAD_REQUEST,
            f"Chat session with id '{chat_session_id}' does not exist.",
        )

    chat_session.shared_status = ChatSessionSharedStatus.PUBLIC
    db_session.commit()

    return {"status": "success", "shared_status": "public"}
