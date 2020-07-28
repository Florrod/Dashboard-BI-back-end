"""empty message

Revision ID: 260ff7986097
Revises: 
Create Date: 2020-07-27 18:25:47.434019

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '260ff7986097'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('clients',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('orders_count', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('enterprise',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('CIF_number', sa.String(length=10), nullable=True),
    sa.Column('name', sa.String(length=120), nullable=True),
    sa.Column('password', sa.String(length=120), nullable=True),
    sa.Column('address', sa.String(length=120), nullable=True),
    sa.Column('phone', sa.String(length=80), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('CIF_number'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('name')
    )
    op.create_table('platform',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('brand',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=True),
    sa.Column('logo', sa.String(length=120), nullable=True),
    sa.Column('enterprise_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['enterprise_id'], ['enterprise.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('integration',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('API_key', sa.String(length=120), nullable=True),
    sa.Column('brand_id', sa.Integer(), nullable=False),
    sa.Column('platform_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['brand_id'], ['brand.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['platform_id'], ['platform.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('order',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.String(length=250), nullable=True),
    sa.Column('total_price', sa.Float(), nullable=True),
    sa.Column('review', sa.Float(), nullable=True),
    sa.Column('platform_id', sa.Integer(), nullable=False),
    sa.Column('brand_id', sa.Integer(), nullable=False),
    sa.Column('integration_id', sa.Integer(), nullable=False),
    sa.Column('client_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['brand_id'], ['brand.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
    sa.ForeignKeyConstraint(['integration_id'], ['integration.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['platform_id'], ['platform.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('line_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_name', sa.String(length=250), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('line_item')
    op.drop_table('order')
    op.drop_table('integration')
    op.drop_table('brand')
    op.drop_table('platform')
    op.drop_table('enterprise')
    op.drop_table('clients')
    # ### end Alembic commands ###
