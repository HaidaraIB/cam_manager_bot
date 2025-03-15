from telegram import Update, Chat, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler
from custom_filters import Admin
from admin.cameras_settings.common import build_cameras_settings_keyboard
from common.back_to_home_page import back_to_admin_home_page_button


async def cameras_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        keyboard = build_cameras_settings_keyboard()
        keyboard.append(back_to_admin_home_page_button[0])

        await update.callback_query.edit_message_text(
            text="إدارة الكاميرات 📷",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return ConversationHandler.END


cameras_settings_handler = CallbackQueryHandler(
    cameras_settings,
    "^manage_cameras$|^back_to_cameras_settings$",
)
