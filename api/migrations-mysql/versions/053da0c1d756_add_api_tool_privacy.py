"""add api tool privacy

Revision ID: 053da0c1d756
Revises: 4829e54d2fee
Create Date: 2024-01-12 06:47:21.656262

"""
import sqlalchemy as sa
from alembic import op

from core import sqltype
from core.sqltype import UUID, gen_uuid

# revision identifiers, used by Alembic.
revision = '053da0c1d756'
down_revision = '4829e54d2fee'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tool_conversation_variables',
                    sa.Column('id', UUID, default=gen_uuid, nullable=False, comment='ID'),
                    sa.Column('user_id', UUID, nullable=False, comment='用户ID'),
                    sa.Column('tenant_id', UUID, nullable=False, comment='租户ID'),
                    sa.Column('conversation_id', UUID, nullable=False, comment='会话ID'),
                    sa.Column('variables_str', sa.String(length=2048), nullable=False, comment='变量'),
                    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'),
                              nullable=False, comment='创建时间'),
                    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'),
                              nullable=False, comment='更新时间'),
                    sa.PrimaryKeyConstraint('id', name='tool_conversation_variables_pkey')
                    )
    with op.batch_alter_table('tool_api_providers', schema=None) as batch_op:
        batch_op.add_column(sa.Column('privacy_policy', sa.String(length=255), nullable=True,
                                      server_default=sqltype.empty_text(), comment='隐私策略'))
        batch_op.alter_column('icon',
                              existing_type=sa.VARCHAR(length=256),
                              type_=sa.String(length=255),
                              existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tool_api_providers', schema=None) as batch_op:
        batch_op.alter_column('icon',
                              existing_type=sa.String(length=255),
                              type_=sa.VARCHAR(length=256),
                              existing_nullable=False)
        batch_op.drop_column('privacy_policy')

    op.drop_table('tool_conversation_variables')
    # ### end Alembic commands ###