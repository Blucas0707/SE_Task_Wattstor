# app/services/mock_data.py
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.site import Site
from app.models.device import Device
from app.models.metric import Metric
from app.models.subscription import Subscription
from app.services.user_service import get_password_hash


def init_user_mock_data(db: Session) -> None:
    # 建立 standard user
    if not db.query(User).filter_by(username='standard_user').first():
        user = User(
            username='standard_user',
            email='standard@example.com',
            hashed_password=get_password_hash('standardpass'),
            role=UserRole.STANDARD,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    # 建立 technician user
    if not db.query(User).filter_by(username='technician_user').first():
        user = User(
            username='technician_user',
            email='tech@example.com',
            hashed_password=get_password_hash('techpass'),
            role=UserRole.TECHNICIAN,
        )
        db.add(user)
        db.commit()
        db.refresh(user)


def init_site_mock_data(db: Session) -> None:
    # 建立 Site A, Site B
    if not db.query(Site).filter_by(name='Site A').first():
        site_a = Site(name='Site A', location='Location A')
        db.add(site_a)
        db.commit()
    if not db.query(Site).filter_by(name='Site B').first():
        site_b = Site(name='Site B', location='Location B')
        db.add(site_b)
        db.commit()


def init_device_mock_data(db: Session) -> None:
    # 取得 site
    site_a = db.query(Site).filter_by(name='Site A').first()
    site_b = db.query(Site).filter_by(name='Site B').first()
    # 建立 Device 1, Device 2
    if site_a and not db.query(Device).filter_by(name='Device 1').first():
        device1 = Device(name='Device 1', type='sensor', site_id=site_a.id)
        db.add(device1)
        db.commit()
    if site_b and not db.query(Device).filter_by(name='Device 2').first():
        device2 = Device(name='Device 2', type='sensor', site_id=site_b.id)
        db.add(device2)
        db.commit()


def init_metric_mock_data(db: Session) -> None:
    device1 = db.query(Device).filter_by(name='Device 1').first()
    device2 = db.query(Device).filter_by(name='Device 2').first()
    if (
        device1
        and not db.query(Metric)
        .filter_by(name='Metric 1', device_id=device1.id)
        .first()
    ):
        metric1 = Metric(name='Metric 1', unit='kW', device_id=device1.id, value=10.5)
        db.add(metric1)
        db.commit()
    if (
        device2
        and not db.query(Metric)
        .filter_by(name='Metric 2', device_id=device2.id)
        .first()
    ):
        metric2 = Metric(name='Metric 2', unit='kW', device_id=device2.id, value=20.5)
        db.add(metric2)
        db.commit()


def init_subscription_mock_data(db: Session) -> None:
    user = db.query(User).filter_by(username='standard_user').first()
    metric1 = db.query(Metric).filter_by(name='Metric 1').first()
    metric2 = db.query(Metric).filter_by(name='Metric 2').first()
    if (
        user
        and metric1
        and metric2
        and not db.query(Subscription).filter_by(name='Subscription 1').first()
    ):
        subscription = Subscription(
            name='Subscription 1', user_id=user.id, metrics=[metric1, metric2]
        )
        db.add(subscription)
        db.commit()


def init_mock_data(db: Session) -> None:
    init_user_mock_data(db)
    init_site_mock_data(db)
    init_device_mock_data(db)
    init_metric_mock_data(db)
    init_subscription_mock_data(db)
