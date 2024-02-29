"""empty message

Revision ID: 286f24867d2e
Revises: c615f1cdc481
Create Date: 2024-02-29 11:19:06.729386

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '286f24867d2e'
down_revision: Union[str, None] = 'c615f1cdc481'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
