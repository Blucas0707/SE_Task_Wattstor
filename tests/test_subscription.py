import pytest
from sqlalchemy.orm import Session

from app.models.subscription import Subscription
from app.models.metric import Metric
from app.models.device import Device
from app.models.user import User, UserRole
from app.core.database import Base, engine
from app.core.auth import get_password_hash


# Test data
TEST_USER = {
    'username': 'testuser',
    'email': 'test@example.com',
    'hashed_password': get_password_hash('testpass'),
    'role': UserRole.STANDARD,
}

TEST_DEVICE = {'name': 'Test Device', 'site_id': 1, 'type': 'sensor'}

TEST_METRIC = {'name': 'Temperature', 'unit': '°C', 'device_id': 1, 'value': 25.0}

TEST_SUBSCRIPTION = {'name': 'Test Subscription', 'metric_ids': [1]}


@pytest.fixture(scope='function')
def db_session():
    """Create a test database session"""
    Base.metadata.create_all(bind=engine)
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope='function')
def test_user(db_session: Session):
    """Create a test user"""
    user = User(**TEST_USER)
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture(scope='function')
def test_device(db_session: Session):
    """Create a test device"""
    device = Device(**TEST_DEVICE)
    db_session.add(device)
    db_session.commit()
    return device


@pytest.fixture(scope='function')
def test_metric(db_session: Session, test_device: Device):
    """Create a test metric"""
    metric = Metric(**TEST_METRIC)
    db_session.add(metric)
    db_session.commit()
    return metric


@pytest.fixture(scope='function')
def test_subscription(db_session: Session, test_user: User, test_metric: Metric):
    """Create a test subscription"""
    sub = Subscription(name=TEST_SUBSCRIPTION['name'], user_id=test_user.id)
    sub.metrics = [test_metric]
    db_session.add(sub)
    db_session.commit()
    return sub


def test_create_subscription(test_user: User, test_metric: Metric):
    """Test creating a subscription"""
    # Login to get token
    response = client.post(
        '/auth/token', data={'username': test_user.username, 'password': 'testpass'}
    )
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # Create subscription
    response = client.post('/subscriptions', json=TEST_SUBSCRIPTION, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data['name'] == TEST_SUBSCRIPTION['name']
    assert len(data['metric_ids']) == len(TEST_SUBSCRIPTION['metric_ids'])


def test_get_subscription(test_subscription: Subscription, test_user: User):
    """Test retrieving a subscription"""
    # Login to get token
    response = client.post(
        '/auth/token', data={'username': test_user.username, 'password': 'testpass'}
    )
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # Retrieve subscription
    response = client.get(f'/subscriptions/{test_subscription.id}', headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == test_subscription.id
    assert data['name'] == test_subscription.name


def test_get_subscription_history(test_subscription: Subscription, test_user: User):
    """Test retrieving subscription history data"""
    # Login to get token
    response = client.post(
        '/auth/token', data={'username': test_user.username, 'password': 'testpass'}
    )
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # Retrieve historical data
    response = client.get(
        f'/subscriptions/{test_subscription.id}/history', headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data['subscription_id'] == test_subscription.id
    assert len(data['metrics']) > 0
    assert 'timestamps' in data['metrics'][0]
    assert 'values' in data['metrics'][0]


def test_unauthorized_access(test_subscription: Subscription):
    """Test unauthorized access"""
    # Access without token
    response = client.get(f'/subscriptions/{test_subscription.id}')
    assert response.status_code == 401


def test_wrong_user_access(test_subscription: Subscription):
    """Test wrong user access"""
    # Create another user
    other_user = {
        'username': 'otheruser',
        'email': 'other@example.com',
        'hashed_password': get_password_hash('otherpass'),
        'role': 'standard',  # Use string instead of enum
    }
    response = client.post('/auth/register', json=other_user)
    assert response.status_code == 200

    # Login with new user
    response = client.post(
        '/auth/token', data={'username': 'otheruser', 'password': 'otherpass'}
    )
    assert response.status_code == 200
    token = response.json()['access_token']

    # Try to access a subscription not belonging to this user
    response = client.get(
        f'/subscriptions/{test_subscription.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == 403
