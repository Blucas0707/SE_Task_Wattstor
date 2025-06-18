from contextvars import ContextVar
from contextlib import contextmanager
from sqlalchemy.orm import Session
from .database import SessionLocal

# ContextVar to hold the current session
_session_ctx: ContextVar[Session | None] = ContextVar('_session_ctx', default=None)


@contextmanager
def get_db_session():
    """
    Context manager that provides a DB session,
    stores it in ContextVar, and ensures it's closed.
    """
    session = SessionLocal()
    token = _session_ctx.set(session)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
        _session_ctx.reset(token)


def current_session() -> Session:
    """
    Retrieve the current session from ContextVar.
    Raises if none is set.
    """
    session = _session_ctx.get()
    if session is None:
        raise RuntimeError('No active DB session found')
    return session


def with_db_session(func):
    """
    Decorator to wrap a function so that it runs within
    get_db_session context. The function itself need not
    accept a db parameter.
    """

    def wrapper(*args, **kwargs):
        with get_db_session():
            return func(*args, **kwargs)

    return wrapper


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
