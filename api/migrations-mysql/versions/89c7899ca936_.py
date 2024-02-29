"""empty message

Revision ID: 89c7899ca936
Revises: 187385f442fc
Create Date: 2024-01-21 04:10:23.192853

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '89c7899ca936'
down_revision = '187385f442fc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sites', schema=None) as batch_op:
        batch_op.alter_column('description',
                              existing_type=sa.VARCHAR(length=255),
                              type_=sa.String(length=255),
                              existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sites', schema=None) as batch_op:
        batch_op.alter_column('description',
                              existing_type=sa.Text(),
                              type_=sa.VARCHAR(length=255),
                              existing_nullable=True)

    # ### end Alembic commands ###