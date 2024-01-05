"""add provider model support

Revision ID: 16fa53d9faec
Revises: 8d2d099ceb74
Create Date: 2023-08-06 16:57:51.248337

"""
import sqlalchemy as sa
from alembic import op

from core.sqltype import UUID

# revision identifiers, used by Alembic.
revision = '16fa53d9faec'
down_revision = '8d2d099ceb74'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('provider_models',
                    sa.Column('id', UUID(), nullable=False),
                    sa.Column('tenant_id', UUID(), nullable=False),
                    sa.Column('provider_name', sa.String(length=40), nullable=False),
                    sa.Column('model_name', sa.String(length=40), nullable=False),
                    sa.Column('model_type', sa.String(length=40), nullable=False),
                    sa.Column('encrypted_config', sa.Text(), nullable=True),
                    sa.Column('is_valid', sa.Boolean(), server_default=sa.text('false'), nullable=False),
                    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'),
                              nullable=False),
                    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'),
                              nullable=False),
                    sa.PrimaryKeyConstraint('id', name='provider_model_pkey'),
                    sa.UniqueConstraint('tenant_id', 'provider_name', 'model_name', 'model_type',
                                        name='unique_provider_model_name')
                    )
    with op.batch_alter_table('provider_models', schema=None) as batch_op:
        batch_op.create_index('provider_model_tenant_id_provider_idx', ['tenant_id', 'provider_name'], unique=False)

    op.create_table('tenant_default_models',
                    sa.Column('id', UUID(), nullable=False),
                    sa.Column('tenant_id', UUID(), nullable=False),
                    sa.Column('provider_name', sa.String(length=40), nullable=False),
                    sa.Column('model_name', sa.String(length=40), nullable=False),
                    sa.Column('model_type', sa.String(length=40), nullable=False),
                    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'),
                              nullable=False),
                    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'),
                              nullable=False),
                    sa.PrimaryKeyConstraint('id', name='tenant_default_model_pkey')
                    )
    with op.batch_alter_table('tenant_default_models', schema=None) as batch_op:
        batch_op.create_index('tenant_default_model_tenant_id_provider_type_idx',
                              ['tenant_id', 'provider_name', 'model_type'], unique=False)

    op.create_table('tenant_preferred_model_providers',
                    sa.Column('id', UUID(), nullable=False),
                    sa.Column('tenant_id', UUID(), nullable=False),
                    sa.Column('provider_name', sa.String(length=40), nullable=False),
                    sa.Column('preferred_provider_type', sa.String(length=40), nullable=False),
                    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'),
                              nullable=False),
                    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'),
                              nullable=False),
                    sa.PrimaryKeyConstraint('id', name='tenant_preferred_model_provider_pkey')
                    )
    with op.batch_alter_table('tenant_preferred_model_providers', schema=None) as batch_op:
        batch_op.create_index('tenant_preferred_model_provider_tenant_provider_idx', ['tenant_id', 'provider_name'],
                              unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tenant_preferred_model_providers', schema=None) as batch_op:
        batch_op.drop_index('tenant_preferred_model_provider_tenant_provider_idx')

    op.drop_table('tenant_preferred_model_providers')
    with op.batch_alter_table('tenant_default_models', schema=None) as batch_op:
        batch_op.drop_index('tenant_default_model_tenant_id_provider_type_idx')

    op.drop_table('tenant_default_models')
    with op.batch_alter_table('provider_models', schema=None) as batch_op:
        batch_op.drop_index('provider_model_tenant_id_provider_idx')

    op.drop_table('provider_models')
    # ### end Alembic commands ###
