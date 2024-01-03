import uuid

import sqlalchemy

from extensions.ext_database import is_postgresql


class UUID(sqlalchemy.types.Uuid):
    def __init__(self):
        super().__init__()
        self.as_uuid = True if is_postgresql() else False


def gen_uuid():
    as_uuid: bool = True if is_postgresql() else False
    if as_uuid:
        return uuid.uuid4()
    else:
        return str(uuid.uuid4())
