"""empty message

Revision ID: 36e542a26602
Revises: df7d1a59e357
Create Date: 2020-07-17 08:55:25.821122

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '36e542a26602'
down_revision = 'df7d1a59e357'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('clients',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('client__platform',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('review', sa.Integer(), nullable=True),
    sa.Column('client_id', sa.Integer(), nullable=False),
    sa.Column('platform_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
    sa.ForeignKeyConstraint(['platform_id'], ['platform.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('order',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.String(length=250), nullable=True),
    sa.Column('total_price', sa.Float(), nullable=True),
    sa.Column('brand_id', sa.Integer(), nullable=False),
    sa.Column('client_id', sa.Integer(), nullable=False),
    sa.Column('integration_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['brand_id'], ['brand.id'], ),
    sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
    sa.ForeignKeyConstraint(['integration_id'], ['integration.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('line_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_name', sa.String(length=250), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('mydata')
    op.add_column('integration', sa.Column('platform_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'integration', 'platform', ['platform_id'], ['id'])
    op.drop_constraint('platform_ibfk_1', 'platform', type_='foreignkey')
    op.drop_column('platform', 'relation_integration')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('platform', sa.Column('relation_integration', mysql.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key('platform_ibfk_1', 'platform', 'integration', ['relation_integration'], ['id'])
    op.drop_constraint(None, 'integration', type_='foreignkey')
    op.drop_column('integration', 'platform_id')
    op.create_table('mydata',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('detail', mysql.VARCHAR(length=250), nullable=True),
    sa.Column('brand_to_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('integration_to_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['brand_to_id'], ['brand.id'], name='mydata_ibfk_1'),
    sa.ForeignKeyConstraint(['integration_to_id'], ['integration.id'], name='mydata_ibfk_2'),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.drop_table('line_item')
    op.drop_table('order')
    op.drop_table('client__platform')
    op.drop_table('clients')
    # ### end Alembic commands ###
