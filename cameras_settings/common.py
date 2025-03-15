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
                f"🔖 Name: {cam_data['name']}\n"
                f"🌐 IP Address: {cam_data['ip']}\n"
                f"🔌 Port: {cam_data['port']}\n"
                f"🤵🏻 Admin Username: {cam_data['admin_user']}\n"
                f"🔑 Admin Password: {cam_data['admin_pass']}\n"
                f"👤 User Username: {cam_data['user']}\n"
                f"🔐 User Password: {cam_data['user_pass']}\n"
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
                f"🤵🏻 Admin Username: {cam.admin_user}\n"
                f"🔑 Admin Password: {cam.admin_password}\n"
                f"👤 User Username: {cam.user}\n"
                f"🔐 User Password: {cam.user_password}\n"
                f"🔖 Serial Number: {cam.serial}\n"
                f"📷 Type: {cam.cam_type}\n"
                f"📶 Status: {cam.status}\n"
                f"📍 Location: {cam.location}"
            )
        )
    else:
        return (
            (
                f"🔖 Name: {cam_data['name']}\n"
                f"🌐 IP Address: {cam_data['ip']}\n"
                f"🔌 Port: {cam_data['port']}\n"
                f"👤 Username: {cam_data['user']}\n"
                f"🔐 Password: {cam_data['user_pass']}\n"
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
                f"👤 Username: {cam.user}\n"
                f"🔐 Password: {cam.user_password}\n"
                f"🔖 Serial Number: {cam.serial}\n"
                f"📷 Type: {cam.cam_type}\n"
                f"📶 Status: {cam.status}\n"
                f"📍 Location: {cam.location}"
            )
        )
