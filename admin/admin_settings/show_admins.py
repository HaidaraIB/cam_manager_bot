from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from common.keyboards import build_admin_keyboard
import os
import models


async def show_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admins = models.Admin.get_admin_ids()
    text = "آيديات الآدمنز الحاليين:\n\n"
    for admin in admins:
        if admin.id == int(os.getenv("OWNER_ID")):
            text += "<code>" + str(admin.id) + "</code>" + " <b>مالك البوت</b>\n"
            continue
        text += "<code>" + str(admin.id) + "</code>" + "\n"
    text += "\nاختر ماذا تريد أن تفعل:"
    await update.callback_query.edit_message_text(
        text=text,
        reply_markup=build_admin_keyboard(),
    )


show_admins_handler = CallbackQueryHandler(
    callback=show_admins,
    pattern="^show admins$",
)
