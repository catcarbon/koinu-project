"""all tables

Revision ID: 055989a7f82f
Revises: 
Create Date: 2019-12-01 03:34:22.759073

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '055989a7f82f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Channel',
    sa.Column('cid', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=32), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('channel_created', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('channel_updated', sa.DateTime(timezone=True), nullable=True),
    sa.Column('is_public', sa.Boolean(), server_default='1', nullable=False),
    sa.Column('channel_admin_uid', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['channel_admin_uid'], ['User.uid'], ),
    sa.PrimaryKeyConstraint('cid')
    )
    op.create_index(op.f('ix_Channel_name'), 'Channel', ['name'], unique=False)
    op.create_table('Article',
    sa.Column('aid', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(length=64), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('article_created', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('article_updated', sa.DateTime(timezone=True), nullable=True),
    sa.Column('article_status', sa.SmallInteger(), server_default='1', nullable=False),
    sa.Column('article_author_uid', sa.Integer(), nullable=True),
    sa.Column('article_channel_cid', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['article_author_uid'], ['User.uid'], ),
    sa.ForeignKeyConstraint(['article_channel_cid'], ['Channel.cid'], ),
    sa.PrimaryKeyConstraint('aid')
    )
    op.create_index(op.f('ix_Article_title'), 'Article', ['title'], unique=False)
    op.create_table('Subscription',
    sa.Column('user_uid', sa.Integer(), nullable=True),
    sa.Column('channel_cid', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['channel_cid'], ['Channel.cid'], ),
    sa.ForeignKeyConstraint(['user_uid'], ['User.uid'], )
    )
    op.create_table('Favorite',
    sa.Column('user_uid', sa.Integer(), nullable=True),
    sa.Column('article_aid', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['article_aid'], ['Article.aid'], ),
    sa.ForeignKeyConstraint(['user_uid'], ['User.uid'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Favorite')
    op.drop_table('Subscription')
    op.drop_index(op.f('ix_Article_title'), table_name='Article')
    op.drop_table('Article')
    op.drop_index(op.f('ix_Channel_name'), table_name='Channel')
    op.drop_table('Channel')
    # ### end Alembic commands ###