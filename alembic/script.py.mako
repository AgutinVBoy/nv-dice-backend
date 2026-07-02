"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from pathlib import Path

import sqlalchemy as sa
from alembic import op
${imports if imports else ""}

revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def _run_sql_files(direction: str) -> None:
    base = Path(__file__).parent / "files" / f"{revision}_migration" / direction
    if not base.is_dir():
        return
    for sql_file in sorted(base.glob("*.sql")):
        op.execute(sql_file.read_text(encoding="utf-8"))


def upgrade() -> None:
    # _run_sql_files("upgrade")
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    # _run_sql_files("downgrade")
    ${downgrades if downgrades else "pass"}
