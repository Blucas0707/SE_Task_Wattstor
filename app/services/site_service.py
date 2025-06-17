from sqlalchemy.orm import Session
from app.models.site import Site
from app.schemas.site import SiteCreate
from app.core.db_session import with_db_session, current_session


@with_db_session
def list_sites() -> list[Site]:
    """
    Return all sites.
    Automatically uses session from ContextVar.
    """
    db: Session = current_session()
    return db.query(Site).all()


@with_db_session
def get_site(site_id: int) -> Site | None:
    """
    Get a single site by ID.
    """
    db: Session = current_session()
    return db.query(Site).filter(Site.id == site_id).first()


@with_db_session
def create_site(site_in: SiteCreate) -> Site:
    """
    Create a new site from Pydantic schema.
    """
    db: Session = current_session()
    site = Site(**site_in.model_dump())
    db.add(site)
    # commit happens after function returns
    db.refresh(site)
    return site
