from telegram import Chat, Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from admin.manage_users.common import build_user_settings_keyboard
from custom_filters import Admin
from common.back_to_home_page import back_to_admin_home_page_button


async def manage_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        keyboard = build_user_settings_keyboard()
        keyboard.append(back_to_admin_home_page_button[0])
        await update.callback_query.edit_message_text(
            text="إعدادات المستخدم 🪄",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


manage_users_handler = CallbackQueryHandler(
    manage_users,
    "^manage_users$|^back_to_manage_users$",
)
