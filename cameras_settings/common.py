from telegram import (
    InlineKeyboardButton,
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto,
)
from telegram.ext import ContextTypes
from typing import TypedDict, List, cast
from telegram.ext import ContextTypes
from common.keyboards import build_back_button
from common.back_to_home_page import (
    back_to_admin_home_page_button,
    back_to_user_home_page_button,
)
import models
import re
import logging

log = logging.getLogger(__name__)

ADMIN_UPDATE_CAM_CONSTRUCTIONS = (
    "اختر حقلاً لتعديله، يمكنك إرسال معلومات الكاميرا كاملة ليقوم البوت بتحديثها تلقائياً"
)
USER_UPDATE_CAM_CONSTRUCITONS = "اختر حقلاً لتعديله"

CAM_INFO_PATTERN = (
    r"(\d+\.\d+\.\d+\.\d+)_(\d+)_([\w\d]+)_([\w\d@]+)_(SN-[\w\d-]*)_\d+(_HD)?"
)


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


async def extract_cam_info(raw_cam_info: str, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["raw_cam_info"] = raw_cam_info
    pattern = re.compile(CAM_INFO_PATTERN)
    match = pattern.match(raw_cam_info)

    if not match:
        return "no match"

    ip, port, admin_user, admin_pass, serial_number, _ = match.groups()
    if models.Camera.get_by(attr="serial", val=serial_number):
        return "duplicate"

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
    context.user_data["serial"] = serial_number[3:] if serial_number[3:] else name
    return "done"


async def media_group_sender(context: ContextTypes.DEFAULT_TYPE):
    is_admin = context.job.data
    photos_data = context.application.user_data[context.job.user_id]["photos_data"]
    res = "no match"
    for p_data in photos_data:
        if p_data["caption"]:
            res = await extract_cam_info(
                raw_cam_info=p_data["caption"], context=context
            )
            if res in ["no match", "duplicate"]:
                continue
            break
    if res == "no match":
        await context.bot.send_message(
            chat_id=context.job.chat_id,
            text="خطأ في التنسيق ⚠️",
        )
        return
    elif res == "duplicate":
        await context.bot.send_message(
            chat_id=context.job.chat_id,
            text="الكاميرا مضافة مسبقاً ⚠️",
        )
        return
    photos = [p_data["file_id"] for p_data in photos_data]
    context.application.user_data[context.job.user_id]["photos"] = photos
    try:
        await context.bot.send_media_group(
            chat_id=context.job.chat_id,
            media=[InputMediaPhoto(media=file_id) for file_id in photos],
            caption=(
                f"تم تحليل البيانات ✅\n\n"
                + stringify_cam(
                    cam_data=context.application.user_data[context.job.user_id],
                    for_admin=is_admin,
                )
            ),
        )
        keyboard = [
            [
                InlineKeyboardButton(
                    text="إضافة ➕",
                    callback_data="confirm_add_cam",
                )
            ],
            build_back_button("back_to_get_cam_info"),
            (
                back_to_admin_home_page_button[0]
                if is_admin
                else back_to_user_home_page_button[0]
            ),
        ]
        await context.bot.send_message(
            chat_id=context.job.chat_id,
            text="هل أنت متأكد من أنك تريد إضافة هذه الكاميرا؟",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    except Exception as e:
        await context.bot.send_message(
            chat_id=context.job.chat_id,
            text="خطأ أثناء تحليل البيانات يرجى إعادة المحاولة من جديد ❗️",
        )
        log.error(f"error while sending media group: {e}")
