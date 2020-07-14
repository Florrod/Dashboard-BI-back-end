"""empty message

Revision ID: 36ad6d5ca710
Revises: aecc5676d3e3
Create Date: 2020-07-13 17:18:10.228308

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '36ad6d5ca710'
down_revision = 'aecc5676d3e3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('mydata',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('detail', sa.String(length=250), nullable=True),
    sa.Column('brand_to_id', sa.Integer(), nullable=False),
    sa.Column('integration_to_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['brand_to_id'], ['brand.id'], ),
    sa.ForeignKeyConstraint(['integration_to_id'], ['integration.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('mydata')
    # ### end Alembic commands ###
