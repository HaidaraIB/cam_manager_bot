from telegram import Chat, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, ConversationHandler
from start import admin_command
from common.keyboards import build_back_button
from common.back_to_home_page import (
    back_to_admin_home_page_button,
    back_to_admin_home_page_handler,
)
from admin.manage_users.manage_users import manage_users_handler
from custom_filters import Admin
from common.constants import *
from common.common import get_user_display_name
import models


CHOOSE_USER_ID_TO_REMOVE = 0


async def remove_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.callback_query.data.isnumeric():
            user_id = int(update.callback_query.data)
            await models.User.delete(user_id=user_id)
            await update.callback_query.answer(text="تمت إزالة المستخدم بنجاح ✅")
        users = models.User.get_users()
        admin_ids_keyboard = [
            [
                InlineKeyboardButton(
                    text=get_user_display_name(user),
                    callback_data=str(user.id),
                ),
            ]
            for user in users
        ]
        admin_ids_keyboard.append(build_back_button("back_to_user_settings"))
        admin_ids_keyboard.append(back_to_admin_home_page_button[0])
        await update.callback_query.edit_message_text(
            text="اختر من القائمة أدناه المستخدم الذي تريد إزالته.",
            reply_markup=InlineKeyboardMarkup(admin_ids_keyboard),
        )
        return CHOOSE_USER_ID_TO_REMOVE


remove_user_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            callback=remove_user,
            pattern="^remove user$",
        ),
    ],
    states={
        CHOOSE_USER_ID_TO_REMOVE: [
            CallbackQueryHandler(
                remove_user,
                "^\d+$",
            ),
        ]
    },
    fallbacks=[
        manage_users_handler,
        admin_command,
        back_to_admin_home_page_handler,
    ],
)
