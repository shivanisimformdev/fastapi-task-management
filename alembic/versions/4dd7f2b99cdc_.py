"""empty message

Revision ID: 4dd7f2b99cdc
Revises: cd8a74077d52
Create Date: 2024-02-29 11:09:10.509680

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4dd7f2b99cdc'
down_revision: Union[str, None] = 'cd8a74077d52'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
