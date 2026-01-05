from app.data.enums import PaymentScheme
from fastapi import APIRouter

from app.schemas.calculator import LeasingCalcRequest, LeasingCalcResponse
from app.utils.finance import calculate_annuity_schedule, calculate_differentiated_schedule

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
    TAX_RATE = 0.2

    # ---------------- ANNUITY ----------------
    if scheme == PaymentScheme.annuity:
        schedule, total_paid, monthly_payment = calculate_annuity_schedule(
            loan_amount, monthly_rate, data.term_months
        )

    # ---------------- DIFFERENTIATED ----------------
    else:
        schedule, total_paid = calculate_differentiated_schedule(
            loan_amount, monthly_rate, data.term_months
        )
        monthly_payment = None

    total_amount = total_paid + advance
    # Налоговая экономия (НДС + прибыль, грубая модель)
    tax_saving = total_paid * TAX_RATE  # 20% (можно вынести в настройку)

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
