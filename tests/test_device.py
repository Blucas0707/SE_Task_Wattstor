import pytest

from sqlalchemy.orm import Session

from app.models.device import Device
from app.models.user import User, UserRole
from app.models.site import Site
from app.core.database import Base, engine
from app.core.auth import get_password_hash

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
    Base.metadata.create_all(bind=engine)
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope='function')
def test_user(db_session: Session):
    user = User(**TEST_USER)
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture(scope='function')
def test_technician(db_session: Session):
    tech = User(**TEST_TECHNICIAN)
    db_session.add(tech)
    db_session.commit()
    return tech


@pytest.fixture(scope='function')
def test_site(db_session: Session):
    """Create a test site"""
    site = Site(**TEST_SITE)
    db_session.add(site)
    db_session.commit()
    return site


@pytest.fixture(scope='function')
def test_device(db_session: Session, test_site: Site):
    device = Device(**TEST_DEVICE)
    db_session.add(device)
    db_session.commit()
    return device


@pytest.mark.device
@pytest.mark.integration
def test_create_device(test_technician: User, test_site: Site):
    # Technician login
    response = client.post(
        '/auth/token',
        data={'username': test_technician.username, 'password': 'techpass'},
    )
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # Create device
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
    # Standard user login
    response = client.post(
        '/auth/token', data={'username': test_user.username, 'password': 'testpass'}
    )
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # Try to create device
    new_device = {'name': 'New Device', 'type': 'sensor', 'site_id': test_site.id}
    response = client.post('/devices', json=new_device, headers=headers)
    assert response.status_code == 403
    assert 'Not enough permissions' in response.json()['detail']


@pytest.mark.device
@pytest.mark.integration
def test_get_device(test_device: Device, test_user: User):
    # User login
    response = client.post(
        '/auth/token', data={'username': test_user.username, 'password': 'testpass'}
    )
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # Get device information
    response = client.get(f'/devices/{test_device.id}', headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == test_device.id
    assert data['name'] == test_device.name
    assert data['type'] == test_device.type


@pytest.mark.device
@pytest.mark.integration
def test_update_device(test_device: Device, test_technician: User):
    # Technician login
    response = client.post(
        '/auth/token',
        data={'username': test_technician.username, 'password': 'techpass'},
    )
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # Update device
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
    # Technician login
    response = client.post(
        '/auth/token',
        data={'username': test_technician.username, 'password': 'techpass'},
    )
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # Delete device
    response = client.delete(f'/devices/{test_device.id}', headers=headers)
    assert response.status_code == 204

    # Confirm device is deleted
    response = client.get(f'/devices/{test_device.id}', headers=headers)
    assert response.status_code == 404


@pytest.mark.device
@pytest.mark.integration
def test_list_devices(test_user: User):
    # User login
    response = client.post(
        '/auth/token', data={'username': test_user.username, 'password': 'testpass'}
    )
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # Get device list
    response = client.get('/devices', headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.device
@pytest.mark.integration
def test_device_metrics(test_device: Device, test_user: User):
    # User login
    response = client.post(
        '/auth/token', data={'username': test_user.username, 'password': 'testpass'}
    )
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # Get device metrics
    response = client.get(f'/devices/{test_device.id}/metrics', headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0  # Each device has at least one metric
