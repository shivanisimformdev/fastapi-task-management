"""empty message

Revision ID: cd8a74077d52
Revises: eca043e0a483
Create Date: 2024-02-29 11:01:15.050129

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cd8a74077d52'
down_revision: Union[str, None] = 'eca043e0a483'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
