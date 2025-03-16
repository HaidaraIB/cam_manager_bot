from enum import Enum


class AlertDest(Enum):
    USERS = "users"
    ADMINS = "admins"
    BOTH = "both"
    NONE = "none"
