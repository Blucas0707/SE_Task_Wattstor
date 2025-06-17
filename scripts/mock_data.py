import random
from datetime import datetime, timedelta

# 載入我們的 Session 管理器與 ORM model
from app.core.db_session import get_db_session
from app.models.site import Site
from app.models.device import Device
from app.models.metric import Metric
from app.models.subscription import Subscription

# 常用的指標名稱與單位範例
METRIC_TYPES = [
    ('power', 'kW'),
    ('energy', 'kWh'),
    ('temperature', '°C'),
    ('voltage', 'V'),
]


def generate_mock_data():
    """
    Generate mock Sites, Devices, Metrics and Subscriptions.
    """
    with get_db_session() as db:
        # 1. 建立 3 個 Site
        sites = []
        for i in range(1, 4):
            site = Site(name=f'Site_{i}')
            db.add(site)
            db.flush()  # 取得 site.id
            sites.append(site)

            # 2. 每個 Site 下建立 2 台 Device
            for j in range(1, 3):
                device = Device(
                    name=f'Device_{i}_{j}',
                    site_id=site.id,
                )
                db.add(device)
                db.flush()  # 取得 device.id

                # 3. 每台 Device 建立 20 筆 Metric（過去 20 分鐘每分鐘一筆）
                for k in range(20):
                    metric_name, unit = random.choice(METRIC_TYPES)
                    metric = Metric(
                        device_id=device.id,
                        name=metric_name,
                        unit=unit,
                        # timestamp 往回推 k 分鐘
                        timestamp=datetime.utcnow() - timedelta(minutes=k),
                        # 隨機值，0~100
                        value=round(random.uniform(0, 100), 2),
                    )
                    db.add(metric)

        # 4. 建立 2 個 Subscription，隨機訂閱部分 Metrics
        all_metrics = db.query(Metric).all()
        for s_idx in range(1, 3):
            sub = Subscription(name=f'Sub_{s_idx}')
            # 隨機挑 5 筆 metric 加入 subscription
            sub.metrics = random.sample(all_metrics, k=5)
            db.add(sub)

        # 以上新增完畢，commit 會在 context manager 裡自動執行


if __name__ == '__main__':
    print('Generating mock data...')
    generate_mock_data()
    print('Done.')
