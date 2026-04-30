"""add_stattus_to_target

Revision ID: 5338a446a9fd
Revises: 85b7580379f7
Create Date: 2026-04-30 14:54:39.475704

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5338a446a9fd'
down_revision: Union[str, Sequence[str], None] = '85b7580379f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

target_status_enum = sa.Enum(
    "PENDING",
    "SCANNING",
    "COMPLETED",
    "FAILED",
    name="targetstatus",
)

def upgrade() -> None:
    bind = op.get_bind()

    target_status_enum.create(bind, checkfirst=True)

    op.add_column(
        "targets",
        sa.Column(
            "status",
            target_status_enum,
            nullable=False,
            server_default="PENDING",
        ),
    )

    op.alter_column(
        "targets",
        "status",
        server_default=None,
    )



def downgrade() -> None:
    bind = op.get_bind()

    op.drop_column("targets", "status")

    target_status_enum.drop(bind, checkfirst=True)
