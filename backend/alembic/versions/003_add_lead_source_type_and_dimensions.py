"""Add source_type and dimensional columns to leads

Revision ID: 003_add_lead_source_type_and_dimensions
Revises: 002_safe_backfill_and_tenant_indexes
Create Date: 2026-10-02

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003_add_lead_source_type_and_dimensions'
down_revision = '002_safe_backfill_and_tenant_indexes'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Use batch_alter_table or raw SQL for SQLite/Postgres compatibility
    conn = op.get_bind()
    dialect = conn.dialect.name

    if dialect == "postgresql":
        op.execute("ALTER TABLE leads ADD COLUMN IF NOT EXISTS source_type VARCHAR(50) DEFAULT 'kommo';")
        op.execute("ALTER TABLE leads ADD COLUMN IF NOT EXISTS unidade VARCHAR(100);")
        op.execute("ALTER TABLE leads ADD COLUMN IF NOT EXISTS procedimento VARCHAR(100);")
        op.execute("ALTER TABLE leads ADD COLUMN IF NOT EXISTS origem VARCHAR(100);")
        op.execute("ALTER TABLE leads ADD COLUMN IF NOT EXISTS suborigem VARCHAR(100);")
        op.execute("ALTER TABLE leads ADD COLUMN IF NOT EXISTS loss_reason VARCHAR(255);")
        op.execute("CREATE INDEX IF NOT EXISTS ix_leads_source_type ON leads (source_type);")
    else:
        with op.batch_alter_table('leads', schema=None) as batch_op:
            try:
                batch_op.add_column(sa.Column('source_type', sa.String(length=50), nullable=True, server_default='kommo'))
                batch_op.create_index('ix_leads_source_type', ['source_type'], unique=False)
            except Exception:
                pass

def downgrade() -> None:
    conn = op.get_bind()
    dialect = conn.dialect.name
    if dialect == "postgresql":
        op.execute("DROP INDEX IF EXISTS ix_leads_source_type;")
        op.execute("ALTER TABLE leads DROP COLUMN IF EXISTS source_type;")
    else:
        with op.batch_alter_table('leads', schema=None) as batch_op:
            try:
                batch_op.drop_index('ix_leads_source_type')
                batch_op.drop_column('source_type')
            except Exception:
                pass
