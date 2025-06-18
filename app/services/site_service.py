from sqlalchemy.orm import Session, selectinload

from app.core.db_session import with_db_session, current_session
from app.models.site import Site
from app.schemas.site import Site as SiteSchema, SiteCreate


@with_db_session
def list_sites() -> list[SiteSchema]:
    """
    Return all sites.
    Automatically uses session from ContextVar.
    """
    db: Session = current_session()
    sites = db.query(Site).options(selectinload(Site.devices)).all()
    return [SiteSchema.model_validate(site) for site in sites]


@with_db_session
def get_site(site_id: int) -> SiteSchema | None:
    """
    Get a single site by ID.
    """
    db: Session = current_session()
    site = db.query(Site).filter(Site.id == site_id).first()
    return SiteSchema.model_validate(site)


@with_db_session
def create_site(site_in: SiteCreate) -> SiteSchema:
    """
    Create a new site from Pydantic schema.
    """
    db: Session = current_session()
    site = Site(**site_in.model_dump())
    db.add(site)
    # commit happens after function returns
    db.refresh(site)
    return SiteSchema.model_validate(site)
