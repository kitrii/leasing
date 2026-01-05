from pydantic import BaseModel, Field
from app.data.enums import PaymentScheme


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

