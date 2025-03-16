from telegram import Chat, Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from common.keyboards import build_admin_keyboard
from common.common import get_user_display_name
from custom_filters import Admin
import models


async def show_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        users = models.User.get_users()
        text = "المستخدمين الحاليين:\n\n"
        for user in users:
            text += get_user_display_name(user=user, tagged=True)
        text += "\n" + "اختر ماذا تريد أن تفعل:"
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=build_admin_keyboard(),
        )


show_users_handler = CallbackQueryHandler(
    callback=show_users,
    pattern="^show users$",
)
