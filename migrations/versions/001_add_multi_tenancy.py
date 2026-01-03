"""
Alembic Migration: Add Multi-Tenancy Support
Revision ID: 001_add_multi_tenancy
Create Date: 2026-01-03
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001_add_multi_tenancy'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Add multi-tenancy support to database"""
    
    # 1. Create organizations table
    op.create_table(
        'organizations',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('subdomain', sa.String(63), nullable=False, unique=True),
        sa.Column('slug', sa.String(100), unique=True),
        sa.Column('plan', sa.String(50), nullable=False, server_default='free'),
        sa.Column('subscription_status', sa.String(50), nullable=False, server_default='trialing'),
        sa.Column('stripe_customer_id', sa.String(255), unique=True),
        sa.Column('stripe_subscription_id', sa.String(255), unique=True),
        sa.Column('max_users', sa.Integer(), server_default='5'),
        sa.Column('max_customers', sa.Integer(), server_default='1000'),
        sa.Column('max_ai_requests_per_month', sa.Integer(), server_default='100'),
        sa.Column('current_users_count', sa.Integer(), server_default='0'),
        sa.Column('current_customers_count', sa.Integer(), server_default='0'),
        sa.Column('current_ai_requests_this_month', sa.Integer(), server_default='0'),
        sa.Column('owner_email', sa.String(255)),
        sa.Column('owner_phone', sa.String(50)),
        sa.Column('company_website', sa.String(255)),
        sa.Column('logo_url', sa.String(500)),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('is_verified', sa.Boolean(), server_default='false'),
        sa.Column('data_retention_days', sa.Integer(), server_default='365'),
        sa.Column('trial_ends_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now())
    )
    
    # Create indexes for organizations
    op.create_index('idx_organizations_subdomain', 'organizations', ['subdomain'])
    op.create_index('idx_organizations_slug', 'organizations', ['slug'])
    op.create_index('idx_organizations_plan', 'organizations', ['plan'])
    
    # 2. Create default organization for existing data
    op.execute("""
        INSERT INTO organizations (name, subdomain, slug, plan, subscription_status, is_active)
        VALUES ('Default Organization', 'default', 'default-org', 'enterprise', 'active', true)
    """)
    
    # 3. Add organization_id to users table
    op.add_column('users', 
        sa.Column('organization_id', sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        'fk_users_organization',
        'users', 'organizations',
        ['organization_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_index('idx_users_org', 'users', ['organization_id'])
    
    # Migrate existing users to default organization
    op.execute("""
        UPDATE users 
        SET organization_id = (SELECT id FROM organizations WHERE subdomain = 'default')
        WHERE organization_id IS NULL
    """)
    
    # Make organization_id NOT NULL after migration
    op.alter_column('users', 'organization_id', nullable=False)
    
    # 4. Add organization_id to related tables
    tables_to_update = [
        'customers',
        'deals', 
        'campaigns',
        'messages',
        'leads'
    ]
    
    for table in tables_to_update:
        # Check if table exists
        try:
            # Add column
            op.add_column(table,
                sa.Column('organization_id', sa.Integer(), nullable=True)
            )
            
            # Add foreign key
            op.create_foreign_key(
                f'fk_{table}_organization',
                table, 'organizations',
                ['organization_id'], ['id'],
                ondelete='CASCADE'
            )
            
            # Create index for performance
            op.create_index(f'idx_{table}_org', table, ['organization_id'])
            
            # Migrate existing data to default organization
            op.execute(f"""
                UPDATE {table}
                SET organization_id = (SELECT id FROM organizations WHERE subdomain = 'default')
                WHERE organization_id IS NULL
            """)
            
            # Make NOT NULL
            op.alter_column(table, 'organization_id', nullable=False)
            
        except Exception as e:
            print(f"Warning: Could not update table {table}: {e}")
    
    # 5. Create composite indexes for common queries
    op.create_index('idx_customers_org_email', 'customers', ['organization_id', 'email'])
    op.create_index('idx_deals_org_status', 'deals', ['organization_id', 'status'])
    op.create_index('idx_campaigns_org_status', 'campaigns', ['organization_id', 'status'])


def downgrade():
    """Remove multi-tenancy support"""
    
    # Drop composite indexes
    op.drop_index('idx_campaigns_org_status', 'campaigns')
    op.drop_index('idx_deals_org_status', 'deals')
    op.drop_index('idx_customers_org_email', 'customers')
    
    # Remove organization_id from related tables
    tables_to_rollback = ['customers', 'deals', 'campaigns', 'messages', 'leads']
    
    for table in tables_to_rollback:
        try:
            op.drop_index(f'idx_{table}_org', table)
            op.drop_constraint(f'fk_{table}_organization', table, type_='foreignkey')
            op.drop_column(table, 'organization_id')
        except Exception as e:
            print(f"Warning: Could not rollback table {table}: {e}")
    
    # Remove organization_id from users
    op.drop_index('idx_users_org', 'users')
    op.drop_constraint('fk_users_organization', 'users', type_='foreignkey')
    op.drop_column('users', 'organization_id')
    
    # Drop organizations table
    op.drop_index('idx_organizations_plan', 'organizations')
    op.drop_index('idx_organizations_slug', 'organizations')
    op.drop_index('idx_organizations_subdomain', 'organizations')
    op.drop_table('organizations')
