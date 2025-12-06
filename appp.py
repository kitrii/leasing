"""
FastAPI backend prototype for "Личный кабинет + роли" для диплома
- Python 3.10+
- FastAPI
- SQLAlchemy (sync)
- Pydantic
- Passlib for password hashing
- PyJWT for JWT

How to run (dev):
$ pip install fastapi uvicorn sqlalchemy pydantic passlib[bcrypt] python-multipart python-jose[cryptography]
$ export DATABASE_URL="sqlite:///./leasing.db" # or PostgreSQL URL
$ uvicorn fastapi_leasing_backend:app --reload --port 8000

This single-file prototype contains:
- models: User, SupplierProfile, Equipment, Application, Payment, Document
- auth: password hashing, JWT access tokens, OAuth2PasswordBearer
- RBAC: dependency require_role
- routers: auth (register/login), profile (/me), applications, supplier equipment, admin endpoints

Notes:
- File upload handlers store files to ./uploads by default (ensure dir exists)
- For production use PostgreSQL, Alembic migrations, async endpoints and background tasks for expensive jobs.
- Payment schedule generation is implemented for annuity and differentiated schemes.

"""
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional, Dict, Any
import os
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import (create_engine, Column, Integer, String, DateTime, ForeignKey, Float, Text, Enum as SAEnum, JSON, Boolean)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session
from passlib.context import CryptContext
import jwt

# -----------------------------
# Config
# -----------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./leasing.db")
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # week
UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# -----------------------------
# DB setup
# -----------------------------
engine = create_engine(DATABASE_URL,
                       connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# -----------------------------
# Password hashing
# -----------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# -----------------------------
# Role enum
# -----------------------------
class RoleEnum(str, Enum):
    client = "client"
    supplier = "supplier"
    manager = "manager"
    admin = "admin"

# -----------------------------
# Models
# -----------------------------


class SupplierProfile(Base):
    __tablename__ = "supplier_profiles"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    company_name = Column(String, nullable=False)
    inn = Column(String, nullable=True)
    legal_address = Column(String, nullable=True)
    logo_url = Column(String, nullable=True)

    user = relationship("User", back_populates="supplier_profile")
    equipments = relationship("Equipment", back_populates="supplier")



class ApplicationStatus(str, Enum):
    sent = "sent"
    reviewing = "reviewing"
    approved = "approved"
    rejected = "rejected"
    contract_issued = "contract_issued"
    active = "active"
    closed = "closed"

class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('users.id'))
    equipment_id = Column(Integer, ForeignKey('equipments.id'))
    supplier_id = Column(Integer, ForeignKey('supplier_profiles.id'))

    down_payment = Column(Float, nullable=False)
    term_months = Column(Integer, nullable=False)
    interest_rate = Column(Float, nullable=False)
    payment_scheme = Column(String, nullable=False)  # annuity/differentiated

    status = Column(SAEnum(ApplicationStatus), default=ApplicationStatus.sent)
    assigned_manager_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    client = relationship("User", foreign_keys=[client_id], back_populates="applications")
    equipment = relationship("Equipment", back_populates="applications")
    payments = relationship("Payment", back_populates="application")





# -----------------------------
# Create tables
# -----------------------------
Base.metadata.create_all(bind=engine)

# -----------------------------
# Pydantic schemas
# -----------------------------
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int]
    role: Optional[RoleEnum]

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str]
    phone: Optional[str]
    role: Optional[RoleEnum] = RoleEnum.client

