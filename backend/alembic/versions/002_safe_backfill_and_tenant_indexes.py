"""Safe backfill for legacy data into default organization

Revision ID: 002_safe_backfill_and_tenant_indexes
Revises: 001_initial_multitenant_schema
Create Date: 2026-08-17 13:35:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '002_safe_backfill_and_tenant_indexes'
down_revision: Union[str, None] = '001_initial_multitenant_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Ensure default organization exists for any orphaned or legacy rows
    conn = op.get_bind()
    
    # Safe backfill logic
    # 1. Check if default org exists
    conn.execute(sa.text("""
        INSERT INTO organizations (name, slug, is_active, created_at, updated_at)
        SELECT 'Organização Principal', 'default', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
        WHERE NOT EXISTS (SELECT 1 FROM organizations WHERE slug = 'default');
    """))

    # 2. Backfill any user without an organization_id
    conn.execute(sa.text("""
        UPDATE users
        SET organization_id = (SELECT id FROM organizations WHERE slug = 'default' LIMIT 1)
        WHERE organization_id IS NULL;
    """))

    # 3. Create membership records for backfilled users
    conn.execute(sa.text("""
        INSERT INTO organization_members (organization_id, user_id, role, created_at)
        SELECT u.organization_id, u.id, u.role, CURRENT_TIMESTAMP
        FROM users u
        WHERE u.organization_id IS NOT NULL
        AND NOT EXISTS (
            SELECT 1 FROM organization_members om 
            WHERE om.organization_id = u.organization_id AND om.user_id = u.id
        );
    """))

def downgrade() -> None:
    pass
