from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates

from app.db.database import get_db
from app.models.user import User
from app.models.lease import Lease
from app.models.payment import Payment
from starlette.responses import RedirectResponse

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# -----------------------
# Главная страница кабинета
# -----------------------
@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, user_id: int = 1):
    return templates.TemplateResponse("dashboard/index.html", {"request": request})


# -----------------------
# Создание заявки (форма)
# -----------------------
@router.get("/dashboard/new", response_class=HTMLResponse)
def dashboard_new(request: Request):
    return templates.TemplateResponse("dashboard/new_lease.html", {"request": request})


# AJAX создание заявки
@router.post("/api/leases/create")
def api_create_lease(
    request: Request,
    equipment: str = Form(...),
    advance: float = Form(...),
    term: int = Form(...),
    rate: float = Form(...),
    payment_scheme: str = Form(...),
    db: Session = Depends(get_db),
    user_id: int = 1
):
    try:
        lease = Lease(
            equipment=equipment,
            amount=advance + term * rate,
            advance=advance,
            term=term,
            rate=rate,
            payment_scheme=payment_scheme,
            status="Отправлена",
            user_id=user_id
        )
        db.add(lease)
        db.commit()
        db.refresh(lease)

        return {"success": True, "lease": lease.to_dict(), "message": "Заявка создана!"}

    except Exception as e:
        db.rollback()
        return {"success": False, "message": "Ошибка при создании заявки"}


# -----------------------
# Мои заявки (страница)
# -----------------------
@router.get("/dashboard/leases", response_class=HTMLResponse)
def dashboard_leases(request: Request):
    return templates.TemplateResponse("dashboard/leases.html", {"request": request})


# AJAX список заявок + фильтры + сортировка
@router.get("/api/leases/list")
def api_list_leases(
    status: str | None = None,
    order: str | None = "desc",
    db: Session = Depends(get_db),
    user_id: int = 1
):
    query = db.query(Lease).filter(Lease.user_id == user_id)

    if status and status != "all":
        query = query.filter(Lease.status == status)

    if order == "asc":
        query = query.order_by(Lease.created_at.asc())
    else:
        query = query.order_by(Lease.created_at.desc())

    result = [lease.to_dict() for lease in query.all()]

    return {"leases": result}


# -----------------------
# Статусы
# -----------------------
@router.get("/dashboard/statuses", response_class=HTMLResponse)
def dashboard_statuses(request: Request):
    return templates.TemplateResponse("dashboard/statuses.html", {"request": request})


# -----------------------
# Платежи
# -----------------------
@router.get("/dashboard/payments", response_class=HTMLResponse)
def dashboard_payments(request: Request):
    return templates.TemplateResponse("dashboard/payments.html", {"request": request})


@router.get("/api/payments/list")
def api_payments_list(db: Session = Depends(get_db), user_id: int = 1):
    payments = db.query(Payment).filter(Payment.user_id == user_id).all()
    return {"payments": [p.to_dict() for p in payments]}


# -----------------------
# Профиль
# -----------------------
@router.get("/dashboard/profile", response_class=HTMLResponse)
def dashboard_profile(request: Request, db: Session = Depends(get_db), user_id: int = 1):
    user = db.query(User).filter(User.id == user_id).first()
    return templates.TemplateResponse("dashboard/profile.html", {"request": request, "user": user})


@router.post("/api/profile/update")
def api_profile_update(
    full_name: str = Form(...),
    phone: str = Form(...),
    db: Session = Depends(get_db),
    user_id: int = 1
):
    user = db.query(User).filter(User.id == user_id).first()
    user.full_name = full_name
    user.phone = phone
    db.commit()
    return {"success": True, "message": "Профиль обновлён"}

