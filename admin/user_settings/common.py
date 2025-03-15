from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Chat, Update
from telegram.ext import ContextTypes, ConversationHandler
from custom_filters import Admin
from common.back_to_home_page import back_to_admin_home_page_button


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
