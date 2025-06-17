# src/schemas.py
from pydantic import BaseModel
from datetime import datetime


class MetricBase(BaseModel):
    name: str
    unit: str


class MetricCreate(MetricBase):
    device_id: int
    value: float


class Metric(MetricBase):
    id: int
    timestamp: datetime
    value: float

    class Config:
        from_attributes = True


class MetricTimeSeries(BaseModel):
    """Schema for time series data of a metric"""

    metric_id: int
    timestamps: list[datetime]
    values: list[float]
    unit: str

    class Config:
        from_attributes = True
