"""allow multiple gender identities

Revision ID: 37aa4277ce51
Revises: fe2c6d7c4e84
Create Date: 2021-01-17 20:37:34.863957

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '37aa4277ce51'
down_revision = 'fe2c6d7c4e84'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('gender_identity_association',
    sa.Column('person_id', sa.Integer(), nullable=False),
    sa.Column('gender_identity_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['gender_identity_id'], ['gender_identity.id'], ),
    sa.ForeignKeyConstraint(['person_id'], ['person.id'], ),
    sa.PrimaryKeyConstraint('person_id', 'gender_identity_id')
    )
    op.drop_constraint('person_ibfk_1', 'person', type_='foreignkey')
    op.drop_column('person', 'gender_identity_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('person', sa.Column('gender_identity_id', mysql.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('person_ibfk_1', 'person', 'gender_identity', ['gender_identity_id'], ['id'])
    op.drop_table('gender_identity_association')
    # ### end Alembic commands ###