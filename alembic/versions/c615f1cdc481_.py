"""empty message

Revision ID: c615f1cdc481
Revises: 4dd7f2b99cdc
Create Date: 2024-02-29 11:14:55.011974

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c615f1cdc481'
down_revision: Union[str, None] = '4dd7f2b99cdc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
