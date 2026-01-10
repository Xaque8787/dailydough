from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from app.database import get_db
from app.models import User, DailyBalance
from app.auth.jwt_handler import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/reports")
async def reports_page(
    request: Request,
    month: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    if month:
        try:
            target_date = datetime.strptime(month, "%Y-%m").date()
        except ValueError:
            target_date = date.today().replace(day=1)
    else:
        target_date = date.today().replace(day=1)

    month_start = target_date.replace(day=1)
    next_month = month_start + relativedelta(months=1)
    prev_month = month_start - relativedelta(months=1)

    finalized_reports = db.query(DailyBalance).filter(
        DailyBalance.date >= month_start,
        DailyBalance.date < next_month,
        DailyBalance.finalized == True
    ).order_by(DailyBalance.date.desc()).all()

    return templates.TemplateResponse(
        "reports/list.html",
        {
            "request": request,
            "current_user": current_user,
            "current_month": target_date,
            "prev_month": prev_month,
            "next_month": next_month,
            "finalized_reports": finalized_reports,
            "is_current_month": target_date.year == date.today().year and target_date.month == date.today().month
        }
    )
