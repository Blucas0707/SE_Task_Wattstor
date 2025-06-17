# src/schemas.py
from pydantic import BaseModel
from typing import List
from .device import Device


class SiteBase(BaseModel):
    name: str


class SiteCreate(SiteBase):
    pass


class Site(SiteBase):
    id: int
    devices: List[Device] = []

    class Config:
        from_attributes = True
