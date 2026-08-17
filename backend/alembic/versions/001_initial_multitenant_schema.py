"""Initial multi-tenant schema with organizations and member isolation

Revision ID: 001_initial_multitenant_schema
Revises: 
Create Date: 2026-08-17 13:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001_initial_multitenant_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Create organizations table
    op.create_table(
        'organizations',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_organizations_id', 'organizations', ['id'], unique=False)
    op.create_index('ix_organizations_name', 'organizations', ['name'], unique=False)
    op.create_index('ix_organizations_slug', 'organizations', ['slug'], unique=True)

    # 2. Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organizations.id', ondelete='SET NULL'), nullable=True),
        sa.Column('external_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=True),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='Consultora'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint('organization_id', 'external_id', name='uq_user_org_external_id'),
    )
    op.create_index('ix_users_id', 'users', ['id'], unique=False)
    op.create_index('ix_users_organization_id', 'users', ['organization_id'], unique=False)
    op.create_index('ix_users_external_id', 'users', ['external_id'], unique=False)
    op.create_index('ix_users_name', 'users', ['name'], unique=False)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # 3. Create organization_members table
    op.create_table(
        'organization_members',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='Consultora'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint('organization_id', 'user_id', name='uq_org_member_org_user')
    )
    op.create_index('ix_organization_members_id', 'organization_members', ['id'], unique=False)
    op.create_index('ix_organization_members_org_id', 'organization_members', ['organization_id'], unique=False)
    op.create_index('ix_organization_members_user_id', 'organization_members', ['user_id'], unique=False)

    # 4. Create companies table
    op.create_table(
        'companies',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('external_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('custom_fields_values', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint('organization_id', 'external_id', name='uq_company_org_ext_id')
    )
    op.create_index('ix_companies_id', 'companies', ['id'], unique=False)
    op.create_index('ix_companies_organization_id', 'companies', ['organization_id'], unique=False)
    op.create_index('ix_companies_name', 'companies', ['name'], unique=False)

    # 5. Create contacts table
    op.create_table(
        'contacts',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('external_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('company_id', sa.Integer(), sa.ForeignKey('companies.id', ondelete='SET NULL'), nullable=True),
        sa.Column('custom_fields_values', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint('organization_id', 'external_id', name='uq_contact_org_ext_id')
    )
    op.create_index('ix_contacts_id', 'contacts', ['id'], unique=False)
    op.create_index('ix_contacts_organization_id', 'contacts', ['organization_id'], unique=False)
    op.create_index('ix_contacts_org_created', 'contacts', ['organization_id', 'created_at'], unique=False)

    # 6. Create pipelines table
    op.create_table(
        'pipelines',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('external_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_main', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.UniqueConstraint('organization_id', 'external_id', name='uq_pipeline_org_ext_id')
    )
    op.create_index('ix_pipelines_id', 'pipelines', ['id'], unique=False)
    op.create_index('ix_pipelines_organization_id', 'pipelines', ['organization_id'], unique=False)

    # 7. Create lead_status table
    op.create_table(
        'lead_status',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('external_id', sa.Integer(), nullable=True),
        sa.Column('pipeline_id', sa.Integer(), sa.ForeignKey('pipelines.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('color', sa.String(length=50), nullable=True),
        sa.Column('type', sa.Integer(), nullable=False, server_default='1'),
        sa.UniqueConstraint('organization_id', 'external_id', name='uq_lead_status_org_ext_id')
    )
    op.create_index('ix_lead_status_id', 'lead_status', ['id'], unique=False)
    op.create_index('ix_lead_status_organization_id', 'lead_status', ['organization_id'], unique=False)

    # 8. Create tags table
    op.create_table(
        'tags',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('external_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('color', sa.String(length=50), nullable=True),
        sa.UniqueConstraint('organization_id', 'external_id', name='uq_tag_org_ext_id')
    )
    op.create_index('ix_tags_id', 'tags', ['id'], unique=False)
    op.create_index('ix_tags_organization_id', 'tags', ['organization_id'], unique=False)

    # 9. Create custom_fields table
    op.create_table(
        'custom_fields',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('external_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=True),
        sa.Column('field_type', sa.String(length=50), nullable=False),
        sa.UniqueConstraint('organization_id', 'external_id', name='uq_custom_field_org_ext_id')
    )
    op.create_index('ix_custom_fields_id', 'custom_fields', ['id'], unique=False)
    op.create_index('ix_custom_fields_organization_id', 'custom_fields', ['organization_id'], unique=False)

    # 10. Create leads table
    op.create_table(
        'leads',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('external_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('price', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('pipeline_id', sa.Integer(), sa.ForeignKey('pipelines.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status_id', sa.Integer(), sa.ForeignKey('lead_status.id', ondelete='CASCADE'), nullable=False),
        sa.Column('responsible_user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('contact_id', sa.Integer(), sa.ForeignKey('contacts.id', ondelete='SET NULL'), nullable=True),
        sa.Column('company_id', sa.Integer(), sa.ForeignKey('companies.id', ondelete='SET NULL'), nullable=True),
        sa.Column('unidade', sa.String(length=100), nullable=True),
        sa.Column('procedimento', sa.String(length=100), nullable=True),
        sa.Column('origem', sa.String(length=100), nullable=True),
        sa.Column('suborigem', sa.String(length=100), nullable=True),
        sa.Column('loss_reason', sa.String(length=255), nullable=True),
        sa.Column('first_response_time_minutes', sa.Float(), nullable=True),
        sa.Column('sales_cycle_days', sa.Float(), nullable=True),
        sa.Column('custom_fields_values', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint('organization_id', 'external_id', name='uq_lead_org_ext_id')
    )
    op.create_index('ix_leads_id', 'leads', ['id'], unique=False)
    op.create_index('ix_leads_organization_id', 'leads', ['organization_id'], unique=False)
    op.create_index('ix_leads_org_created', 'leads', ['organization_id', 'created_at'], unique=False)
    op.create_index('ix_leads_org_status', 'leads', ['organization_id', 'status_id'], unique=False)
    op.create_index('ix_leads_org_resp_user', 'leads', ['organization_id', 'responsible_user_id'], unique=False)
    op.create_index('ix_leads_org_pipeline', 'leads', ['organization_id', 'pipeline_id'], unique=False)

    # 11. Create lead_tags association table
    op.create_table(
        'lead_tags',
        sa.Column('lead_id', sa.Integer(), sa.ForeignKey('leads.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('tag_id', sa.Integer(), sa.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
    )

    # 12. Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('external_id', sa.Integer(), nullable=True),
        sa.Column('lead_id', sa.Integer(), sa.ForeignKey('leads.id', ondelete='CASCADE'), nullable=True),
        sa.Column('responsible_user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('is_completed', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolution_time_hours', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint('organization_id', 'external_id', name='uq_task_org_ext_id')
    )
    op.create_index('ix_tasks_id', 'tasks', ['id'], unique=False)
    op.create_index('ix_tasks_organization_id', 'tasks', ['organization_id'], unique=False)
    op.create_index('ix_tasks_org_completed_due', 'tasks', ['organization_id', 'is_completed', 'due_date'], unique=False)

    # 13. Create events table
    op.create_table(
        'events',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('external_id', sa.String(length=100), nullable=True),
        sa.Column('lead_id', sa.Integer(), sa.ForeignKey('leads.id', ondelete='CASCADE'), nullable=True),
        sa.Column('type', sa.String(length=100), nullable=False),
        sa.Column('value_before', sa.Text(), nullable=True),
        sa.Column('value_after', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint('organization_id', 'external_id', name='uq_event_org_ext_id')
    )
    op.create_index('ix_events_id', 'events', ['id'], unique=False)
    op.create_index('ix_events_organization_id', 'events', ['organization_id'], unique=False)

    # 14. Create lead_history table
    op.create_table(
        'lead_history',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('lead_id', sa.Integer(), sa.ForeignKey('leads.id', ondelete='CASCADE'), nullable=False),
        sa.Column('from_status_id', sa.Integer(), sa.ForeignKey('lead_status.id', ondelete='SET NULL'), nullable=True),
        sa.Column('to_status_id', sa.Integer(), sa.ForeignKey('lead_status.id', ondelete='CASCADE'), nullable=False),
        sa.Column('changed_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )
    op.create_index('ix_lead_history_id', 'lead_history', ['id'], unique=False)
    op.create_index('ix_lead_history_org_lead', 'lead_history', ['organization_id', 'lead_id'], unique=False)

    # 15. Create sync_logs table
    op.create_table(
        'sync_logs',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('trigger_type', sa.String(length=50), nullable=False, server_default='automatic'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='in_progress'),
        sa.Column('items_synced', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_message', sa.Text(), nullable=True)
    )
    op.create_index('ix_sync_logs_id', 'sync_logs', ['id'], unique=False)
    op.create_index('ix_sync_logs_org_started', 'sync_logs', ['organization_id', 'started_at'], unique=False)

    # 16. Create crm_integrations table
    op.create_table(
        'crm_integrations',
        sa.Column('id', sa.String(length=36), nullable=False, primary_key=True),
        sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('company_id', sa.String(length=36), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False, server_default='kommo'),
        sa.Column('subdomain', sa.String(length=255), nullable=False),
        sa.Column('client_id', sa.String(length=255), nullable=True),
        sa.Column('client_secret', sa.String(length=255), nullable=True),
        sa.Column('redirect_uri', sa.String(length=500), nullable=True),
        sa.Column('access_token', sa.Text(), nullable=True),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('connected_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_sync', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='disconnected'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint('organization_id', 'subdomain', name='uq_crm_integration_org_subdomain')
    )
    op.create_index('ix_crm_integrations_id', 'crm_integrations', ['id'], unique=False)
    op.create_index('ix_crm_integrations_org_id', 'crm_integrations', ['organization_id'], unique=False)

    # 17. Create integration_logs table
    op.create_table(
        'integration_logs',
        sa.Column('id', sa.String(length=36), nullable=False, primary_key=True),
        sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=True),
        sa.Column('integration_id', sa.String(length=36), sa.ForeignKey('crm_integrations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.String(length=100), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='info'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )
    op.create_index('ix_integration_logs_id', 'integration_logs', ['id'], unique=False)
    op.create_index('ix_integration_logs_org_created', 'integration_logs', ['organization_id', 'created_at'], unique=False)

def downgrade() -> None:
    op.drop_table('integration_logs')
    op.drop_table('crm_integrations')
    op.drop_table('sync_logs')
    op.drop_table('lead_history')
    op.drop_table('events')
    op.drop_table('tasks')
    op.drop_table('lead_tags')
    op.drop_table('leads')
    op.drop_table('custom_fields')
    op.drop_table('tags')
    op.drop_table('lead_status')
    op.drop_table('pipelines')
    op.drop_table('contacts')
    op.drop_table('companies')
    op.drop_table('organization_members')
    op.drop_table('users')
    op.drop_table('organizations')
