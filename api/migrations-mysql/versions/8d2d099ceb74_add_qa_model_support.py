"""add_qa_model_support

Revision ID: 8d2d099ceb74
Revises: a5b56fb053ef
Create Date: 2023-07-18 15:25:15.293438

"""
import sqlalchemy as sa
from alembic import op

from core.sqltype import UUID

# revision identifiers, used by Alembic.
revision = '8d2d099ceb74'
down_revision = '7ce5a52e4eee'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('document_segments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('answer', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('updated_by', UUID(), nullable=True))
        batch_op.add_column(
            sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'), nullable=False))

    with op.batch_alter_table('documents', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('doc_form', sa.String(length=255), server_default=sa.text("'text_model'"),
                      nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('documents', schema=None) as batch_op:
        batch_op.drop_column('doc_form')

    with op.batch_alter_table('document_segments', schema=None) as batch_op:
        batch_op.drop_column('updated_at')
        batch_op.drop_column('updated_by')
        batch_op.drop_column('answer')

    # ### end Alembic commands ###
