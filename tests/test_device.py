import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.device import Device
from app.models.user import User, UserRole
from app.models.site import Site
from app.core.database import Base, engine
from app.core.auth import get_password_hash

# 創建測試客戶端
client = TestClient(app)

# 測試數據
TEST_USER = {
    'username': 'testuser',
    'email': 'test@example.com',
    'hashed_password': get_password_hash('testpass'),
    'role': UserRole.STANDARD,
}

TEST_TECHNICIAN = {
    'username': 'technician',
    'email': 'tech@example.com',
    'hashed_password': get_password_hash('techpass'),
    'role': UserRole.TECHNICIAN,
}

TEST_SITE = {'name': 'Test Site', 'location': 'Test Location'}

TEST_DEVICE = {'name': 'Test Device', 'type': 'sensor', 'site_id': 1}


@pytest.fixture(scope='function')
def db_session():
    """創建測試數據庫會話"""
    Base.metadata.create_all(bind=engine)
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope='function')
def test_user(db_session: Session):
    """創建測試用戶"""
    user = User(**TEST_USER)
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture(scope='function')
def test_technician(db_session: Session):
    """創建測試技術員"""
    tech = User(**TEST_TECHNICIAN)
    db_session.add(tech)
    db_session.commit()
    return tech


@pytest.fixture(scope='function')
def test_site(db_session: Session):
    """創建測試站點"""
    site = Site(**TEST_SITE)
    db_session.add(site)
    db_session.commit()
    return site


@pytest.fixture(scope='function')
def test_device(db_session: Session, test_site: Site):
    """創建測試設備"""
    device = Device(**TEST_DEVICE)
    db_session.add(device)
    db_session.commit()
    return device


@pytest.mark.device
@pytest.mark.integration
def test_create_device(test_technician: User, test_site: Site):
    """測試創建設備"""
    # 技術員登錄
    response = client.post(
        '/auth/token',
        data={'username': test_technician.username, 'password': 'techpass'},
    )
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # 創建設備
    new_device = {'name': 'New Device', 'type': 'sensor', 'site_id': test_site.id}
    response = client.post('/devices', json=new_device, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data['name'] == new_device['name']
    assert data['type'] == new_device['type']
    assert data['site_id'] == new_device['site_id']


@pytest.mark.device
@pytest.mark.integration
def test_create_device_unauthorized(test_user: User, test_site: Site):
    """測試未授權創建設備"""
    # 普通用戶登錄
    response = client.post(
        '/auth/token', data={'username': test_user.username, 'password': 'testpass'}
    )
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # 嘗試創建設備
    new_device = {'name': 'New Device', 'type': 'sensor', 'site_id': test_site.id}
    response = client.post('/devices', json=new_device, headers=headers)
    assert response.status_code == 403
    assert 'Not enough permissions' in response.json()['detail']


@pytest.mark.device
@pytest.mark.integration
def test_get_device(test_device: Device, test_user: User):
    """測試獲取設備信息"""
    # 用戶登錄
    response = client.post(
        '/auth/token', data={'username': test_user.username, 'password': 'testpass'}
    )
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # 獲取設備信息
    response = client.get(f'/devices/{test_device.id}', headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == test_device.id
    assert data['name'] == test_device.name
    assert data['type'] == test_device.type


@pytest.mark.device
@pytest.mark.integration
def test_update_device(test_device: Device, test_technician: User):
    """測試更新設備"""
    # 技術員登錄
    response = client.post(
        '/auth/token',
        data={'username': test_technician.username, 'password': 'techpass'},
    )
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # 更新設備
    update_data = {'name': 'Updated Device', 'type': 'controller'}
    response = client.put(
        f'/devices/{test_device.id}', json=update_data, headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == update_data['name']
    assert data['type'] == update_data['type']


@pytest.mark.device
@pytest.mark.integration
def test_delete_device(test_device: Device, test_technician: User):
    """測試刪除設備"""
    # 技術員登錄
    response = client.post(
        '/auth/token',
        data={'username': test_technician.username, 'password': 'techpass'},
    )
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # 刪除設備
    response = client.delete(f'/devices/{test_device.id}', headers=headers)
    assert response.status_code == 204

    # 確認設備已刪除
    response = client.get(f'/devices/{test_device.id}', headers=headers)
    assert response.status_code == 404


@pytest.mark.device
@pytest.mark.integration
def test_list_devices(test_user: User):
    """測試列出設備"""
    # 用戶登錄
    response = client.post(
        '/auth/token', data={'username': test_user.username, 'password': 'testpass'}
    )
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # 獲取設備列表
    response = client.get('/devices', headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.device
@pytest.mark.integration
def test_device_metrics(test_device: Device, test_user: User):
    """測試設備指標"""
    # 用戶登錄
    response = client.post(
        '/auth/token', data={'username': test_user.username, 'password': 'testpass'}
    )
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # 獲取設備指標
    response = client.get(f'/devices/{test_device.id}/metrics', headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0  # 每個設備至少有一個指標
