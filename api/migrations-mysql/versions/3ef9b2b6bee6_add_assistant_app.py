"""add_assistant_app

Revision ID: 3ef9b2b6bee6
Revises: 89c7899ca936
Create Date: 2024-01-05 15:26:25.117551

"""
import sqlalchemy as sa
from alembic import op

from core import sqltype
from core.sqltype import UUID, gen_uuid

# revision identifiers, used by Alembic.
revision = '3ef9b2b6bee6'
down_revision = '89c7899ca936'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tool_api_providers',
                    sa.Column('id', UUID, default=gen_uuid, nullable=False, comment='ID'),
                    sa.Column('name', sa.String(length=40), nullable=False, comment='名称'),
                    sa.Column('schema', sa.String(length=4096), nullable=False, comment='schema'),
                    sa.Column('schema_type_str', sa.String(length=40), nullable=False, comment='schema类型'),
                    sa.Column('user_id', UUID, nullable=False, comment='用户ID'),
                    sa.Column('tenant_id', UUID, nullable=False, comment='租户ID'),
                    sa.Column('tools_str', sa.String(length=255), nullable=False, comment='工具'),
                    sa.PrimaryKeyConstraint('id', name='tool_api_provider_pkey')
                    )
    op.create_table('tool_builtin_providers',
                    sa.Column('id', UUID, default=gen_uuid, nullable=False, comment='ID'),
                    sa.Column('tenant_id', UUID, nullable=True, comment='租户ID'),
                    sa.Column('user_id', UUID, nullable=False, comment='用户ID'),
                    sa.Column('provider', sa.String(length=40), nullable=False, comment='提供方'),
                    sa.Column('encrypted_credentials', sa.String(length=2048), nullable=True,
                              server_default=sqltype.empty_text(), comment='验证信息'),
                    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'),
                              nullable=False, comment='创建时间'),
                    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'),
                              nullable=False, comment='更新时间'),
                    sa.PrimaryKeyConstraint('id', name='tool_builtin_provider_pkey'),
                    sa.UniqueConstraint('tenant_id', 'provider', name='unq_builtin_tool_provider')
                    )
    op.create_table('tool_published_apps',
                    sa.Column('id', UUID, default=gen_uuid, nullable=False, comment='ID'),
                    sa.Column('app_id', UUID, nullable=False, comment='应用ID'),
                    sa.Column('user_id', UUID, nullable=False, comment='用户ID'),
                    sa.Column('description', sa.String(length=255), nullable=False, comment='描述'),
                    sa.Column('llm_description', sa.String(length=255), nullable=False, comment='llm描述'),
                    sa.Column('query_description', sa.String(length=255), nullable=False, comment='查询描述'),
                    sa.Column('query_name', sa.String(length=40), nullable=False, comment='查询名'),
                    sa.Column('tool_name', sa.String(length=40), nullable=False, comment='工具名'),
                    sa.Column('author', sa.String(length=40), nullable=False, comment='作者'),
                    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'),
                              nullable=False, comment='创建时间'),
                    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'),
                              nullable=False, comment='更新时间'),
                    sa.ForeignKeyConstraint(['app_id'], ['apps.id'], ),
                    sa.PrimaryKeyConstraint('id', name='published_app_tool_pkey'),
                    sa.UniqueConstraint('app_id', 'user_id', name='unq_published_app_tool')
                    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tool_published_apps')
    op.drop_table('tool_builtin_providers')
    op.drop_table('tool_api_providers')
    # ### end Alembic commands ###
