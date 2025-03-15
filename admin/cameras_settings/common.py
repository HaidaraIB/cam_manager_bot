from telegram import InlineKeyboardButton
import models
import re


def build_cameras_settings_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                text="إضافة كاميرا 📷",
                callback_data="add_camera",
            )
        ],
        [
            InlineKeyboardButton(
                text="قائمة الكاميرات 📋",
                callback_data="list_cameras",
            )
        ],
    ]
    return keyboard


def build_single_camera_settings_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                text="تعديل 🔄",
                callback_data="update_camera",
            ),
            InlineKeyboardButton(
                text="حذف ❌",
                callback_data="delete_cameras",
            ),
        ],
    ]
    return keyboard


def build_update_camera_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                text="الاسم",
                callback_data="update_cam_name",
            ),
            InlineKeyboardButton(
                text="الصورة",
                callback_data="update_cam_photo",
            ),
            InlineKeyboardButton(
                text="ip",
                callback_data="update_cam_ip",
            ),
        ],
        [
            InlineKeyboardButton(
                text="port",
                callback_data="update_cam_port",
            ),
            InlineKeyboardButton(
                text="admin user",
                callback_data="update_cam_admin_user",
            ),
            InlineKeyboardButton(
                text="admin password",
                callback_data="update_cam_admin_password",
            ),
        ],
        [
            InlineKeyboardButton(
                text="user",
                callback_data="update_cam_user",
            ),
            InlineKeyboardButton(
                text="user password",
                callback_data="update_cam_user_password",
            ),
            InlineKeyboardButton(
                text="النوع",
                callback_data="update_cam_cam_type",
            ),
        ],
        [
            InlineKeyboardButton(
                text="الحالة",
                callback_data="update_cam_status",
            ),
            InlineKeyboardButton(
                text="الموقع",
                callback_data="update_cam_location",
            ),
            InlineKeyboardButton(
                text="الرقم التسلسلي",
                callback_data="update_cam_serial",
            ),
        ],
    ]
    return keyboard


def build_add_camera_methods_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                text="يدويًا 📝",
                callback_data="manual_entry",
            )
        ],
        [
            InlineKeyboardButton(
                text="تلقائيًا ⚙️",
                callback_data="auto_entry",
            )
        ],
    ]
    return keyboard


def stringify_cam(cam_data: dict = None, cam: models.Camera = None):
    return (
        (
            f"🔖 Name: {cam_data['name']}\n"
            f"🌐 IP Address: {cam_data['ip']}\n"
            f"🔌 Port: {cam_data['port']}\n"
            f"👤 Username: {cam_data['admin_user']}\n"
            f"🔐 Password: {cam_data['admin_pass']}\n"
            f"🔖 Serial Number: {cam_data['serial']}\n"
            f"📷 Type: {cam_data['cam_type']}\n"
            f"📶 Status: {cam_data['status']}\n"
            f"📍 Location: {cam_data['location']}"
        )
        if cam_data
        else (
            f"🔖 Name: {cam.name}\n"
            f"🌐 IP Address: {cam.ip}\n"
            f"🔌 Port: {cam.port}\n"
            f"👤 Username: {cam.admin_user}\n"
            f"🔐 Password: {cam.admin_password}\n"
            f"🔖 Serial Number: {cam.serial}\n"
            f"📷 Type: {cam.cam_type}\n"
            f"📶 Status: {cam.status}\n"
            f"📍 Location: {cam.location}"
        )
    )
