from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, HTTPException, Depends

from app.schemas.subscription import Subscription, SubscriptionCreate
from app.services import subscription_service
from app.models.user import User
from app.core.auth import get_current_active_user

router = APIRouter(prefix='/subscriptions', tags=['Subscriptions'])


@router.get('/', response_model=list[Subscription])
async def read_subscriptions(current_user: User = Depends(get_current_active_user)):
    """
    R4: List all subscriptions for the current user.
    """
    return subscription_service.list_subscriptions(current_user.id)


@router.get('/{subscription_id}', response_model=Subscription)
async def read_subscription(
    subscription_id: int, current_user: User = Depends(get_current_active_user)
):
    """
    R4: Get a specific subscription by ID.
    Only accessible by the subscription owner.
    """
    sub = subscription_service.get_subscription(subscription_id)
    if not sub:
        raise HTTPException(status_code=404, detail='Subscription not found')
    if sub.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail='Not authorized to access this subscription'
        )
    return sub


@router.post('/', response_model=Subscription, status_code=201)
async def create_subscription(
    sub_in: SubscriptionCreate, current_user: User = Depends(get_current_active_user)
):
    """
    R4: Create a new subscription.
    Users can subscribe to any metrics they have access to.
    """
    try:
        return subscription_service.create_subscription(sub_in, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put('/{subscription_id}', response_model=Subscription)
async def update_subscription(
    subscription_id: int,
    sub_in: SubscriptionCreate,
    current_user: User = Depends(get_current_active_user),
):
    """
    R4: Update an existing subscription.
    Only accessible by the subscription owner.
    """
    try:
        sub = subscription_service.get_subscription(subscription_id)
        if not sub:
            raise HTTPException(status_code=404, detail='Subscription not found')
        if sub.user_id != current_user.id:
            raise HTTPException(
                status_code=403, detail='Not authorized to modify this subscription'
            )
        return subscription_service.update_subscription(subscription_id, sub_in)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete('/{subscription_id}', status_code=204)
async def delete_subscription(
    subscription_id: int, current_user: User = Depends(get_current_active_user)
):
    """
    R4: Delete a subscription by ID.
    Only accessible by the subscription owner.
    """
    try:
        sub = subscription_service.get_subscription(subscription_id)
        if not sub:
            raise HTTPException(status_code=404, detail='Subscription not found')
        if sub.user_id != current_user.id:
            raise HTTPException(
                status_code=403, detail='Not authorized to delete this subscription'
            )
        subscription_service.delete_subscription(subscription_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return None


@router.get('/{subscription_id}/latest')
async def get_subscription_latest_values(
    subscription_id: int, current_user: User = Depends(get_current_active_user)
):
    """
    R4: Get the latest values for all metrics in a subscription.
    Only accessible by the subscription owner.
    """
    try:
        sub = subscription_service.get_subscription(subscription_id)
        if not sub:
            raise HTTPException(status_code=404, detail='Subscription not found')
        if sub.user_id != current_user.id:
            raise HTTPException(
                status_code=403, detail='Not authorized to access this subscription'
            )
        return subscription_service.get_subscription_latest_values(subscription_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get('/{subscription_id}/history')
async def get_subscription_history(
    subscription_id: int,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    interval_minutes: int = 5,
    current_user: User = Depends(get_current_active_user),
):
    """
    R5: Get historical time series data for all metrics in a subscription.

    Args:
        subscription_id: ID of the subscription
        start_time: Start time for the time series (defaults to 24 hours ago)
        end_time: End time for the time series (defaults to current time)
        interval_minutes: Time interval between data points in minutes (default: 5)
    """
    try:
        # Check subscription ownership
        sub = subscription_service.get_subscription(subscription_id)
        if not sub:
            raise HTTPException(status_code=404, detail='Subscription not found')
        if sub.user_id != current_user.id:
            raise HTTPException(
                status_code=403, detail='Not authorized to access this subscription'
            )

        # Set default time range if not provided
        if not end_time:
            end_time = datetime.now(timezone.utc)
        if not start_time:
            start_time = end_time - timedelta(hours=24)

        return subscription_service.get_subscription_history(
            subscription_id=subscription_id,
            start_time=start_time,
            end_time=end_time,
            interval_minutes=interval_minutes,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
