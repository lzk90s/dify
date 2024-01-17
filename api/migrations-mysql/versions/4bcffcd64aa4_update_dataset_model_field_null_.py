"""update_dataset_model_field_null_available

Revision ID: 4bcffcd64aa4
Revises: 853f9b9cd3b6
Create Date: 2023-08-28 20:58:50.077056

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '4bcffcd64aa4'
down_revision = '853f9b9cd3b6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('datasets', schema=None) as batch_op:
        batch_op.alter_column('embedding_model',
                              existing_type=sa.VARCHAR(length=255),
                              nullable=True,
                              existing_server_default=sa.text("'text-embedding-ada-002'"))
        batch_op.alter_column('embedding_model_provider',
                              existing_type=sa.VARCHAR(length=255),
                              nullable=True,
                              existing_server_default=sa.text("'openai'"))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('datasets', schema=None) as batch_op:
        batch_op.alter_column('embedding_model_provider',
                              existing_type=sa.VARCHAR(length=255),
                              nullable=False,
                              existing_server_default=sa.text("'openai'"))
        batch_op.alter_column('embedding_model',
                              existing_type=sa.VARCHAR(length=255),
                              nullable=False,
                              existing_server_default=sa.text("'text-embedding-ada-002'"))

    # ### end Alembic commands ###