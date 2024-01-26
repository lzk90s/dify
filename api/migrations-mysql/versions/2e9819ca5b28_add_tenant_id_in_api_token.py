"""add_tenant_id_in_api_token

Revision ID: 2e9819ca5b28
Revises: 6e2cfb077b04
Create Date: 2023-09-22 15:41:01.243183

"""
import sqlalchemy as sa
from alembic import op

from core import sqltype
from core.sqltype import UUID

# revision identifiers, used by Alembic.
revision = '2e9819ca5b28'
down_revision = 'ab23c11305d4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('api_tokens', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tenant_id', UUID(), nullable=True,
                                      server_default=sqltype.empty_text(), comment='租户ID'))
        batch_op.create_index('idx_api_token_tenant', ['tenant_id', 'type'], unique=False)
        batch_op.drop_column('dataset_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('api_tokens', schema=None) as batch_op:
        batch_op.add_column(sa.Column('dataset_id', UUID(), autoincrement=False, nullable=True))
        batch_op.drop_index('idx_api_token_tenant')
        batch_op.drop_column('tenant_id')

    # ### end Alembic commands ###
