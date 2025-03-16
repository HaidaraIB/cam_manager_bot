from enum import Enum


class AlertType(Enum):
    STATUS_UPDATE = {
        "en": "Status Update",
        "ar": "تحديث الحالة",
        "code": "status_update",
    }
    ADD_CAM = {
        "en": "Add Cam",
        "ar": "إضافة كاميرا",
        "code": "add_cam",
    }
    ADD_USER = {
        "en": "Add User",
        "ar": "إضافة مستخدم",
        "code": "add_user",
    }
