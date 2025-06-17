from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException

from app.schemas.metric import Metric, MetricCreate, MetricTimeSeries
from app.services import metric_service

router = APIRouter(prefix='/metrics', tags=['Metrics'])


@router.get('/', response_model=list[Metric])
def read_metrics(device_id: int | None = None):
    """
    R3: List all metrics, optionally filtered by device_id.
    """
    try:
        return metric_service.list_metrics(device_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/{metric_id}', response_model=Metric)
def read_metric(metric_id: int):
    """
    R3: Get a specific metric by ID.
    """
    metric = metric_service.get_metric(metric_id)
    if not metric:
        raise HTTPException(status_code=404, detail='Metric not found')
    return metric


@router.post('/', response_model=Metric, status_code=201)
def create_metric(metric_in: MetricCreate):
    """
    R3: Create a new metric.
    """
    try:
        return metric_service.create_metric(metric_in)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put('/{metric_id}', response_model=Metric)
def update_metric(metric_id: int, metric_in: MetricCreate):
    """
    R3: Update an existing metric.
    """
    try:
        return metric_service.update_metric(metric_id, metric_in)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete('/{metric_id}', status_code=204)
def delete_metric(metric_id: int):
    """
    R3: Delete a metric by ID.
    """
    try:
        metric_service.delete_metric(metric_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return None


@router.get('/{metric_id}/history', response_model=MetricTimeSeries)
def get_metric_history(
    metric_id: int,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    interval_minutes: int = 5,
):
    """
    R5: Get historical time series data for a metric.

    Args:
        metric_id: ID of the metric
        start_time: Start time for the time series (defaults to 24 hours ago)
        end_time: End time for the time series (defaults to current time)
        interval_minutes: Time interval between data points in minutes (default: 5)
    """
    try:
        if not end_time:
            end_time = datetime.now(timezone.utc)
        if not start_time:
            start_time = end_time - timedelta(hours=24)

        return metric_service.get_metric_history(
            metric_id=metric_id,
            start_time=start_time,
            end_time=end_time,
            interval_minutes=interval_minutes,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/device/{device_id}/latest', response_model=list[Metric])
def get_device_latest_metrics(device_id: int):
    """
    R3: Get the latest values for all metrics of a device.
    Returns a list of metrics with their latest values and metadata (timestamp, unit).
    """
    try:
        return metric_service.get_latest_metric_value(device_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
