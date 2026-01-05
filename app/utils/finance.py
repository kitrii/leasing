from math import pow

def calculate_annuity_schedule(
    loan_amount: float,
    monthly_rate: float,
    term: int
):
    schedule = []
    remaining = loan_amount
    total_paid = 0

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

    return schedule, total_paid, round(annuity_payment, 2)


def calculate_differentiated_schedule(
    loan_amount: float,
    monthly_rate: float,
    term: int
):
    schedule = []
    remaining = loan_amount
    total_paid = 0
    principal_part = loan_amount / term

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

    return schedule, total_paid
