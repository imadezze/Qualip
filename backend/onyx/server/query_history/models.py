from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from onyx.auth.users import get_display_email
from onyx.configs.constants import MessageType
from onyx.configs.constants import QAFeedbackType
from onyx.configs.constants import SessionType
from onyx.db.models import ChatMessage
from onyx.db.models import ChatSession


class AbridgedSearchDoc(BaseModel):
    """A subset of the info present in `SearchDoc`"""

    document_id: str
    semantic_identifier: str
    link: str | None


class MessageSnapshot(BaseModel):
    id: int
    message: str
    message_type: MessageType
    documents: list[AbridgedSearchDoc]
    feedback_type: QAFeedbackType | None
    feedback_text: str | None
    time_created: datetime

    @classmethod
    def build(cls, message: ChatMessage) -> "MessageSnapshot":
        latest_messages_feedback_obj = (
            message.chat_message_feedbacks[-1]
            if len(message.chat_message_feedbacks) > 0
            else None
        )
        feedback_type = (
            (
                QAFeedbackType.LIKE
                if latest_messages_feedback_obj.is_positive
                else QAFeedbackType.DISLIKE
            )
            if latest_messages_feedback_obj
            else None
        )
        feedback_text = (
            latest_messages_feedback_obj.feedback_text
            if latest_messages_feedback_obj
            else None
        )
        return cls(
            id=message.id,
            message=message.message,
            message_type=message.message_type,
            documents=[
                AbridgedSearchDoc(
                    document_id=document.document_id,
                    semantic_identifier=document.semantic_id,
                    link=document.link,
                )
                for document in message.search_docs
            ],
            feedback_type=feedback_type,
            feedback_text=feedback_text,
            time_created=message.time_sent,
        )


class ChatSessionMinimal(BaseModel):
    id: UUID
    user_email: str
    name: str | None
    first_user_message: str
    first_ai_message: str
    assistant_id: int | None
    assistant_name: str | None
    time_created: datetime
    feedback_type: QAFeedbackType | None
    flow_type: SessionType
    conversation_length: int

    @classmethod
    def from_chat_session(cls, chat_session: ChatSession) -> "ChatSessionMinimal":
        first_user_message = next(
            (
                message.message
                for message in chat_session.messages
                if message.message_type == MessageType.USER
            ),
            "",
        )
        first_ai_message = next(
            (
                message.message
                for message in chat_session.messages
                if message.message_type == MessageType.ASSISTANT
            ),
            "",
        )

        list_of_message_feedbacks = [
            feedback.is_positive
            for message in chat_session.messages
            for feedback in message.chat_message_feedbacks
        ]
        session_feedback_type = None
        if list_of_message_feedbacks:
            if all(list_of_message_feedbacks):
                session_feedback_type = QAFeedbackType.LIKE
            elif not any(list_of_message_feedbacks):
                session_feedback_type = QAFeedbackType.DISLIKE
            else:
                session_feedback_type = QAFeedbackType.MIXED

        return cls(
            id=chat_session.id,
            user_email=get_display_email(
                chat_session.user.email if chat_session.user else None
            ),
            name=chat_session.description,
            first_user_message=first_user_message,
            first_ai_message=first_ai_message,
            assistant_id=chat_session.persona_id,
            assistant_name=(
                chat_session.persona.name if chat_session.persona else None
            ),
            time_created=chat_session.time_created,
            feedback_type=session_feedback_type,
            flow_type=(
                SessionType.SLACK if chat_session.onyxbot_flow else SessionType.CHAT
            ),
            conversation_length=len(
                [
                    message
                    for message in chat_session.messages
                    if message.message_type != MessageType.SYSTEM
                ]
            ),
        )


class ChatSessionSnapshot(BaseModel):
    id: UUID
    user_email: str
    name: str | None
    messages: list[MessageSnapshot]
    assistant_id: int | None
    assistant_name: str | None
    time_created: datetime
    flow_type: SessionType
