from enum import Enum


class RoleEnum(str, Enum):
    client = "client"
    supplier = "supplier"
    manager = "manager"
    admin = "admin"


class LeasePaymentScheme(str, Enum):
    annuity = "annuity"
    differentiated = "differentiated"


class LeaseStatus(str, Enum):
    send = "Отправлена"  # Заявка создана и отправлена на рассмотрение
    approved = "Одобрена"  # Заявка одобрена, можно приступать к оформлению договора
    rejected = "Отклонена"  # Заявка отклонена
    contract_created = "Оформлен договор"  # Договор создан
    in_progress = "В процессе"  # Лизинг выполняется, платежи идут
    completed = "Завершена"  # Все платежи выполнены, лизинг закрыт
    cancelled = "Отменена"  # Заявка или лизинг отменен пользователем или менеджером
