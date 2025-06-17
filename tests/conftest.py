import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# 添加項目根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import Base
from app.main import app
from app.core.db_session import get_db
from app.models.user import User, UserRole
from app.models.device import Device
from app.models.metric import Metric
from app.models.subscription import Subscription
from app.services.user_service import get_password_hash

# 使用 SQLite 內存數據庫進行測試
TEST_DATABASE_URL = 'sqlite:///:memory:'


@pytest.fixture(scope='session')
def engine():
    """創建測試數據庫引擎"""
    engine = create_engine(TEST_DATABASE_URL, connect_args={'check_same_thread': False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    if os.path.exists('./test.db'):
        os.remove('./test.db')


@pytest.fixture(scope='function')
def db_session(engine):
    """創建數據庫會話"""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        expire_on_commit=False,
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope='function')
def client(db_session):
    """創建測試客戶端"""

    def override_get_db():
        # 只 yield，不關閉，由外層 fixture 管理生/死週期
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope='function')
def test_user(db_session):
    """創建測試用戶"""
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
    """創建測試技術員"""
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
    """創建測試設備"""
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
    """創建測試指標"""
    metric = Metric(name='Test Metric', unit='kW', device_id=test_device.id)
    db_session.add(metric)
    db_session.commit()
    db_session.refresh(metric)
    return metric


@pytest.fixture(scope='function')
def test_subscription(db_session, test_user, test_metric):
    """創建測試訂閱"""
    subscription = Subscription(
        name='Test Subscription', user_id=test_user.id, metrics=[test_metric]
    )
    db_session.add(subscription)
    db_session.commit()
    db_session.refresh(subscription)
    return subscription
