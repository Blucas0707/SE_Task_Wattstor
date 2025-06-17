# src/models.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Device(Base):
    """Device model"""
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"))
    type = Column(String)  # e.g., "sensor", "controller", etc.

    # Relationships
    site = relationship("Site", back_populates="devices")
    metrics = relationship("Metric", back_populates="device", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure device has at least one metric
        if not self.metrics:
            self.metrics = []
