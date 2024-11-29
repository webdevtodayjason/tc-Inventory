"""Add PIN code field to User model

Revision ID: c8a18f1acdb4
Revises: 091345c15f66
Create Date: 2024-11-29 12:46:37.699650

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c8a18f1acdb4'
down_revision = '091345c15f66'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('pin_code', sa.String(length=6), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('pin_code')

    # ### end Alembic commands ###
