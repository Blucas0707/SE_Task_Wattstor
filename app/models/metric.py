from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship

from app.core.database import Base


class Metric(Base):
    """Metric model for device measurements"""

    __tablename__ = 'metrics'

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey('devices.id'))
    name = Column(String, index=True)
    unit = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    value = Column(Float)

    # Relationships
    device = relationship('Device', back_populates='metrics')
    subscriptions = relationship(
        'Subscription', secondary='subscription_metric', back_populates='metrics'
    )
