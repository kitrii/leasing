from enum import Enum


class RoleEnum(str, Enum):
    client = "client"
    supplier = "supplier"
    manager = "manager"
    admin = "admin"
