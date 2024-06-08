"""empty message

Revision ID: dd95e9fbc9ef
Revises: 
Create Date: 2024-06-05 04:07:23.781148

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dd95e9fbc9ef'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('medicine',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(length=32), nullable=False),
    sa.Column('elder_id', sa.Integer(), nullable=False),
    sa.Column('start_year', sa.Integer(), nullable=False),
    sa.Column('start_month', sa.Integer(), nullable=False),
    sa.Column('start_day', sa.Integer(), nullable=False),
    sa.Column('end_year', sa.Integer(), nullable=False),
    sa.Column('end_month', sa.Integer(), nullable=False),
    sa.Column('end_day', sa.Integer(), nullable=False),
    sa.Column('medicine_period', sa.Integer(), nullable=False),
    sa.Column('memo', sa.String(length=64), nullable=True),
    sa.Column('do_alarm', sa.Integer(), nullable=False),
    sa.Column('confirm_alarm_minute', sa.Integer(), nullable=False),
    sa.Column('is_complete', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['elder_id'], ['elder.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('medicine_alarm',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('medicine_id', sa.Integer(), nullable=False),
    sa.Column('elder_id', sa.Integer(), nullable=False),
    sa.Column('year', sa.Integer(), nullable=False),
    sa.Column('month', sa.Integer(), nullable=False),
    sa.Column('day', sa.Integer(), nullable=False),
    sa.Column('hour', sa.Integer(), nullable=False),
    sa.Column('minute', sa.Integer(), nullable=False),
    sa.Column('do_alarm', sa.Boolean(), nullable=False),
    sa.Column('confirm_alarm_minute', sa.Integer(), nullable=False),
    sa.Column('is_complete', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['elder_id'], ['elder.id'], ),
    sa.ForeignKeyConstraint(['medicine_id'], ['medicine.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('medicine_alarm')
    op.drop_table('medicine')
    # ### end Alembic commands ###
