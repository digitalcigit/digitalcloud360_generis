"""add_name_to_user_model

Revision ID: f45c116fedf1
Revises: d3ea4d165475
Create Date: 2025-08-20 23:02:52.968598

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f45c116fedf1'
down_revision: Union[str, Sequence[str], None] = 'd3ea4d165475'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
