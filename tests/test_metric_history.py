import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.metric import Metric
from app.models.device import Device
from app.core.database import Base, engine

# 創建測試客戶端
client = TestClient(app)

# 測試數據
TEST_DEVICE = {
    "name": "Test Device",
    "site_id": 1
}

TEST_METRIC = {
    "name": "Temperature",
    "unit": "°C",
    "device_id": 1,
    "value": 25.0
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

def test_get_metric_history_basic(test_metric: Metric):
    """測試基本的時間序列獲取功能"""
    response = client.get(f"/metrics/{test_metric.id}/history")
    assert response.status_code == 200
    data = response.json()

    # 驗證返回的數據結構
    assert data["metric_id"] == test_metric.id
    assert data["unit"] == test_metric.unit
    assert len(data["timestamps"]) > 0
    assert len(data["values"]) > 0
    assert len(data["timestamps"]) == len(data["values"])

def test_get_metric_history_custom_time_range(test_metric: Metric):
    """測試自定義時間範圍"""
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=2)

    response = client.get(
        f"/metrics/{test_metric.id}/history",
        params={
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "interval_minutes": 15
        }
    )

    assert response.status_code == 200
    data = response.json()

    # 驗證時間範圍
    timestamps = [datetime.fromisoformat(ts) for ts in data["timestamps"]]
    assert timestamps[0] >= start_time
    assert timestamps[-1] <= end_time

    # 驗證時間間隔
    for i in range(1, len(timestamps)):
        diff = timestamps[i] - timestamps[i-1]
        assert diff.total_seconds() == 15 * 60  # 15分鐘

def test_get_metric_history_invalid_time_range(test_metric: Metric):
    """測試無效的時間範圍"""
    end_time = datetime.now(timezone.utc)
    start_time = end_time + timedelta(hours=1)  # 開始時間在結束時間之後

    response = client.get(
        f"/metrics/{test_metric.id}/history",
        params={
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }
    )

    assert response.status_code == 400
    assert "start_time must be before end_time" in response.json()["detail"]

def test_get_metric_history_nonexistent_metric():
    """測試不存在的指標"""
    response = client.get("/metrics/999/history")
    assert response.status_code == 400
    assert "Metric with id 999 not found" in response.json()["detail"]

def test_get_metric_history_data_consistency(test_metric: Metric):
    """測試數據一致性"""
    # 獲取兩次歷史數據
    response1 = client.get(f"/metrics/{test_metric.id}/history")
    response2 = client.get(f"/metrics/{test_metric.id}/history")

    assert response1.status_code == 200
    assert response2.status_code == 200

    data1 = response1.json()
    data2 = response2.json()

    # 驗證兩次請求返回相同的數據
    assert data1["metric_id"] == data2["metric_id"]
    assert data1["unit"] == data2["unit"]
    assert len(data1["timestamps"]) == len(data2["timestamps"])
    assert len(data1["values"]) == len(data2["values"])

    # 驗證時間戳格式
    for timestamp in data1["timestamps"]:
        assert isinstance(timestamp, str)
        assert timestamp.endswith("Z")  # 確保是 UTC 時間

    # 驗證值的一致性
    for i in range(len(data1["values"])):
        assert abs(data1["values"][i] - data2["values"][i]) < 0.0001  # 允許小的浮點數誤差

def test_get_metric_history_different_intervals(test_metric: Metric):
    """測試不同的時間間隔"""
    intervals = [1, 5, 15, 30, 60]  # 不同的時間間隔（分鐘）

    for interval in intervals:
        response = client.get(
            f"/metrics/{test_metric.id}/history",
            params={"interval_minutes": interval}
        )

        assert response.status_code == 200
        data = response.json()

        # 驗證時間間隔
        timestamps = [datetime.fromisoformat(ts) for ts in data["timestamps"]]
        for i in range(1, len(timestamps)):
            diff = timestamps[i] - timestamps[i-1]
            assert diff.total_seconds() == interval * 60
