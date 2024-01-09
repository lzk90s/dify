from sqlalchemy import FetchedValue
from sqlalchemy.sql.sqltypes import JSON

from core.sqltype import UUID, gen_uuid
from extensions.ext_database import db


class DataSourceBinding(db.Model):
    __tablename__ = 'data_source_bindings'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='source_binding_pkey'),
        db.Index('source_binding_tenant_id_idx', 'tenant_id'),
        db.Index('source_info_idx', "source_info", postgresql_using='gin')
    )

    id = db.Column(UUID, default=gen_uuid, server_default=FetchedValue())
    tenant_id = db.Column(UUID, nullable=False)
    access_token = db.Column(db.String(255), nullable=False)
    provider = db.Column(db.String(255), nullable=False)
    source_info = db.Column(JSON, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=FetchedValue())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=FetchedValue())
    disabled = db.Column(db.Boolean, nullable=True, server_default=FetchedValue())
