"""Added admin user bool field

Revision ID: 5f064272cb84
Revises: 87da61af279b
Create Date: 2024-02-28 17:27:46.127678

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5f064272cb84'
down_revision: Union[str, None] = '87da61af279b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
