from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from pydantic import BaseModel
from app.database import get_db
from app.models import User, CheckPayee, EFTCardNumber, EFTPayee, DailyBalanceCheck, DailyBalanceEFT
from app.auth.jwt_handler import get_current_user

router = APIRouter()

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
