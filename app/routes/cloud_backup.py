import re
from datetime import datetime
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import User, BackupProvider
from app.auth.jwt_handler import get_current_admin_user
from app.utils.encryption import encrypt, decrypt
from app.utils import rclone

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

_SAFE_NAME_RE = re.compile(r'^[a-zA-Z0-9._/\-]{1,512}$')

S3_PRESETS = {
    "backblaze_b2": {
        "label": "Backblaze B2",
        "endpoint": "https://s3.us-west-002.backblazeb2.com",
        "region": "",
    },
    "aws_s3": {
        "label": "AWS S3",
        "endpoint": "https://s3.amazonaws.com",
        "region": "us-east-1",
    },
    "cloudflare_r2": {
        "label": "Cloudflare R2",
        "endpoint": "",
        "region": "auto",
    },
    "minio": {
        "label": "MinIO (self-hosted)",
        "endpoint": "",
        "region": "",
    },
    "other": {
        "label": "Other S3-Compatible",
        "endpoint": "",
        "region": "",
    },
}


@router.get("/cloud-backup", response_class=HTMLResponse)
async def cloud_backup_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    providers = db.query(BackupProvider).order_by(BackupProvider.created_at).all()
    return templates.TemplateResponse(
        "cloud_backup/index.html",
        {
            "request": request,
            "current_user": current_user,
            "providers": providers,
            "presets": S3_PRESETS,
        }
    )


@router.post("/cloud-backup/providers/create")
async def create_provider(
    request: Request,
    name: str = Form(...),
    endpoint: str = Form(...),
    bucket_name: str = Form(...),
    region: Optional[str] = Form(None),
    path_prefix: str = Form("db-backups/"),
    access_key: str = Form(...),
    secret_key: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    name = name.strip()
    endpoint = endpoint.strip()
    bucket_name = bucket_name.strip()
    region = region.strip() if region else None
    path_prefix = path_prefix.strip().rstrip("/") + "/"

    if not _SAFE_NAME_RE.match(bucket_name):
        raise HTTPException(status_code=400, detail="Invalid bucket name")
    if not _SAFE_NAME_RE.match(path_prefix):
        raise HTTPException(status_code=400, detail="Invalid path prefix")

    provider = BackupProvider(
        name=name,
        provider_type="s3",
        access_key_enc=encrypt(access_key),
        secret_key_enc=encrypt(secret_key),
        endpoint=endpoint,
        bucket_name=bucket_name,
        region=region or None,
        path_prefix=path_prefix,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(provider)
    db.commit()
    return RedirectResponse(url="/cloud-backup?created=true", status_code=302)


@router.get("/cloud-backup/providers/{provider_id}", response_class=HTMLResponse)
async def edit_provider_page(
    provider_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    provider = db.query(BackupProvider).filter(BackupProvider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return templates.TemplateResponse(
        "cloud_backup/edit.html",
        {
            "request": request,
            "current_user": current_user,
            "provider": provider,
            "presets": S3_PRESETS,
        }
    )


@router.post("/cloud-backup/providers/{provider_id}/update")
async def update_provider(
    provider_id: int,
    name: str = Form(...),
    endpoint: str = Form(...),
    bucket_name: str = Form(...),
    region: Optional[str] = Form(None),
    path_prefix: str = Form("db-backups/"),
    access_key: Optional[str] = Form(None),
    secret_key: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    provider = db.query(BackupProvider).filter(BackupProvider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    bucket_name = bucket_name.strip()
    path_prefix = path_prefix.strip().rstrip("/") + "/"

    if not _SAFE_NAME_RE.match(bucket_name):
        raise HTTPException(status_code=400, detail="Invalid bucket name")
    if not _SAFE_NAME_RE.match(path_prefix):
        raise HTTPException(status_code=400, detail="Invalid path prefix")

    provider.name = name.strip()
    provider.endpoint = endpoint.strip()
    provider.bucket_name = bucket_name
    provider.region = region.strip() if region and region.strip() else None
    provider.path_prefix = path_prefix
    provider.updated_at = datetime.utcnow()

    if access_key and access_key.strip():
        provider.access_key_enc = encrypt(access_key.strip())
    if secret_key and secret_key.strip():
        provider.secret_key_enc = encrypt(secret_key.strip())

    db.commit()
    return RedirectResponse(url="/cloud-backup?updated=true", status_code=302)


@router.post("/cloud-backup/providers/{provider_id}/delete")
async def delete_provider(
    provider_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    provider = db.query(BackupProvider).filter(BackupProvider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    db.delete(provider)
    db.commit()
    return RedirectResponse(url="/cloud-backup?deleted=true", status_code=302)


@router.post("/cloud-backup/providers/{provider_id}/toggle")
async def toggle_provider(
    provider_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    provider = db.query(BackupProvider).filter(BackupProvider.id == provider_id).first()
    if not provider:
        return JSONResponse(status_code=404, content={"success": False, "message": "Provider not found"})
    provider.is_active = not provider.is_active
    provider.updated_at = datetime.utcnow()
    db.commit()
    return JSONResponse(content={"success": True, "is_active": provider.is_active})


@router.post("/cloud-backup/providers/test")
async def test_connection(
    request: Request,
    endpoint: str = Form(...),
    access_key: str = Form(...),
    secret_key: str = Form(...),
    region: Optional[str] = Form(None),
    current_user: User = Depends(get_current_admin_user)
):
    """Test credentials against endpoint without saving anything."""
    from app.utils.encryption import encrypt

    class _TempProvider:
        access_key_enc = encrypt(access_key)
        secret_key_enc = encrypt(secret_key)
        bucket_name = ""

    _TempProvider.endpoint = endpoint.strip()
    _TempProvider.region = region.strip() if region and region.strip() else None

    result = rclone.test_connection(_TempProvider)
    return JSONResponse(content=result)


@router.post("/cloud-backup/providers/{provider_id}/test-connection")
async def test_saved_connection(
    provider_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    provider = db.query(BackupProvider).filter(BackupProvider.id == provider_id).first()
    if not provider:
        return JSONResponse(status_code=404, content={"success": False, "message": "Provider not found"})
    result = rclone.test_connection(provider)
    return JSONResponse(content=result)


@router.post("/cloud-backup/providers/{provider_id}/verify-bucket")
async def verify_bucket(
    provider_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    provider = db.query(BackupProvider).filter(BackupProvider.id == provider_id).first()
    if not provider:
        return JSONResponse(status_code=404, content={"success": False, "message": "Provider not found"})
    result = rclone.verify_bucket(provider)
    return JSONResponse(content=result)


@router.post("/cloud-backup/providers/{provider_id}/create-bucket")
async def create_bucket(
    provider_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    provider = db.query(BackupProvider).filter(BackupProvider.id == provider_id).first()
    if not provider:
        return JSONResponse(status_code=404, content={"success": False, "message": "Provider not found"})
    result = rclone.create_bucket(provider)
    return JSONResponse(content=result)


@router.post("/cloud-backup/providers/{provider_id}/run-backup")
async def run_backup(
    provider_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    provider = db.query(BackupProvider).filter(BackupProvider.id == provider_id).first()
    if not provider:
        return JSONResponse(status_code=404, content={"success": False, "message": "Provider not found"})
    if not provider.is_active:
        return JSONResponse(status_code=400, content={"success": False, "message": "Provider is inactive"})
    result = rclone.run_backup(provider)
    return JSONResponse(content=result)
