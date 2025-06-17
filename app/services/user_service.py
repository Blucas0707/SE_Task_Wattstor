from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.auth import get_password_hash, verify_password
from app.core.db_session import with_db_session, current_session


@with_db_session
def get_user_by_username(username: str) -> User | None:
    """Get user by username"""
    return current_session().query(User).filter(User.username == username).first()


@with_db_session
def get_user_by_email(email: str) -> User | None:
    """Get user by email"""
    return current_session().query(User).filter(User.email == email).first()


@with_db_session
def create_user(user_in: UserCreate) -> User:
    """Create new user"""
    db = current_session()
    # Check if username exists
    if get_user_by_username(user_in.username):
        raise ValueError("Username already registered")
    # Check if email exists
    if get_user_by_email(user_in.email):
        raise ValueError("Email already registered")

    # Create new user
    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@with_db_session
def update_user(user_id: int, user_in: UserUpdate) -> User:
    """Update user information"""
    db = current_session()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User not found")

    # Update fields if provided
    if user_in.username is not None:
        existing_user = get_user_by_username(user_in.username)
        if existing_user and existing_user.id != user_id:
            raise ValueError("Username already taken")
        user.username = user_in.username

    if user_in.email is not None:
        existing_user = get_user_by_email(user_in.email)
        if existing_user and existing_user.id != user_id:
            raise ValueError("Email already taken")
        user.email = user_in.email

    if user_in.password is not None:
        user.hashed_password = get_password_hash(user_in.password)

    if user_in.role is not None:
        user.role = user_in.role

    if user_in.is_active is not None:
        user.is_active = user_in.is_active

    db.commit()
    db.refresh(user)
    return user


@with_db_session
def authenticate_user(username: str, password: str) -> User | None:
    """Authenticate user with username and password"""
    user = get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
