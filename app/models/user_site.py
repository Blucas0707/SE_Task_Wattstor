from sqlalchemy import Column, Integer, ForeignKey, Table

from app.core.database import Base

# Association table for user-site relationship
user_site = Table(
    'user_site',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('site_id', Integer, ForeignKey('sites.id'), primary_key=True),
)
