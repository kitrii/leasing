def calculate_lease_amount(advance: float, rate: float, term: int) -> float:
    """
    Простейшая формула суммы лизинга.
    В будущем можно вынести сюда все сложные бизнес-правила.
    """
    return advance + float(term) * float(rate)
