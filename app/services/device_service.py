from sqlalchemy.orm import Session

from app.models.site import Site
from app.models.device import Device
from app.schemas.device import DeviceCreate
from app.core.db_session import with_db_session, current_session


@with_db_session
def list_devices(site_id: int | None = None) -> list[Device]:
    """
    Retrieve all devices. If site_id is provided, filter devices by that site.
    """
    db: Session = current_session()
    query = db.query(Device)
    if site_id is not None:
        query = query.filter(Device.site_id == site_id)
    return query.all()


@with_db_session
def get_device(device_id: int) -> Device | None:
    """
    Retrieve a single device by its ID.
    """
    db: Session = current_session()
    return db.query(Device).filter(Device.id == device_id).first()


@with_db_session
def create_device(device_in: DeviceCreate) -> Device:
    """
    Create a new device under a specific site.
    """
    db: Session = current_session()
    # Ensure the site exists before creating device
    site = db.query(Site).filter(Site.id == device_in.site_id).first()
    if not site:
        raise ValueError(f'Site with id {device_in.site_id} does not exist')
    device = Device(**device_in.model_dump())
    db.add(device)
    db.flush()  # assign ID
    db.refresh(device)
    return device


@with_db_session
def update_device(device_id: int, device_in: DeviceCreate) -> Device:
    """
    Update an existing device's attributes.
    """
    db: Session = current_session()
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise ValueError(f'Device with id {device_id} not found')
    # Optionally validate new site
    site = db.query(Site).filter(Site.id == device_in.site_id).first()
    if not site:
        raise ValueError(f'Site with id {device_in.site_id} does not exist')
    # Update fields
    device.name = device_in.name
    device.site_id = device_in.site_id
    db.flush()
    db.refresh(device)
    return device


@with_db_session
def delete_device(device_id: int) -> None:
    """
    Delete a device by its ID. Also cascades to metrics.
    """
    db: Session = current_session()
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise ValueError(f'Device with id {device_id} not found')
    db.delete(device)
    # commit happens automatically
    return None
