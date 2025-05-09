from telegram import InlineKeyboardButton


def build_user_settings_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                text="إضافة مستخدم ➕",
                callback_data="add user",
            ),
            InlineKeyboardButton(
                text="حذف مستخدم ✖️",
                callback_data="remove user",
            ),
        ],
        [
            InlineKeyboardButton(
                text="عرض المستخدمين الحاليين 🆔",
                callback_data="show users",
            )
        ],
    ]
    return keyboard