class UserPublic(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
    phone: Optional[str]
    role: RoleEnum
    class Config:
        orm_mode = True

class EquipmentCreate(BaseModel):
    name: str
    description: Optional[str]
    price: float
    quantity: int = 1
    params: Optional[Dict[str, Any]] = None

class EquipmentOut(BaseModel):
    id: int
    name: str
    price: float
    quantity: int
    params: Optional[Dict[str, Any]]
    images: Optional[List[str]]
    supplier_id: int
    class Config:
        orm_mode = True

class ApplicationCreate(BaseModel):
    equipment_id: int
    down_payment: float
    term_months: int
    interest_rate: float
    payment_scheme: str = Field(..., regex="^(annuity|differentiated)$")

class ApplicationOut(BaseModel):
    id: int
    equipment_id: int
    client_id: int
    down_payment: float
    term_months: int
    interest_rate: float
    payment_scheme: str
    status: ApplicationStatus
    created_at: datetime
    class Config:
        orm_mode = True

class PaymentOut(BaseModel):
    due_date: datetime
    amount: float
    paid: bool
    paid_at: Optional[datetime]
    class Config:
        orm_mode = True

# -----------------------------
# Utils: auth
# -----------------------------
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

# -----------------------------
# DB dependency
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------
# Current user dependency
# -----------------------------
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_access_token(token)
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

# RBAC
def require_role(role: RoleEnum):
    def role_checker(user: User = Depends(get_current_user)):
        if user.role != role and user.role != RoleEnum.admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user
    return role_checker

# -----------------------------
# Payment schedule generators
# -----------------------------
from math import pow

def generate_annuity_schedule(principal: float, months: int, annual_rate_percent: float, start_date: datetime) -> List[Dict[str, Any]]:
    # principal = equipment_price - down_payment
    monthly_rate = annual_rate_percent / 100 / 12
    if monthly_rate == 0:
        monthly_payment = principal / months
    else:
        monthly_payment = principal * (monthly_rate * pow(1 + monthly_rate, months)) / (pow(1 + monthly_rate, months) - 1)
    schedule = []
    remaining = principal
    for m in range(1, months + 1):
        if monthly_rate == 0:
            interest = 0
            principal_paid = monthly_payment
        else:
            interest = remaining * monthly_rate
            principal_paid = monthly_payment - interest
        remaining -= principal_paid
        due = start_date + timedelta(days=30*m)
        schedule.append({"month": m, "due_date": due, "amount": round(monthly_payment, 2), "principal_paid": round(principal_paid,2), "interest": round(interest,2), "remaining": round(max(remaining,0),2)})
    return schedule


def generate_differentiated_schedule(principal: float, months: int, annual_rate_percent: float, start_date: datetime) -> List[Dict[str, Any]]:
    monthly_rate = annual_rate_percent / 100 / 12
    schedule = []
    remaining = principal
    principal_payment = principal / months
    for m in range(1, months + 1):
        interest = remaining * monthly_rate
        amount = principal_payment + interest
        remaining -= principal_payment
        due = start_date + timedelta(days=30*m)
        schedule.append({"month": m, "due_date": due, "amount": round(amount,2), "principal_paid": round(principal_payment,2), "interest": round(interest,2), "remaining": round(max(remaining,0),2)})
    return schedule

# -----------------------------
# App and routers
# -----------------------------
app = FastAPI(title="Leasing Backend Prototype")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Auth endpoints ---
@app.post('/auth/register', response_model=UserPublic)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail='Email already registered')
    user = User(email=user_in.email, hashed_password=get_password_hash(user_in.password), full_name=user_in.full_name, phone=user_in.phone, role=user_in.role)
    db.add(user)
    db.commit()
    db.refresh(user)
    # if supplier role, create empty supplier profile
    if user.role == RoleEnum.supplier:
        sp = SupplierProfile(user_id=user.id, company_name=user_in.full_name or "Supplier")
        db.add(sp)
        db.commit()
    return user

@app.post('/auth/token', response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail='Incorrect username or password')
    token = create_access_token({"user_id": user.id, "role": user.role.value})
    return {"access_token": token, "token_type": "bearer"}

# --- Profile ---
@app.get('/me', response_model=UserPublic)
def read_me(user: User = Depends(get_current_user)):
    return user

@app.put('/me', response_model=UserPublic)
def update_me(full_name: Optional[str] = Form(None), phone: Optional[str] = Form(None), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if full_name is not None:
        user.full_name = full_name
    if phone is not None:
        user.phone = phone
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post('/me/upload-document')
def upload_document(file: UploadFile = File(...), application_id: Optional[int] = Form(None), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # save file
    filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}"
    path = UPLOAD_DIR / filename
    with path.open('wb') as f:
        f.write(file.file.read())
    url = str(path)
    doc = Document(user_id=user.id, application_id=application_id, filename=file.filename, url=url)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return {"id": doc.id, "url": doc.url}

# --- Equipment for suppliers ---
@app.post('/supplier/equipment', response_model=EquipmentOut)
def add_equipment(data: EquipmentCreate, db: Session = Depends(get_db), user: User = Depends(require_role(RoleEnum.supplier))):
    sp = db.query(SupplierProfile).filter(SupplierProfile.user_id == user.id).first()
    if not sp:
        raise HTTPException(status_code=400, detail='Supplier profile not found')
    eq = Equipment(supplier_id=sp.id, name=data.name, description=data.description, price=data.price, quantity=data.quantity, params=data.params, images=[])
    db.add(eq)
    db.commit()
    db.refresh(eq)
    return eq

@app.post('/supplier/equipment/{equipment_id}/upload-image')
def upload_equipment_image(equipment_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(require_role(RoleEnum.supplier))):
    sp = db.query(SupplierProfile).filter(SupplierProfile.user_id == user.id).first()
    eq = db.query(Equipment).filter(Equipment.id == equipment_id, Equipment.supplier_id == sp.id).first()
    if not eq:
        raise HTTPException(status_code=404, detail='Equipment not found')
    filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}"
    path = UPLOAD_DIR / filename
    with path.open('wb') as f:
        f.write(file.file.read())
    url = str(path)
    imgs = eq.images or []
    imgs.append(url)
    eq.images = imgs
    db.add(eq)
    db.commit()
    db.refresh(eq)
    return {"images": eq.images}

@app.get('/supplier/equipment', response_model=List[EquipmentOut])
def list_my_equipment(db: Session = Depends(get_db), user: User = Depends(require_role(RoleEnum.supplier))):
    sp = db.query(SupplierProfile).filter(SupplierProfile.user_id == user.id).first()
    return db.query(Equipment).filter(Equipment.supplier_id == sp.id).all()

