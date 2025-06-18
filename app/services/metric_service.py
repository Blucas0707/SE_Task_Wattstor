import random
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.db_session import with_db_session, current_session
from app.models.device import Device
from app.models.metric import Metric
from app.schemas.metric import Metric as MetricSchema, MetricCreate, MetricTimeSeries


@with_db_session
def list_metrics(device_id: int | None = None) -> list[MetricSchema]:
    """
    Retrieve all metrics. If device_id is provided, filter metrics by that device.
    Sorted by timestamp descending.
    """
    db: Session = current_session()
    query = db.query(Metric)
    if device_id is not None:
        query = query.filter(Metric.device_id == device_id)
    metrics = query.order_by(Metric.timestamp.desc()).all()
    return [MetricSchema.model_validate(metric) for metric in metrics]


@with_db_session
def get_metric(metric_id: int) -> MetricSchema | None:
    """
    Retrieve a single metric by its ID.
    """
    db: Session = current_session()
    metric = db.query(Metric).filter(Metric.id == metric_id).first()
    return MetricSchema.model_validate(metric)


@with_db_session
def create_metric(metric_in: MetricCreate) -> MetricSchema:
    """
    Create a new metric for a specific device.
    Validate the device exists before creation.
    """
    db: Session = current_session()
    device = db.query(Device).filter(Device.id == metric_in.device_id).first()
    if not device:
        raise ValueError(f'Device with id {metric_in.device_id} does not exist')
    metric = Metric(**metric_in.model_dump())
    db.add(metric)
    db.flush()
    db.refresh(metric)
    return MetricSchema.model_validate(metric)


@with_db_session
def update_metric(metric_id: int, metric_in: MetricCreate) -> MetricSchema:
    """
    Update an existing metric's data.
    If device_id changes, validate new device exists.
    """
    db: Session = current_session()
    metric = db.query(Metric).filter(Metric.id == metric_id).first()
    if not metric:
        raise ValueError(f'Metric with id {metric_id} not found')
    if metric_in.device_id != metric.device_id:
        new_device = db.query(Device).filter(Device.id == metric_in.device_id).first()
        if not new_device:
            raise ValueError(f'Device with id {metric_in.device_id} does not exist')
        metric.device_id = metric_in.device_id
    metric.name = metric_in.name
    metric.unit = metric_in.unit
    metric.value = metric_in.value
    db.flush()
    db.refresh(metric)
    return MetricSchema.model_validate(metric)


@with_db_session
def delete_metric(metric_id: int) -> None:
    """
    Delete a metric by its ID.
    """
    db: Session = current_session()
    metric = db.query(Metric).filter(Metric.id == metric_id).first()
    if not metric:
        raise ValueError(f'Metric with id {metric_id} not found')
    db.delete(metric)
    return None


@with_db_session
def get_metric_history(
    db: Session,
    metric_id: int,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    interval_minutes: int = 5,
) -> MetricTimeSeries:
    """Get the historical time series data for a metric"""
    # Validate if the metric exists
    metric = db.query(Metric).filter(Metric.id == metric_id).first()
    if not metric:
        raise HTTPException(status_code=404, detail='Metric not found')

    # Set default time range
    if not end_time:
        end_time = datetime.utcnow()
    if not start_time:
        start_time = end_time - timedelta(hours=24)

    # Validate time range
    if start_time >= end_time:
        raise HTTPException(
            status_code=400, detail='Start time must be before end time'
        )

    # Generate timestamps
    timestamps = []
    current_time = start_time
    while current_time <= end_time:
        timestamps.append(current_time.isoformat() + 'Z')
        current_time += timedelta(minutes=interval_minutes)

    # Use a fixed seed to generate reproducible random data
    random.seed(metric_id)
    values = [random.uniform(0, 100) for _ in range(len(timestamps))]

    return MetricTimeSeries(
        metric_id=metric_id, timestamps=timestamps, values=values, unit=metric.unit
    )


@with_db_session
def get_latest_metric_value(device_id: int) -> list[MetricSchema]:
    """
    Get the latest value for each metric of a device.
    Returns a list of metrics with their latest values and metadata.
    """
    db: Session = current_session()
    # Get all metrics for the device
    metrics = db.query(Metric).filter(Metric.device_id == device_id).all()

    if not metrics:
        raise ValueError(f'No metrics found for device {device_id}')

    # Get the latest value for each metric
    latest_metrics = []
    for metric in metrics:
        latest = (
            db.query(Metric)
            .filter(Metric.device_id == device_id, Metric.name == metric.name)
            .order_by(Metric.timestamp.desc())
            .first()
        )
        if latest:
            latest_metrics.append(latest)

    return [
        MetricSchema.model_validate(latest_metric) for latest_metric in latest_metrics
    ]
