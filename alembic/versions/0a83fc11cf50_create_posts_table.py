"""Create posts table

Revision ID: 0a83fc11cf50
Revises: 
Create Date: 2025-05-15 03:10:00.505525

"""
from typing import Sequence, Union
from sqlalchemy.dialects import postgresql
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0a83fc11cf50'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'posts',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('author_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('media_urls', postgresql.ARRAY(sa.String)),
        sa.Column('visibility', sa.String, server_default='public'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('posts')