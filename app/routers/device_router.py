from fastapi import APIRouter, HTTPException, Depends

from app.schemas.device import Device, DeviceCreate
from app.services import device_service
from app.models.user import User
from app.core.auth import (
    get_current_active_user,
    get_technician_user,
    get_authorized_user_for_site,
)

router = APIRouter(prefix='/devices', tags=['Devices'])


@router.get('/', response_model=list[Device])
async def read_devices(
    site_id: int | None = None, current_user: User = Depends(get_current_active_user)
):
    """
    R2: List all devices, optionally filtered by site_id.
    Standard users can only see devices at sites they are authorized to access.
    """
    try:
        # If site_id is provided, check authorization
        if site_id is not None:
            await get_authorized_user_for_site(site_id, current_user)
        return device_service.list_devices(site_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/{device_id}', response_model=Device)
async def read_device(
    device_id: int, current_user: User = Depends(get_current_active_user)
):
    """
    R2: Get a specific device by ID.
    Standard users can only see devices at sites they are authorized to access.
    """
    device = device_service.get_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail='Device not found')

    # Check site authorization
    await get_authorized_user_for_site(device.site_id, current_user)
    return device


@router.post('/', response_model=Device, status_code=201)
async def create_device(
    device_in: DeviceCreate, current_user: User = Depends(get_technician_user)
):
    """
    R2: Create a new device.
    Only technicians can create devices at sites they are assigned to.
    """
    try:
        # Check site authorization
        await get_authorized_user_for_site(device_in.site_id, current_user)
        return device_service.create_device(device_in)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put('/{device_id}', response_model=Device)
async def update_device(
    device_id: int,
    device_in: DeviceCreate,
    current_user: User = Depends(get_technician_user),
):
    """
    R2: Update an existing device.
    Only technicians can update devices at sites they are assigned to.
    """
    try:
        # Get existing device to check site
        device = device_service.get_device(device_id)
        if not device:
            raise HTTPException(status_code=404, detail='Device not found')

        # Check authorization for both old and new site
        await get_authorized_user_for_site(device.site_id, current_user)
        if device_in.site_id != device.site_id:
            await get_authorized_user_for_site(device_in.site_id, current_user)

        return device_service.update_device(device_id, device_in)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete('/{device_id}', status_code=204)
async def delete_device(
    device_id: int, current_user: User = Depends(get_technician_user)
):
    """
    R2: Delete a device by ID.
    Only technicians can delete devices at sites they are assigned to.
    """
    try:
        # Get device to check site
        device = device_service.get_device(device_id)
        if not device:
            raise HTTPException(status_code=404, detail='Device not found')

        # Check site authorization
        await get_authorized_user_for_site(device.site_id, current_user)
        device_service.delete_device(device_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return None
