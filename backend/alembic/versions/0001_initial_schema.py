"""create initial PriceNest schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-10-22 16:42:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=128), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 2. Create localities table
    op.create_table(
        'localities',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('slug', sa.String(length=128), nullable=False),
        sa.Column('zone', sa.String(length=64), nullable=False),
        sa.Column('locality_type', sa.String(length=32), nullable=False),
        sa.Column('pincode', sa.String(length=12), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('benchmark_price_per_sqft', sa.Float(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )
    op.create_index(op.f('ix_localities_is_active'), 'localities', ['is_active'], unique=False)
    op.create_index(op.f('ix_localities_pincode'), 'localities', ['pincode'], unique=False)
    op.create_index(op.f('ix_localities_slug'), 'localities', ['slug'], unique=True)

    # 3. Create model_registry table
    op.create_table(
        'model_registry',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('version', sa.String(length=32), nullable=False),
        sa.Column('model_name', sa.String(length=64), nullable=False),
        sa.Column('algorithm', sa.String(length=64), nullable=False),
        sa.Column('training_dataset_ref', sa.String(length=128), nullable=False),
        sa.Column('metrics', sa.JSON(), nullable=False),
        sa.Column('hyperparameters', sa.JSON(), nullable=False),
        sa.Column('feature_names', sa.JSON(), nullable=False),
        sa.Column('artifact_filename', sa.String(length=128), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('deployed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_model_registry_is_active'), 'model_registry', ['is_active'], unique=False)
    op.create_index(op.f('ix_model_registry_version'), 'model_registry', ['version'], unique=True)

    # 4. Create prediction_requests table
    op.create_table(
        'prediction_requests',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('session_id', sa.String(length=64), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=True),
        sa.Column('locality_id', sa.String(length=36), nullable=True),
        sa.Column('locality_name_raw', sa.String(length=128), nullable=False),
        sa.Column('total_sqft', sa.Float(), nullable=False),
        sa.Column('bhk', sa.Float(), nullable=False),
        sa.Column('bathrooms', sa.Integer(), nullable=False),
        sa.Column('balconies', sa.Integer(), nullable=True),
        sa.Column('input_features', sa.JSON(), nullable=False),
        sa.Column('predicted_price_inr', sa.Float(), nullable=False),
        sa.Column('predicted_range_min_inr', sa.Float(), nullable=False),
        sa.Column('predicted_range_max_inr', sa.Float(), nullable=False),
        sa.Column('per_sqft_rate_inr', sa.Float(), nullable=False),
        sa.Column('model_version', sa.String(length=32), nullable=False),
        sa.Column('latency_ms', sa.Float(), nullable=False),
        sa.Column('client_ip_hash', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['locality_id'], ['localities.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_prediction_requests_created_at'), 'prediction_requests', ['created_at'], unique=False)
    op.create_index(op.f('ix_prediction_requests_model_version'), 'prediction_requests', ['model_version'], unique=False)
    op.create_index(op.f('ix_prediction_requests_session_id'), 'prediction_requests', ['session_id'], unique=False)
    op.create_index(op.f('ix_prediction_requests_user_id'), 'prediction_requests', ['user_id'], unique=False)

    # 5. Create valuation_feedback table
    op.create_table(
        'valuation_feedback',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('prediction_request_id', sa.String(length=36), nullable=False),
        sa.Column('feedback_type', sa.String(length=32), nullable=False),
        sa.Column('reported_actual_price_inr', sa.Float(), nullable=True),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['prediction_request_id'], ['prediction_requests.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('prediction_request_id'),
    )

    # 6. Create saved_valuations table
    op.create_table(
        'saved_valuations',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('prediction_request_id', sa.String(length=36), nullable=False),
        sa.Column('custom_title', sa.String(length=128), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['prediction_request_id'], ['prediction_requests.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_saved_valuations_user_id'), 'saved_valuations', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_saved_valuations_user_id'), table_name='saved_valuations')
    op.drop_table('saved_valuations')
    op.drop_table('valuation_feedback')
    op.drop_index(op.f('ix_prediction_requests_user_id'), table_name='prediction_requests')
    op.drop_index(op.f('ix_prediction_requests_session_id'), table_name='prediction_requests')
    op.drop_index(op.f('ix_prediction_requests_model_version'), table_name='prediction_requests')
    op.drop_index(op.f('ix_prediction_requests_created_at'), table_name='prediction_requests')
    op.drop_table('prediction_requests')
    op.drop_index(op.f('ix_model_registry_version'), table_name='model_registry')
    op.drop_index(op.f('ix_model_registry_is_active'), table_name='model_registry')
    op.drop_table('model_registry')
    op.drop_index(op.f('ix_localities_slug'), table_name='localities')
    op.drop_index(op.f('ix_localities_pincode'), table_name='localities')
    op.drop_index(op.f('ix_localities_is_active'), table_name='localities')
    op.drop_table('localities')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
