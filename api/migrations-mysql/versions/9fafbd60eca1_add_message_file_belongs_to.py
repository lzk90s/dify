"""add message file belongs to

Revision ID: 9fafbd60eca1
Revises: 4823da1d26cf
Create Date: 2024-01-15 13:07:20.340896

"""
import sqlalchemy as sa
from alembic import op

from core import sqltype

# revision identifiers, used by Alembic.
revision = '9fafbd60eca1'
down_revision = '4823da1d26cf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('message_files', schema=None) as batch_op:
        batch_op.add_column(sa.Column('belongs_to', sa.String(length=255), nullable=True,
                                      server_default=sqltype.empty_text(), comment='属于'))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('message_files', schema=None) as batch_op:
        batch_op.drop_column('belongs_to')

    # ### end Alembic commands ###
