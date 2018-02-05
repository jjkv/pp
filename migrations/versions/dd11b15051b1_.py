"""empty message

Revision ID: dd11b15051b1
Revises: 9fef8a7e9f41
Create Date: 2018-02-05 13:57:56.649698

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dd11b15051b1'
down_revision = '9fef8a7e9f41'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('school', sa.Column('admin_school', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('school', 'admin_school')
    # ### end Alembic commands ###
