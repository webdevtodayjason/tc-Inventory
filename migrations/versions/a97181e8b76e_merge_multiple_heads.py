"""merge multiple heads

Revision ID: a97181e8b76e
Revises: 83ea675314e7, b2e0961e8a45
Create Date: 2025-02-06 11:50:56.826286

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a97181e8b76e'
down_revision = ('83ea675314e7', 'b2e0961e8a45')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
