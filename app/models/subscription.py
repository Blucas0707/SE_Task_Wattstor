# src/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.core.database import Base

# many-to-many association between Subscription and Metric
subscription_metric = Table(
    'subscription_metric',
    Base.metadata,
    Column('subscription_id', ForeignKey('subscriptions.id'), primary_key=True),
    Column('metric_id', ForeignKey('metrics.id'), primary_key=True),
)


class Subscription(Base):
    """Subscription model for metric subscriptions"""

    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))

    # Relationships
    user = relationship('User', back_populates='subscriptions')
    metrics = relationship(
        'Metric', secondary=subscription_metric, back_populates='subscriptions'
    )
