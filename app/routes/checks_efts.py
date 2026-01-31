from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from pydantic import BaseModel
from app.database import get_db
from app.models import User, CheckPayee, EFTCardNumber, EFTPayee, DailyBalanceCheck, DailyBalanceEFT
from app.auth.jwt_handler import get_current_user, get_current_user_from_cookie

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

class CheckPayeeCreate(BaseModel):
    name: str

class EFTCardNumberCreate(BaseModel):
    number: str

class EFTPayeeCreate(BaseModel):
    name: str

@router.get("/api/checks-efts/check-payees")
async def get_check_payees(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payees = db.query(CheckPayee).order_by(CheckPayee.name).all()
    return [{"id": p.id, "name": p.name} for p in payees]

@router.post("/api/checks-efts/check-payees")
async def create_check_payee(
    payee: CheckPayeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    name = payee.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Payee name cannot be empty")

    existing = db.query(CheckPayee).filter(CheckPayee.name == name).first()
    if existing:
        return {"id": existing.id, "name": existing.name}

    new_payee = CheckPayee(name=name)
    db.add(new_payee)
    db.commit()
    db.refresh(new_payee)

    return {"id": new_payee.id, "name": new_payee.name}

@router.put("/api/checks-efts/check-payees/{payee_id}")
async def update_check_payee(
    payee_id: int,
    payee: CheckPayeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    existing = db.query(CheckPayee).filter(CheckPayee.id == payee_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Payee not found")

    name = payee.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Payee name cannot be empty")

    name_exists = db.query(CheckPayee).filter(
        CheckPayee.name == name,
        CheckPayee.id != payee_id
    ).first()
    if name_exists:
        raise HTTPException(status_code=400, detail="Payee name already exists")

    existing.name = name
    db.commit()
    db.refresh(existing)

    return {"id": existing.id, "name": existing.name}

@router.delete("/api/checks-efts/check-payees/{payee_id}")
async def delete_check_payee(
    payee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payee = db.query(CheckPayee).filter(CheckPayee.id == payee_id).first()
    if not payee:
        raise HTTPException(status_code=404, detail="Payee not found")

    db.delete(payee)
    db.commit()

    return {"success": True}

@router.get("/api/checks-efts/eft-card-numbers")
async def get_eft_card_numbers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    cards = db.query(EFTCardNumber).order_by(EFTCardNumber.number).all()
    return [{"id": c.id, "number": c.number} for c in cards]

@router.post("/api/checks-efts/eft-card-numbers")
async def create_eft_card_number(
    card: EFTCardNumberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    number = card.number.strip()
    if not number:
        raise HTTPException(status_code=400, detail="Card number cannot be empty")

    existing = db.query(EFTCardNumber).filter(EFTCardNumber.number == number).first()
    if existing:
        return {"id": existing.id, "number": existing.number}

    new_card = EFTCardNumber(number=number)
    db.add(new_card)
    db.commit()
    db.refresh(new_card)

    return {"id": new_card.id, "number": new_card.number}

@router.put("/api/checks-efts/eft-card-numbers/{card_id}")
async def update_eft_card_number(
    card_id: int,
    card: EFTCardNumberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    existing = db.query(EFTCardNumber).filter(EFTCardNumber.id == card_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Card number not found")

    number = card.number.strip()
    if not number:
        raise HTTPException(status_code=400, detail="Card number cannot be empty")

    number_exists = db.query(EFTCardNumber).filter(
        EFTCardNumber.number == number,
        EFTCardNumber.id != card_id
    ).first()
    if number_exists:
        raise HTTPException(status_code=400, detail="Card number already exists")

    existing.number = number
    db.commit()
    db.refresh(existing)

    return {"id": existing.id, "number": existing.number}

@router.delete("/api/checks-efts/eft-card-numbers/{card_id}")
async def delete_eft_card_number(
    card_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    card = db.query(EFTCardNumber).filter(EFTCardNumber.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card number not found")

    db.delete(card)
    db.commit()

    return {"success": True}

@router.get("/api/checks-efts/eft-payees")
async def get_eft_payees(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payees = db.query(EFTPayee).order_by(EFTPayee.name).all()
    return [{"id": p.id, "name": p.name} for p in payees]

@router.post("/api/checks-efts/eft-payees")
async def create_eft_payee(
    payee: EFTPayeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    name = payee.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Payee name cannot be empty")

    existing = db.query(EFTPayee).filter(EFTPayee.name == name).first()
    if existing:
        return {"id": existing.id, "name": existing.name}

    new_payee = EFTPayee(name=name)
    db.add(new_payee)
    db.commit()
    db.refresh(new_payee)

    return {"id": new_payee.id, "name": new_payee.name}

@router.put("/api/checks-efts/eft-payees/{payee_id}")
async def update_eft_payee(
    payee_id: int,
    payee: EFTPayeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    existing = db.query(EFTPayee).filter(EFTPayee.id == payee_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Payee not found")

    name = payee.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Payee name cannot be empty")

    name_exists = db.query(EFTPayee).filter(
        EFTPayee.name == name,
        EFTPayee.id != payee_id
    ).first()
    if name_exists:
        raise HTTPException(status_code=400, detail="Payee name already exists")

    existing.name = name
    db.commit()
    db.refresh(existing)

    return {"id": existing.id, "name": existing.name}

@router.delete("/api/checks-efts/eft-payees/{payee_id}")
async def delete_eft_payee(
    payee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payee = db.query(EFTPayee).filter(EFTPayee.id == payee_id).first()
    if not payee:
        raise HTTPException(status_code=404, detail="Payee not found")

    db.delete(payee)
    db.commit()

    return {"success": True}

@router.get("/checks-efts/manage", response_class=HTMLResponse)
async def manage_checks_efts_page(
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    return templates.TemplateResponse(
        "checks_efts/manage.html",
        {
            "request": request,
            "current_user": user
        }
    )
