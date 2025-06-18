import pytest


def test_login_success(client, test_user):
    response = client.post(
        '/auth/token', data={'username': test_user.username, 'password': 'testpass'}
    )
    assert response.status_code == 200
    data = response.json()
    assert 'access_token' in data
    assert data['token_type'] == 'bearer'


def test_login_wrong_password(client, test_user):
    response = client.post(
        '/auth/token', data={'username': test_user.username, 'password': 'wrongpass'}
    )
    assert response.status_code == 401
    assert 'Incorrect username or password' in response.json()['detail']


def test_login_nonexistent_user(client):
    response = client.post(
        '/auth/token', data={'username': 'nonexistent', 'password': 'testpass'}
    )
    assert response.status_code == 401
    assert 'Incorrect username or password' in response.json()['detail']


def test_register_user(client, test_admin):
    # Admin login
    response = client.post(
        '/auth/token', data={'username': test_admin.username, 'password': 'adminpass'}
    )
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # Register new user
    new_user = {
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'newpass',
        'role': 'standard',
    }
    response = client.post('/auth/register', json=new_user, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data['username'] == new_user['username']
    assert data['email'] == new_user['email']
    assert 'id' in data


def test_register_duplicate_username(client, test_user, test_admin):
    # Admin login
    response = client.post(
        '/auth/token', data={'username': test_admin.username, 'password': 'adminpass'}
    )
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # Try to register duplicate username
    new_user = {
        'username': test_user.username,
        'email': 'different@example.com',
        'password': 'newpass',
        'role': 'standard',
    }
    response = client.post('/auth/register', json=new_user, headers=headers)
    assert response.status_code == 400
    assert 'Username already registered' in response.json()['detail']


def test_get_current_user(client, test_user):
    # Login
    response = client.post(
        '/auth/token', data={'username': test_user.username, 'password': 'testpass'}
    )
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # Get user info
    response = client.get('/auth/me', headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data['username'] == test_user.username
    assert data['email'] == test_user.email
    assert data['role'] == 'standard'


def test_unauthorized_access(client):
    response = client.get('/auth/me')
    assert response.status_code == 401
    assert 'Not authenticated' in response.json()['detail']


def test_invalid_token(client):
    headers = {'Authorization': 'Bearer invalid_token'}
    response = client.get('/auth/me', headers=headers)
    assert response.status_code == 401
    assert 'Could not validate credentials' in response.json()['detail']


def test_standard_user_register_attempt(client, test_user):
    # Standard user login
    response = client.post(
        '/auth/token', data={'username': test_user.username, 'password': 'testpass'}
    )
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # Try to register new user
    new_user = {
        'username': 'newuser2',
        'email': 'new2@example.com',
        'password': 'newpass',
        'role': 'standard',
    }
    response = client.post('/auth/register', json=new_user, headers=headers)
    assert response.status_code == 403
    assert 'Not enough permissions' in response.json()['detail']
