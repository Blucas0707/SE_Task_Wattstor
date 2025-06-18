import enum

from sqlalchemy import Column, Integer, String, Enum, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.user_site import user_site


class UserRole(enum.Enum):
    """User roles in the system"""

    STANDARD = 'standard'
    TECHNICIAN = 'technician'
    ADMIN = 'admin'


class User(Base):
    """User model for authentication and authorization"""

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.STANDARD)
    is_active = Column(Boolean, default=True)

    # Relationships
    authorized_sites = relationship(
        'Site', secondary=user_site, back_populates='authorized_users'
    )
    subscriptions = relationship('Subscription', back_populates='user')
