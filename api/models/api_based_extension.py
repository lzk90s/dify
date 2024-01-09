import enum

from sqlalchemy import FetchedValue

from core.sqltype import UUID, gen_uuid
from extensions.ext_database import db


class APIBasedExtensionPoint(enum.Enum):
    APP_EXTERNAL_DATA_TOOL_QUERY = 'app.external_data_tool.query'
    PING = 'ping'
    APP_MODERATION_INPUT = 'app.moderation.input'
    APP_MODERATION_OUTPUT = 'app.moderation.output'


class APIBasedExtension(db.Model):
    __tablename__ = 'api_based_extensions'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='api_based_extension_pkey'),
        db.Index('api_based_extension_tenant_idx', 'tenant_id'),
    )

    id = db.Column(UUID, default=gen_uuid, server_default=FetchedValue())
    tenant_id = db.Column(UUID, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    api_endpoint = db.Column(db.String(255), nullable=False, server_default=FetchedValue())
    api_key = db.Column(db.Text, nullable=False, server_default=FetchedValue())
    created_at = db.Column(db.DateTime, nullable=False, server_default=FetchedValue())
