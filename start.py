from telegram import Update, Chat, BotCommandScopeChat
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    Application,
    ConversationHandler,
)
import os
import models
from custom_filters import Admin, User
from common.keyboards import build_user_keyboard, build_admin_keyboard
from common.common import check_hidden_keyboard
from common.lang_dicts import *
# from common.decorators import (
#     check_if_user_banned_dec,
#     add_new_user_dec,
#     check_if_user_member_decorator,
# )


async def inits(app: Application):
    await models.Admin.add_new_admin(admin_id=int(os.getenv("OWNER_ID")))
    for alert_type in models.AlertType:
        await models.Alert.add(alert_type=alert_type)


async def set_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    st_cmd = ("start", "start command")
    commands = [st_cmd]
    if Admin().filter(update):
        commands.append(("admin", "admin command"))
    await context.bot.set_my_commands(
        commands=commands, scope=BotCommandScopeChat(chat_id=update.effective_chat.id)
    )


# @add_new_user_dec
# @check_if_user_banned_dec
# @check_if_user_member_decorator
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        lang = context.user_data.get('lang', models.Language.ARABIC)
        await set_commands(update, context)
        await update.message.reply_text(
            text=TEXTS[lang]['welcome'],
            reply_markup=build_user_keyboard(lang=lang),
        )
        return ConversationHandler.END


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await set_commands(update, context)
        await update.message.reply_text(
            text="أهلاً بك...",
            reply_markup=check_hidden_keyboard(context),
        )

        await update.message.reply_text(
            text="تعمل الآن كآدمن 🕹",
            reply_markup=build_admin_keyboard(),
        )
        return ConversationHandler.END


start_command = CommandHandler(command="start", callback=start)
admin_command = CommandHandler(command="admin", callback=admin)
