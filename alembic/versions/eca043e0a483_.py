"""empty message

Revision ID: eca043e0a483
Revises: 09cfa7951721
Create Date: 2024-02-29 10:59:57.204095

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eca043e0a483'
down_revision: Union[str, None] = '09cfa7951721'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
