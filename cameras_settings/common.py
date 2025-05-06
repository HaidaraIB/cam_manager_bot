from telegram import InlineKeyboardButton, Update
from telegram.ext import ContextTypes
import models
import re

ADMIN_UPDATE_CAM_CONSTRUCTIONS = (
    "اختر حقلاً لتعديله، يمكنك إرسال معلومات الكاميرا كاملة ليقوم البوت بتحديثها تلقائياً"
)
USER_UPDATE_CAM_CONSTRUCITONS = "اختر حقلاً لتعديله"


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
        [
            InlineKeyboardButton(
                text="بحث 🔎",
                callback_data="search_cameras",
            )
        ],
    ]
    return keyboard


def build_single_camera_settings_keyboard(for_admin: bool):
    keyboard = [
        [
            InlineKeyboardButton(
                text="تعديل 🔄",
                callback_data="update_camera",
            ),
        ],
    ]
    if for_admin:
        keyboard[0].append(
            InlineKeyboardButton(
                text="حذف ❌",
                callback_data="delete_cameras",
            )
        )
    return keyboard


def build_update_camera_keyboard(for_admin: bool):
    if for_admin:
        keyboard = [
            [
                InlineKeyboardButton(
                    text="إضافة صورة",
                    callback_data="update_cam_add_new_photo",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="الاسم",
                    callback_data="update_cam_name",
                ),
                InlineKeyboardButton(
                    text="port",
                    callback_data="update_cam_port",
                ),
                InlineKeyboardButton(
                    text="ip",
                    callback_data="update_cam_ip",
                ),
            ],
            [
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
            ],
            [
                InlineKeyboardButton(
                    text="النوع",
                    callback_data="update_cam_cam_type",
                ),
                InlineKeyboardButton(
                    text="الحالة",
                    callback_data="update_cam_status",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="الموقع",
                    callback_data="update_cam_location",
                ),
                InlineKeyboardButton(
                    text="الرقم التسلسلي",
                    callback_data="update_cam_serial",
                ),
                InlineKeyboardButton(
                    text="DDNS",
                    callback_data="update_cam_ddns",
                ),
            ],
        ]
    else:
        keyboard = [
            [
                InlineKeyboardButton(
                    text="الحالة",
                    callback_data="update_cam_status",
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


def stringify_cam(
    for_admin: bool,
    cam_data: dict = None,
    cam: models.Camera = None,
):
    if for_admin:
        return (
            (
                f"🔖 Name: <b>{cam_data['name']}</b>\n"
                f"🌐 IP Address: {cam_data['ip']}\n"
                f"🛰️ DDNS: {cam_data['ddns']}\n"
                f"🔌 Port: <b>{cam_data['port']}</b>\n"
                f"🤵🏻 Admin Username: <code>{cam_data['admin_user']}</code>\n"
                f"🔑 Admin Password: <code>{cam_data['admin_pass']}</code>\n"
                f"👤 User Username: <code>{cam_data['user']}</code>\n"
                f"🔐 User Password: <code>{cam_data['user_pass']}</code>\n"
                f"🔖 Serial Number: <code>{cam_data['serial']}</code>\n"
                f"📷 Type: <b>{cam_data['cam_type']}</b>\n"
                f"📶 Status: <b>{cam_data['status']}</b>\n"
                f"📍 Location: <b>{cam_data['location']}</b>"
            )
            if cam_data
            else (
                f"🔖 Name: <b>{cam.name}</b>\n"
                f"🌐 IP Address: {cam.ip}\n"
                f"🛰️ DDNS: {cam.ddns}\n"
                f"🔌 Port: <b>{cam.port}</b>\n"
                f"🤵🏻 Admin Username: <code>{cam.admin_user}</code>\n"
                f"🔑 Admin Password: <code>{cam.admin_password}</code>\n"
                f"👤 User Username: <code>{cam.user}</code>\n"
                f"🔐 User Password: <code>{cam.user_password}</code>\n"
                f"🔖 Serial Number: <code>{cam.serial}</code>\n"
                f"📷 Type: <b>{cam.cam_type}</b>\n"
                f"📶 Status: <b>{cam.status}</b>\n"
                f"📍 Location: <b>{cam.location}</b>"
            )
        )
    else:
        return (
            (
                f"🔖 Name: <b>{cam_data['name']}</b>\n"
                f"🌐 IP Address: {cam_data['ip']}\n"
                f"🛰️ DDNS: {cam_data['ddns']}\n"
                f"🔌 Port: <b>{cam_data['port']}</b>\n"
                f"👤 Username: <code>{cam_data['user']}</code>\n"
                f"🔐 Password: <code>{cam_data['user_pass']}</code>\n"
                f"🔖 Serial Number: <code>{cam_data['serial']}</code>\n"
                f"📷 Type: <b>{cam_data['cam_type']}</b>\n"
                f"📶 Status: <b>{cam_data['status']}</b>\n"
                f"📍 Location: <b>{cam_data['location']}</b>"
            )
            if cam_data
            else (
                f"🔖 Name: <b>{cam.name}</b>\n"
                f"🌐 IP Address: {cam.ip}\n"
                f"🛰️ DDNS: {cam.ddns}\n"
                f"🔌 Port: <b>{cam.port}</b>\n"
                f"👤 Username: <code>{cam.user}</code>\n"
                f"🔐 Password: <code>{cam.user_password}</code>\n"
                f"🔖 Serial Number: <code>{cam.serial}</code>\n"
                f"📷 Type: <b>{cam.cam_type}</b>\n"
                f"📶 Status: <b>{cam.status}</b>\n"
                f"📍 Location: <b>{cam.location}</b>"
            )
        )


def calc_cam_photos_count(serial: str):
    cam = models.Camera.get_by(attr="serial", val=serial)
    photos = models.CamPhoto.get_by(attr="cam_id", val=cam.id, all=True)
    cam_photos_count = len(photos) + 1
    return cam_photos_count


async def extract_cam_info(
    raw_cam_info: str, update: Update, context: ContextTypes.DEFAULT_TYPE
):
    context.user_data["raw_cam_info"] = raw_cam_info
    pattern = re.compile(
        r"(\d+\.\d+\.\d+\.\d+)_(\d+)_([\w\d]+)_([\w\d@]+)_(SN-[\w\d]+)_\d+"
    )
    match = pattern.match(raw_cam_info)
    if not match:
        await update.message.reply_text(
            text="خطأ في التنسيق ⚠️",
        )
        return False
    ip, port, admin_user, admin_pass, serial_number = match.groups()
    if models.Camera.get_by(attr="serial", val=serial_number):
        await update.message.reply_text(
            text="الكاميرا مضافة مسبقاً ⚠️",
        )
        return False
    last_cam = models.Camera.get_by(last=True)
    last_cam_id = last_cam.id if last_cam else 0
    name = f"Cam_{str(last_cam_id + 1).rjust(3, '0')}_cctv"

    cam_type = (
        "dahua"
        if port in ["37777", "80"]
        else "hikvision" if port in ["8000", "9000"] else "unknown"
    )
    context.user_data["name"] = name
    context.user_data["ip"] = ip
    context.user_data["port"] = port
    context.user_data["admin_user"] = admin_user
    context.user_data["admin_pass"] = admin_pass
    context.user_data["user"] = ""
    context.user_data["user_pass"] = ""
    context.user_data["cam_type"] = cam_type
    context.user_data["status"] = "connected"
    context.user_data["location"] = "N/A"
    context.user_data["ddns"] = "N/A"
    context.user_data["serial"] = serial_number
    return True
