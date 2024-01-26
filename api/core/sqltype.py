import uuid
from uuid import UUID as _python_UUID

import sqlalchemy

from extensions.ext_database import is_postgresql


class UUID(sqlalchemy.types.Uuid):
    def __init__(self):
        super().__init__()
        self.as_uuid = True if is_postgresql() else False

    def bind_processor(self, dialect):
        character_based_uuid = (
                not dialect.supports_native_uuid or not self.native_uuid
        )

        if character_based_uuid:
            if self.as_uuid:
                def process(value):
                    if value:
                        value = value.hex
                    return value

                return process
            else:
                def process(value):
                    if value:
                        value = value.replace("-", "")
                    return value

                return process
        else:
            return None

    def result_processor(self, dialect, coltype):
        character_based_uuid = (
                not dialect.supports_native_uuid or not self.native_uuid
        )

        if character_based_uuid:
            if self.as_uuid:
                def process(value):
                    if value:
                        value = _python_UUID(value)
                    return value

                return process
            else:
                def process(value):
                    if value:
                        value = str(_python_UUID(value))
                    return value

                return process
        else:
            if not self.as_uuid:
                def process(value):
                    if value:
                        value = str(value)
                    return value

                return process
            else:
                return None


def gen_uuid():
    as_uuid: bool = True if is_postgresql() else False
    if as_uuid:
        return uuid.uuid4()
    else:
        return str(uuid.uuid4())


def invalid_uuid():
    as_uuid: bool = True if is_postgresql() else False
    if as_uuid:
        return None
    else:
        return ''


def invalid_time():
    as_uuid: bool = True if is_postgresql() else False
    if as_uuid:
        return None
    else:
        return sqlalchemy.text("'1970-01-01 00:00:00'")


# def empty_uuid():
#     return sqlalchemy.text("''")


def empty_text():
    return sqlalchemy.text("''")
