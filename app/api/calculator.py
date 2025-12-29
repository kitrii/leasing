

from pydantic import BaseModel, Field
from enum import Enum


class PaymentScheme(str, Enum):
    annuity = "annuity"
    differentiated = "differentiated"


class LeasingCalcRequest(BaseModel):
    scheme: PaymentScheme = Field(..., description="Схема платежей")
    annual_rate: float = Field(..., example=15.0, description="Процентная ставка годовых")
    asset_price: float = Field(..., example=10_000_000, description="Стоимость имущества")
    term_months: int = Field(..., example=36, description="Срок договора в месяцах")
    advance_percent: float = Field(..., example=20.0, description="Аванс в процентах")


class PaymentScheduleItem(BaseModel):
    month: int
    payment: float
    interest: float
    principal: float
    remaining_debt: float


class LeasingCalcResponse(BaseModel):
    monthly_payment: float | None
    total_amount: float
    tax_saving: float
    annual_overpayment_percent: float
    schedule: list[PaymentScheduleItem]


from fastapi import APIRouter
from math import pow

router = APIRouter()


@router.post("/api/calculate", response_model=LeasingCalcResponse)
def calculate_leasing(data: LeasingCalcRequest):
    asset_price = data.asset_price
    term = data.term_months
    annual_rate = data.annual_rate
    scheme = data.scheme

    advance = asset_price * data.advance_percent / 100
    loan_amount = asset_price - advance
    monthly_rate = annual_rate / 100 / 12

    schedule = []
    total_paid = 0
    remaining = loan_amount

    # ---------------- ANNUITY ----------------
    if scheme == PaymentScheme.annuity:
        annuity_payment = loan_amount * (
            monthly_rate * pow(1 + monthly_rate, term)
        ) / (pow(1 + monthly_rate, term) - 1)

        for month in range(1, term + 1):
            interest = remaining * monthly_rate
            principal = annuity_payment - interest
            remaining -= principal

            schedule.append({
                "month": month,
                "payment": round(annuity_payment, 2),
                "interest": round(interest, 2),
                "principal": round(principal, 2),
                "remaining_debt": round(max(remaining, 0), 2),
            })

            total_paid += annuity_payment

        monthly_payment = round(annuity_payment, 2)

    # ---------------- DIFFERENTIATED ----------------
    else:
        principal_part = loan_amount / term
        monthly_payment = None

        for month in range(1, term + 1):
            interest = remaining * monthly_rate
            payment = principal_part + interest
            remaining -= principal_part

            schedule.append({
                "month": month,
                "payment": round(payment, 2),
                "interest": round(interest, 2),
                "principal": round(principal_part, 2),
                "remaining_debt": round(max(remaining, 0), 2),
            })

            total_paid += payment

    total_amount = total_paid + advance

    # Налоговая экономия (НДС + прибыль, грубая модель)
    tax_saving = total_paid * 0.2  # 20% (можно вынести в настройку)

    annual_overpayment_percent = (
        (total_amount - asset_price) / asset_price
    ) / (term / 12) * 100

    return {
        "monthly_payment": monthly_payment,
        "total_amount": round(total_amount, 2),
        "tax_saving": round(tax_saving, 2),
        "annual_overpayment_percent": round(annual_overpayment_percent, 2),
        "schedule": schedule,
    }
