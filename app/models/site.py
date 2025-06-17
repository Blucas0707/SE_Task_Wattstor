# src/models.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.user_site import user_site


class Site(Base):
    """Site model"""
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    location = Column(String)

    # Relationships
    devices = relationship("Device", back_populates="site")
    authorized_users = relationship(
        "User",
        secondary=user_site,
        back_populates="authorized_sites"
    )
