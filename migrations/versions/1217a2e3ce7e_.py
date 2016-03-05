"""empty message

Revision ID: 1217a2e3ce7e
Revises: 1402a9a4e97e
Create Date: 2016-03-05 11:32:09.364053

"""

# revision identifiers, used by Alembic.
revision = '1217a2e3ce7e'
down_revision = '1402a9a4e97e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('conference_space',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('space_name', sa.String(length=64), nullable=True),
    sa.Column('location_id', sa.Integer(), nullable=True),
    sa.Column('event_date', sa.Date(), nullable=True),
    sa.Column('start_time', sa.DateTime(), nullable=True),
    sa.Column('end_time', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('space_name')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('conference_space')
    ### end Alembic commands ###