# --- Applications (client) ---
@app.post('/applications', response_model=ApplicationOut)
def create_application(app_in: ApplicationCreate, db: Session = Depends(get_db), user: User = Depends(require_role(RoleEnum.client))):
    equipment = db.query(Equipment).filter(Equipment.id == app_in.equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail='Equipment not found')
    # basic validation
    if app_in.down_payment < 0 or app_in.term_months <= 0:
        raise HTTPException(status_code=400, detail='Invalid financial params')
    application = Application(client_id=user.id, equipment_id=equipment.id, supplier_id=equipment.supplier_id, down_payment=app_in.down_payment, term_months=app_in.term_months, interest_rate=app_in.interest_rate, payment_scheme=app_in.payment_scheme)
    db.add(application)
    db.commit()
    db.refresh(application)
    return application

@app.get('/applications', response_model=List[ApplicationOut])
def list_my_applications(db: Session = Depends(get_db), user: User = Depends(require_role(RoleEnum.client)), status: Optional[ApplicationStatus] = None):
    q = db.query(Application).filter(Application.client_id == user.id)
    if status:
        q = q.filter(Application.status == status)
    return q.order_by(Application.created_at.desc()).all()

@app.get('/applications/{application_id}', response_model=ApplicationOut)
def get_application(application_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    appobj = db.query(Application).filter(Application.id == application_id).first()
    if not appobj:
        raise HTTPException(status_code=404, detail='Application not found')
    # clients can access only their own apps unless admin/manager
    if user.role == RoleEnum.client and appobj.client_id != user.id:
        raise HTTPException(status_code=403, detail='Forbidden')
    return appobj

@app.get('/applications/{application_id}/payments', response_model=List[PaymentOut])
def get_application_payments(application_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    appobj = db.query(Application).filter(Application.id == application_id).first()
    if not appobj:
        raise HTTPException(status_code=404, detail='Application not found')
    if user.role == RoleEnum.client and appobj.client_id != user.id:
        raise HTTPException(status_code=403, detail='Forbidden')
    return db.query(Payment).filter(Payment.application_id == application_id).order_by(Payment.due_date).all()

# --- Manager endpoints ---
@app.get('/manager/applications', response_model=List[ApplicationOut])
def manager_list_applications(db: Session = Depends(get_db), user: User = Depends(require_role(RoleEnum.manager)), status: Optional[ApplicationStatus] = None):
    q = db.query(Application)
    if status:
        q = q.filter(Application.status == status)
    return q.order_by(Application.created_at.desc()).all()

@app.post('/manager/applications/{application_id}/assign')
def manager_assign_application(application_id: int, manager_id: int = Form(...), db: Session = Depends(get_db), user: User = Depends(require_role(RoleEnum.manager))):
    appobj = db.query(Application).filter(Application.id == application_id).first()
    if not appobj:
        raise HTTPException(status_code=404, detail='Application not found')
    appobj.assigned_manager_id = manager_id
    appobj.status = ApplicationStatus.reviewing
    db.add(appobj)
    db.commit()
    return {"ok": True}

@app.post('/manager/applications/{application_id}/change-status')
def manager_change_status(application_id: int, status_new: ApplicationStatus = Form(...), db: Session = Depends(get_db), user: User = Depends(require_role(RoleEnum.manager))):
    appobj = db.query(Application).filter(Application.id == application_id).first()
    if not appobj:
        raise HTTPException(status_code=404, detail='Application not found')
    appobj.status = status_new
    db.add(appobj)
    db.commit()
    # If approved -> generate payments and optionally create contract
    if status_new == ApplicationStatus.approved:
        equipment = db.query(Equipment).filter(Equipment.id == appobj.equipment_id).first()
        principal = equipment.price - appobj.down_payment
        start_date = datetime.utcnow()
        if appobj.payment_scheme == 'annuity':
            schedule = generate_annuity_schedule(principal, appobj.term_months, appobj.interest_rate, start_date)
        else:
            schedule = generate_differentiated_schedule(principal, appobj.term_months, appobj.interest_rate, start_date)
        # persist payments
        for item in schedule:
            p = Payment(application_id=appobj.id, due_date=item['due_date'], amount=item['amount'])
            db.add(p)
        appobj.status = ApplicationStatus.contract_issued
        db.add(appobj)
        db.commit()
    return {"ok": True}

# --- Admin endpoints ---
@app.get('/admin/users', response_model=List[UserPublic])
def admin_list_users(db: Session = Depends(get_db), user: User = Depends(require_role(RoleEnum.admin))):
    return db.query(User).order_by(User.created_at.desc()).all()

@app.post('/admin/users/{user_id}/set-role')
def admin_set_role(user_id: int, role: RoleEnum = Form(...), db: Session = Depends(get_db), user: User = Depends(require_role(RoleEnum.admin))):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail='User not found')
    u.role = role
    db.add(u)
    db.commit()
    return {"ok": True}

# --- Public equipment listing ---
@app.get('/equipments', response_model=List[EquipmentOut])
def list_equipments(db: Session = Depends(get_db), skip: int = 0, limit: int = 50):
    return db.query(Equipment).offset(skip).limit(limit).all()

# -----------------------------
# End of file
# -----------------------------
