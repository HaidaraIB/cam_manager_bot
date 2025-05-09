from telegram import Update, Chat, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler
from custom_filters import Admin, User
from cameras_settings.common import build_cameras_settings_keyboard
from common.back_to_home_page import (
    back_to_admin_home_page_button
)
from common.keyboards import build_back_to_user_home_page_button
from common.lang_dicts import *


async def cameras_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        lang = context.user_data.get('lang', models.Language.ARABIC)
        keyboard = build_cameras_settings_keyboard(lang=lang)
        keyboard.append(
            back_to_admin_home_page_button[0]
            if is_admin
            else build_back_to_user_home_page_button(lang=lang)[0]
        )
        await update.callback_query.edit_message_text(
            text=TEXTS[lang]['cameras_settings'],
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return ConversationHandler.END


cameras_settings_handler = CallbackQueryHandler(
    cameras_settings,
    "^manage_cameras$|^back_to_cameras_settings$",
)
