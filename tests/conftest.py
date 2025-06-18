import os
import sys
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.core.db_session import get_db
from app.main import app
from app.models.user import User, UserRole
from app.models.device import Device
from app.models.metric import Metric
from app.models.user_site import user_site
from app.models.site import Site
from app.models.subscription import Subscription
from app.services.user_service import get_password_hash
from settings import DATABASE_URL


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TEST_DATABASE_URL = DATABASE_URL


@pytest.fixture(scope='session')
def engine():
    """Create DB Engine for Testing"""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    print(f'{Base.metadata.tables=}')
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope='function')
def db_session(engine):
    """Create DB Session"""
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope='function')
def client(db_session):
    """Create Client for testing"""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope='function')
def test_user(db_session):
    user = User(
        username='testuser',
        email='test@example.com',
        hashed_password=get_password_hash('testpass'),
        role=UserRole.STANDARD,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope='function')
def test_technician(db_session):
    technician = User(
        username='technician',
        email='tech@example.com',
        hashed_password=get_password_hash('techpass'),
        role=UserRole.TECHNICIAN,
    )
    db_session.add(technician)
    db_session.commit()
    db_session.refresh(technician)
    return technician


@pytest.fixture(scope='function')
def test_device(db_session, test_technician):
    device = Device(
        name='Test Device',
        device_type='sensor',
        location='Test Location',
        status='active',
        created_by=test_technician.id,
    )
    db_session.add(device)
    db_session.commit()
    db_session.refresh(device)
    return device


@pytest.fixture(scope='function')
def test_metric(db_session, test_device):
    metric = Metric(name='Test Metric', unit='kW', device_id=test_device.id)
    db_session.add(metric)
    db_session.commit()
    db_session.refresh(metric)
    return metric


@pytest.fixture(scope='function')
def test_subscription(db_session, test_user, test_metric):
    subscription = Subscription(
        name='Test Subscription', user_id=test_user.id, metrics=[test_metric]
    )
    db_session.add(subscription)
    db_session.commit()
    db_session.refresh(subscription)
    return subscription
