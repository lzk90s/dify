"""modify provider model name length

Revision ID: 187385f442fc
Revises: 88072f0caa04
Create Date: 2024-01-02 07:18:43.887428

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '187385f442fc'
down_revision = '88072f0caa04'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('provider_models', schema=None) as batch_op:
        batch_op.alter_column('model_name',
                              existing_type=sa.VARCHAR(length=40),
                              type_=sa.String(length=255),
                              existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('provider_models', schema=None) as batch_op:
        batch_op.alter_column('model_name',
                              existing_type=sa.String(length=255),
                              type_=sa.VARCHAR(length=40),
                              existing_nullable=False)

    # ### end Alembic commands ###
