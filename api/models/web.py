from sqlalchemy import FetchedValue

from core.sqltype import UUID, gen_uuid
from extensions.ext_database import db
from models.model import Message


class SavedMessage(db.Model):
    __tablename__ = 'saved_messages'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='saved_message_pkey'),
        db.Index('saved_message_message_idx', 'app_id', 'message_id', 'created_by_role', 'created_by'),
    )

    id = db.Column(UUID, default=gen_uuid, server_default=FetchedValue())
    app_id = db.Column(UUID, nullable=False)
    message_id = db.Column(UUID, nullable=False)
    created_by_role = db.Column(db.String(255), nullable=False, server_default=FetchedValue())
    created_by = db.Column(UUID, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=FetchedValue())

    @property
    def message(self):
        return db.session.query(Message).filter(Message.id == self.message_id).first()


class PinnedConversation(db.Model):
    __tablename__ = 'pinned_conversations'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='pinned_conversation_pkey'),
        db.Index('pinned_conversation_conversation_idx', 'app_id', 'conversation_id', 'created_by_role', 'created_by'),
    )

    id = db.Column(UUID, default=gen_uuid, server_default=FetchedValue())
    app_id = db.Column(UUID, nullable=False)
    conversation_id = db.Column(UUID, nullable=False)
    created_by_role = db.Column(db.String(255), nullable=False, server_default=FetchedValue())
    created_by = db.Column(UUID, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=FetchedValue())
