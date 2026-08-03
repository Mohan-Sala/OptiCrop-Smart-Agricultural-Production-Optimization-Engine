"""add_indexes

Revision ID: 097ac139b0de
Revises: b52b022d585c
Create Date: 2026-07-18 21:12:50.275228

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '097ac139b0de'
down_revision: Union[str, None] = 'b52b022d585c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Unique constraint on active alerts
    op.create_unique_constraint(
        'uq_active_alert_dedup',
        'monitoring_alerts',
        ['project_id', 'model_id', 'rule_id', 'severity', 'status']
    )
    # Partial index on prediction_runs for status = 'FAILED'
    op.create_index(
        'idx_prediction_runs_failed',
        'prediction_runs',
        ['project_id', 'prediction_timestamp'],
        postgresql_where=sa.text("status = 'FAILED'")
    )
    # Partial index on monitoring_alerts for status = 'ACTIVE'
    op.create_index(
        'idx_monitoring_alerts_active',
        'monitoring_alerts',
        ['project_id', 'created_at'],
        postgresql_where=sa.text("status = 'ACTIVE'")
    )


def downgrade() -> None:
    op.drop_index('idx_monitoring_alerts_active', table_name='monitoring_alerts')
    op.drop_index('idx_prediction_runs_failed', table_name='prediction_runs')
    op.drop_constraint('uq_active_alert_dedup', 'monitoring_alerts', type_='unique')
