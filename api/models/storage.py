from sqlalchemy import FetchedValue

from core.sqltype import UUID, gen_uuid
from extensions.ext_database import db


class FileStorage(db.Model):
    __tablename__ = 'file_storages'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='source_binding_pkey'),
        db.Index('file_key_tenant_id_idx', 'tenant_id', 'key'),
    )

    id = db.Column(UUID, default=gen_uuid, server_default=FetchedValue())
    type = db.String(db.String(32), nullable=False)
    key = db.Column(db.String(256), nullable=False)
    target_key = db.Column(db.String(256), nullable=False)
