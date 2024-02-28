"""Added admin user bool field

Revision ID: 934fe6e78552
Revises: 5f064272cb84
Create Date: 2024-02-28 17:30:13.229336

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '934fe6e78552'
down_revision: Union[str, None] = '5f064272cb84'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
