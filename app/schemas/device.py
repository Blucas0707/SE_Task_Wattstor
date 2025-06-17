# src/schemas.py
from pydantic import BaseModel
from typing import List
from .metric import Metric


class DeviceBase(BaseModel):
    name: str


class DeviceCreate(DeviceBase):
    site_id: int


class Device(DeviceBase):
    id: int
    site_id: int
    metrics: List[Metric] = []

    class Config:
        from_attributes = True
