"""The chat summary definition and schema for the database."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import UUID, Column, DateTime, String, UniqueConstraint

from src.models.literals_types_constants import DatabasePrefixes
from src.sql_alchemy_conf import Base


class ChatSummary(Base):
    __tablename__: DatabasePrefixes = "chat_summary"
    __table_args__ = (
        UniqueConstraint(
            "session_id", "conversation_id", name="_session_conversation_uc"
        ),
    )

    conversation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    summary_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    author_name = Column(String)
    author_role = Column(String)
    content = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    event_type = Column(String)
