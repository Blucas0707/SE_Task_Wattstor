import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.subscription import Subscription
from app.models.metric import Metric
from app.models.device import Device
from app.models.user import User, UserRole
from app.core.database import Base, engine
from app.core.auth import get_password_hash

# 創建測試客戶端
client = TestClient(app)

# 測試數據
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "hashed_password": get_password_hash("testpass"),
    "role": UserRole.STANDARD
}

TEST_DEVICE = {
    "name": "Test Device",
    "site_id": 1,
    "type": "sensor"
}

TEST_METRIC = {
    "name": "Temperature",
    "unit": "°C",
    "device_id": 1,
    "value": 25.0
}

TEST_SUBSCRIPTION = {
    "name": "Test Subscription",
    "metric_ids": [1]
}

@pytest.fixture(scope="function")
def db_session():
    """創建測試數據庫會話"""
    Base.metadata.create_all(bind=engine)
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_user(db_session: Session):
    """創建測試用戶"""
    user = User(**TEST_USER)
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture(scope="function")
def test_device(db_session: Session):
    """創建測試設備"""
    device = Device(**TEST_DEVICE)
    db_session.add(device)
    db_session.commit()
    return device

@pytest.fixture(scope="function")
def test_metric(db_session: Session, test_device: Device):
    """創建測試指標"""
    metric = Metric(**TEST_METRIC)
    db_session.add(metric)
    db_session.commit()
    return metric

@pytest.fixture(scope="function")
def test_subscription(db_session: Session, test_user: User, test_metric: Metric):
    """創建測試訂閱"""
    sub = Subscription(
        name=TEST_SUBSCRIPTION["name"],
        user_id=test_user.id
    )
    sub.metrics = [test_metric]
    db_session.add(sub)
    db_session.commit()
    return sub

def test_create_subscription(test_user: User, test_metric: Metric):
    """測試創建訂閱"""
    # 登錄獲取 token
    response = client.post(
        "/auth/token",
        data={"username": test_user.username, "password": "testpass"}
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 創建訂閱
    response = client.post(
        "/subscriptions",
        json=TEST_SUBSCRIPTION,
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == TEST_SUBSCRIPTION["name"]
    assert len(data["metric_ids"]) == len(TEST_SUBSCRIPTION["metric_ids"])

def test_get_subscription(test_subscription: Subscription, test_user: User):
    """測試獲取訂閱"""
    # 登錄獲取 token
    response = client.post(
        "/auth/token",
        data={"username": test_user.username, "password": "testpass"}
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 獲取訂閱
    response = client.get(
        f"/subscriptions/{test_subscription.id}",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_subscription.id
    assert data["name"] == test_subscription.name

def test_get_subscription_history(test_subscription: Subscription, test_user: User):
    """測試獲取訂閱歷史數據"""
    # 登錄獲取 token
    response = client.post(
        "/auth/token",
        data={"username": test_user.username, "password": "testpass"}
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 獲取歷史數據
    response = client.get(
        f"/subscriptions/{test_subscription.id}/history",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["subscription_id"] == test_subscription.id
    assert len(data["metrics"]) > 0
    assert "timestamps" in data["metrics"][0]
    assert "values" in data["metrics"][0]

def test_unauthorized_access(test_subscription: Subscription):
    """測試未授權訪問"""
    # 不帶 token 訪問
    response = client.get(f"/subscriptions/{test_subscription.id}")
    assert response.status_code == 401

def test_wrong_user_access(test_subscription: Subscription):
    """測試錯誤用戶訪問"""
    # 創建另一個用戶
    other_user = {
        "username": "otheruser",
        "email": "other@example.com",
        "hashed_password": get_password_hash("otherpass"),
        "role": "standard"  # 使用字符串而不是枚舉
    }
    response = client.post("/auth/register", json=other_user)
    assert response.status_code == 200

    # 使用新用戶登錄
    response = client.post(
        "/auth/token",
        data={"username": "otheruser", "password": "otherpass"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    # 嘗試訪問不屬於該用戶的訂閱
    response = client.get(
        f"/subscriptions/{test_subscription.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
