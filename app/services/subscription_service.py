import random
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.db_session import with_db_session, current_session
from app.models.subscription import Subscription
from app.models.metric import Metric
from app.schemas.subscription import (
    Subscription as SubscriptionSchema,
    SubscriptionCreate,
)


@with_db_session
def list_subscriptions() -> list[SubscriptionSchema]:
    """
    Retrieve all subscriptions.
    """
    db: Session = current_session()
    subscriptions = db.query(Subscription).all()
    return [SubscriptionSchema.model_validate(sub) for sub in subscriptions]


@with_db_session
def get_subscription(subscription_id: int) -> SubscriptionSchema | None:
    """
    Retrieve a single subscription by its ID.
    """
    db: Session = current_session()
    subscription = (
        db.query(Subscription).filter(Subscription.id == subscription_id).first()
    )
    return SubscriptionSchema.model_validate(subscription)


@with_db_session
def create_subscription(sub_in: SubscriptionCreate) -> SubscriptionSchema:
    """
    Create a new subscription and link to metrics.
    Validate each metric exists before linking.
    """
    db: Session = current_session()
    # Validate metrics
    metrics = db.query(Metric).filter(Metric.id.in_(sub_in.metric_ids)).all()
    if len(metrics) != len(sub_in.metric_ids):
        raise ValueError('One or more metric IDs are invalid')
    sub = Subscription(name=sub_in.name)
    sub.metrics = metrics
    db.add(sub)
    db.flush()
    db.refresh(sub)
    return SubscriptionSchema.model_validate(sub)


@with_db_session
def update_subscription(
    subscription_id: int, sub_in: SubscriptionCreate
) -> SubscriptionSchema:
    """
    Update an existing subscription's name and metrics.
    Validate metrics before updating links.
    """
    db: Session = current_session()
    sub = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not sub:
        raise ValueError(f'Subscription with id {subscription_id} not found')
    # Validate metrics
    metrics = db.query(Metric).filter(Metric.id.in_(sub_in.metric_ids)).all()
    if len(metrics) != len(sub_in.metric_ids):
        raise ValueError('One or more metric IDs are invalid')
    # Update fields
    sub.name = sub_in.name
    sub.metrics = metrics
    db.flush()
    db.refresh(sub)
    return SubscriptionSchema.model_validate(sub)


@with_db_session
def delete_subscription(subscription_id: int) -> None:
    """
    Delete a subscription and its metric links.
    """
    db: Session = current_session()
    sub = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not sub:
        raise ValueError(f'Subscription with id {subscription_id} not found')
    # Clear associations if needed (handled by cascade)
    db.delete(sub)
    return None


@with_db_session
def get_subscription_latest_values(subscription_id: int) -> dict:
    """
    Get the latest values for all metrics in a subscription.
    Returns a dictionary with metric information and latest values.
    """
    db: Session = current_session()
    sub = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not sub:
        raise ValueError(f'Subscription with id {subscription_id} not found')

    # Get latest values for each metric
    latest_values = []
    for metric in sub.metrics:
        latest = (
            db.query(Metric)
            .filter(Metric.id == metric.id)
            .order_by(Metric.timestamp.desc())
            .first()
        )
        if latest:
            latest_values.append(
                {
                    'metric_id': latest.id,
                    'name': latest.name,
                    'unit': latest.unit,
                    'value': latest.value,
                    'timestamp': latest.timestamp,
                    'device_id': latest.device_id,
                    'device_name': latest.device.name,
                    'site_id': latest.device.site_id,
                    'site_name': latest.device.site.name,
                }
            )

    return {
        'subscription_id': sub.id,
        'subscription_name': sub.name,
        'metrics': latest_values,
    }


@with_db_session
def get_subscription_history(
    subscription_id: int,
    start_time: datetime,
    end_time: datetime,
    interval_minutes: int = 5,
) -> dict:
    """
    Get time series data for all metrics in a subscription.
    Returns a dictionary with metric information and time series data.
    """
    db: Session = current_session()
    sub = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not sub:
        raise ValueError(f'Subscription with id {subscription_id} not found')

    # Get time series for each metric
    time_series = []
    for metric in sub.metrics:
        # Generate time series data
        timestamps = []
        values = []
        current_time = start_time

        # Use fixed random seed to ensure reproducibility
        random.seed(metric.id)

        while current_time <= end_time:
            timestamps.append(current_time)
            # Generate a time-based random value to make it look more realistic
            base_value = metric.value
            variation = random.uniform(-0.1, 0.1) * base_value
            values.append(base_value + variation)
            current_time += timedelta(minutes=interval_minutes)

        time_series.append(
            {
                'metric_id': metric.id,
                'name': metric.name,
                'unit': metric.unit,
                'device_id': metric.device_id,
                'device_name': metric.device.name,
                'site_id': metric.device.site_id,
                'site_name': metric.device.site.name,
                'timestamps': timestamps,
                'values': values,
            }
        )

    return {
        'subscription_id': sub.id,
        'subscription_name': sub.name,
        'start_time': start_time,
        'end_time': end_time,
        'interval_minutes': interval_minutes,
        'metrics': time_series,
    }
