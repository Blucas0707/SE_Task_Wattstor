# src/schemas.py
from pydantic import BaseModel
from typing import List


class SubscriptionBase(BaseModel):
    name: str
    metric_ids: List[int]


class SubscriptionCreate(SubscriptionBase):
    pass


class Subscription(SubscriptionBase):
    id: int

    class Config:
        from_attributes = True
