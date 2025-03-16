from telegram import InlineKeyboardButton
import models

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
                f"🔌 Port: <b>{cam.port}</b>\n"
                f"👤 Username: <code>{cam.user}</code>\n"
                f"🔐 Password: <code>{cam.user_password}</code>\n"
                f"🔖 Serial Number: <code>{cam.serial}</code>\n"
                f"📷 Type: <b>{cam.cam_type}</b>\n"
                f"📶 Status: <b>{cam.status}</b>\n"
                f"📍 Location: <b>{cam.location}</b>"
            )
        )
