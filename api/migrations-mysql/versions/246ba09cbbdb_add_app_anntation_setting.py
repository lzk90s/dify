"""add_app_anntation_setting

Revision ID: 246ba09cbbdb
Revises: 714aafe25d39
Create Date: 2023-12-14 11:26:12.287264

"""
import sqlalchemy as sa
from alembic import op

from core.sqltype import UUID

# revision identifiers, used by Alembic.
revision = '246ba09cbbdb'
down_revision = '714aafe25d39'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('app_annotation_settings',
                    sa.Column('id', UUID(), server_default=sa.text('(UUID())'), nullable=False),
                    sa.Column('app_id', UUID(), nullable=False),
                    sa.Column('score_threshold', sa.Float(), server_default=sa.text('0'), nullable=False),
                    sa.Column('collection_binding_id', UUID(), nullable=False),
                    sa.Column('created_user_id', UUID(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'),
                              nullable=False),
                    sa.Column('updated_user_id', UUID(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'),
                              nullable=False),
                    sa.PrimaryKeyConstraint('id', name='app_annotation_settings_pkey')
                    )
    with op.batch_alter_table('app_annotation_settings', schema=None) as batch_op:
        batch_op.create_index('app_annotation_settings_app_idx', ['app_id'], unique=False)

    with op.batch_alter_table('app_model_configs', schema=None) as batch_op:
        batch_op.drop_column('annotation_reply')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('app_model_configs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('annotation_reply', sa.TEXT(), autoincrement=False, nullable=True))

    with op.batch_alter_table('app_annotation_settings', schema=None) as batch_op:
        batch_op.drop_index('app_annotation_settings_app_idx')

    op.drop_table('app_annotation_settings')
    # ### end Alembic commands ###
