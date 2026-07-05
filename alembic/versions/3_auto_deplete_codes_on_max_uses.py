"""auto deplete codes on max uses

Revision ID: 3
Revises: 2
Create Date: 2026-07-05 15:50:48.211552

"""
from pathlib import Path

import sqlalchemy as sa
from alembic import op


revision = '3'
down_revision = '2'
branch_labels = None
depends_on = None


def _run_sql_files(direction: str) -> None:
    base = Path(__file__).parent / "files" / f"{revision}_migration" / direction
    if not base.is_dir():
        return
    for sql_file in sorted(base.glob("*.sql")):
        op.execute(sql_file.read_text(encoding="utf-8"))


def upgrade() -> None:
    op.execute("""
        CREATE OR REPLACE FUNCTION check_code_uses_limit()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.uses_count >= NEW.max_uses AND NEW.status = 'active'::code_status_enum THEN
                NEW.status := 'depleted'::code_status_enum;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER trigger_update_code_status
        BEFORE INSERT OR UPDATE ON codes
        FOR EACH ROW
        EXECUTE FUNCTION check_code_uses_limit();
    """)

    op.execute("""
        UPDATE codes
        SET status = 'depleted'::code_status_enum,
            updated_at = now()
        WHERE uses_count >= max_uses 
          AND status = 'active'::code_status_enum;
    """)


def downgrade() -> None:
    op.execute("""
        DROP TRIGGER IF EXISTS trigger_update_code_status ON codes;
    """)
    op.execute("""
        DROP FUNCTION IF EXISTS check_code_uses_limit();
    """)
