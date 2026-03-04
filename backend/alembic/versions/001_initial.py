"""Initial migration

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("username", sa.String(100), unique=True, nullable=False, index=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("is_verified", sa.Boolean(), default=False),
        sa.Column("merge_count", sa.Integer(), default=0),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("last_login", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "merge_histories",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("output_filename", sa.String(255), nullable=False),
        sa.Column("original_filenames", sa.Text(), nullable=False),
        sa.Column("file_count", sa.Integer(), nullable=False),
        sa.Column("total_pages", sa.Integer(), default=0),
        sa.Column("output_size_bytes", sa.BigInteger(), default=0),
        sa.Column("page_ranges", sa.Text(), nullable=True),
        sa.Column("watermark_applied", sa.String(255), nullable=True),
        sa.Column("compressed", sa.Integer(), default=0),
        sa.Column("download_token", sa.String(255), unique=True, nullable=True),
        sa.Column("download_expires_at", sa.DateTime(), nullable=True),
        sa.Column("download_count", sa.Integer(), default=0),
        sa.Column("status", sa.String(20), default="completed"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("merge_histories")
    op.drop_table("users")