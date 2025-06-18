from fastapi import APIRouter, HTTPException
from app.schemas.site import Site
from app.services import site_service

router = APIRouter(prefix='/sites', tags=['Sites'])


@router.get('/', response_model=list[Site])
def read_sites():
    """R1: List all sites."""
    sites = site_service.list_sites()
    return sites


@router.get('/{site_id}', response_model=Site)
def read_site(site_id: int):
    """R1: Get site by ID."""
    site = site_service.get_site(site_id)
    if not site:
        raise HTTPException(status_code=404, detail='Site not found')
    return site
