import uuid

import sqlalchemy


class UUID(sqlalchemy.types.String):
    def __init__(self, *args, **kwargs):
        super().__init__(length=64)


def gen_uuid():
    return str(uuid.uuid4())
