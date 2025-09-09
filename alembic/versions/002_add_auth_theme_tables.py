### alembic/versions/002_add_auth_theme_tables.py
"""Add authentication and theme tables

Revision ID: 002
Revises: 001
Create Date: 2024-XX-XX XX:XX:XX.XXXXXX
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Create device_type enum
    device_type_enum = postgresql.ENUM('android', 'ios', 'web', name='devicetype')
    device_type_enum.create(op.get_bind())
    
    # Create refresh_tokens table
    op.create_table('refresh_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token_hash', sa.String(length=256), nullable=False),
        sa.Column('device_id', sa.String(length=255), nullable=False),
        sa.Column('device_info', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token_hash')
    )
    op.create_index(op.f('ix_refresh_tokens_user_id'), 'refresh_tokens', ['user_id'], unique=False)
    
    # Create devices table
    op.create_table('devices',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('device_id', sa.String(length=255), nullable=False),
        sa.Column('device_name', sa.String(length=255), nullable=True),
        sa.Column('device_type', device_type_enum, nullable=False),
        sa.Column('platform_version', sa.String(length=100), nullable=True),
        sa.Column('app_version', sa.String(length=50), nullable=True),
        sa.Column('fcm_token', sa.Text(), nullable=True),
        sa.Column('apns_token', sa.Text(), nullable=True),
        sa.Column('supports_biometric', sa.Boolean(), nullable=True),
        sa.Column('biometric_type', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('last_active', sa.DateTime(), nullable=True),
        sa.Column('registered_at', sa.DateTime(), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_devices_user_id'), 'devices', ['user_id'], unique=False)
    op.create_index(op.f('ix_devices_device_id'), 'devices', ['device_id'], unique=False)
    
    # Create user_preferences table
    op.create_table('user_preferences',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('theme_mode', sa.String(length=20), nullable=True),
        sa.Column('primary_color', sa.String(length=7), nullable=True),
        sa.Column('accent_color', sa.String(length=7), nullable=True),
        sa.Column('push_notifications', sa.Boolean(), nullable=True),
        sa.Column('email_notifications', sa.Boolean(), nullable=True),
        sa.Column('meeting_reminders', sa.Boolean(), nullable=True),
        sa.Column('summary_notifications', sa.Boolean(), nullable=True),
        sa.Column('language', sa.String(length=10), nullable=True),
        sa.Column('timezone', sa.String(length=50), nullable=True),
        sa.Column('date_format', sa.String(length=20), nullable=True),
        sa.Column('time_format', sa.String(length=10), nullable=True),
        sa.Column('default_meeting_duration', sa.Integer(), nullable=True),
        sa.Column('auto_join_meetings', sa.Boolean(), nullable=True),
        sa.Column('record_meetings_by_default', sa.Boolean(), nullable=True),
        sa.Column('analytics_enabled', sa.Boolean(), nullable=True),
        sa.Column('crash_reporting', sa.Boolean(), nullable=True),
        sa.Column('custom_settings', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    
    # Enhance users table
    op.add_column('users', sa.Column('google_id', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('apple_id', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('biometric_enabled', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('biometric_public_key', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('avatar_url', sa.String(length=500), nullable=True))
    op.add_column('users', sa.Column('phone_number', sa.String(length=20), nullable=True))
    op.add_column('users', sa.Column('last_login', sa.DateTime(), nullable=True))
    
    # Create unique indexes for social login
    op.create_index('ix_users_google_id', 'users', ['google_id'], unique=True)
    op.create_index('ix_users_apple_id', 'users', ['apple_id'], unique=True)
    
    # Set default values
    op.execute("UPDATE users SET biometric_enabled = false WHERE biometric_enabled IS NULL")
    op.alter_column('users', 'biometric_enabled', nullable=False, server_default='false')


def downgrade():
    # Remove columns from users table
    op.drop_index('ix_users_google_id', table_name='users')
    op.drop_index('ix_users_apple_id', table_name='users')
    op.drop_column('users', 'last_login')
    op.drop_column('users', 'phone_number')
    op.drop_column('users', 'avatar_url')
    op.drop_column('users', 'biometric_public_key')
    op.drop_column('users', 'biometric_enabled')
    op.drop_column('users', 'apple_id')
    op.drop_column('users', 'google_id')
    
    # Drop tables
    op.drop_table('user_preferences')
    op.drop_index(op.f('ix_devices_device_id'), table_name='devices')
    op.drop_index(op.f('ix_devices_user_id'), table_name='devices')
    op.drop_table('devices')
    op.drop_index(op.f('ix_refresh_tokens_user_id'), table_name='refresh_tokens')
    op.drop_table('refresh_tokens')
    
    # Drop enum
    device_type_enum = postgresql.ENUM('android', 'ios', 'web', name='devicetype')
    device_type_enum.drop(op.get_bind())
