from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.payment import Payment


def generate_payments_for_lease(lease, db: Session):
    """
    Генерация графика платежей для лизинговой заявки.
    Разделяет общую сумму лизинга на равные месячные платежи.
    """
    try:
        monthly_amount = lease.amount / lease.term
        payments = [
            Payment(
                lease_id=lease.id,
                amount=monthly_amount,
                due_date=datetime.utcnow() + timedelta(days=30 * (i + 1))
            )
            for i in range(lease.term)
        ]
        db.add_all(payments)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
