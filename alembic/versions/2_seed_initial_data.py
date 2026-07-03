"""seed initial data

Revision ID: 2
Revises: 1
Create Date: 2026-07-03 02:50:55.406970

"""
from decimal import Decimal
from pathlib import Path

import sqlalchemy as sa
from alembic import op

revision = '2'
down_revision = '1'
branch_labels = None
depends_on = None


def _run_sql_files(direction: str) -> None:
    base = Path(__file__).parent / "files" / f"{revision}_migration" / direction
    if not base.is_dir():
        return
    for sql_file in sorted(base.glob("*.sql")):
        op.execute(sql_file.read_text(encoding="utf-8"))


roles_table = sa.table(
    'roles',
    sa.column('code', sa.String),
    sa.column('label', sa.String)
)

config_table = sa.table(
    'system_configurations',
    sa.column('min_game_bet', sa.Numeric),
    sa.column('is_maintenance_enabled', sa.Boolean)
)


def upgrade() -> None:
    op.bulk_insert(roles_table, [
        {'code': 'user', 'label': 'Пользователь'},
        {'code': 'admin', 'label': 'Администратор'}
    ])

    op.bulk_insert(config_table, [
        {
            'min_game_bet': Decimal('1.00'),
            'is_maintenance_enabled': False
        }
    ])

    op.execute("""
        CREATE OR REPLACE FUNCTION protect_system_config_delete()
        RETURNS TRIGGER AS $$
        BEGIN
            IF OLD.id = 1 THEN
                RAISE EXCEPTION 'Удаление системной конфигурации (id=1) запрещено на уровне СУБД.';
            END IF;
            RETURN OLD;
        END;
        $$
        LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER check_system_config_delete
        BEFORE DELETE ON system_configurations
        FOR EACH ROW
        EXECUTE FUNCTION protect_system_config_delete();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS check_system_config_delete ON system_configurations;")
    op.execute("DROP FUNCTION IF EXISTS protect_system_config_delete();")
    op.execute(config_table.delete())
    op.execute(roles_table.delete().where(roles_table.c.code.in_(['user', 'admin'])))
