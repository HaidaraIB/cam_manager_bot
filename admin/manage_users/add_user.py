from telegram import (
    Chat,
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButtonRequestUsers,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from common.common import send_alert, get_user_display_name
from common.back_to_home_page import back_to_admin_home_page_handler
from common.keyboards import build_admin_keyboard
from common.constants import *
from custom_filters import Admin
from admin.manage_users.manage_users import manage_users_handler
from start import admin_command
import models
import asyncio

NEW_USER_ID = 0


async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await update.callback_query.answer()
        await update.callback_query.delete_message()
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=(
                "اختر حساب المستخدم الذي تريد إضافته بالضغط على الزر أدناه\n\n"
                "يمكنك إلغاء العملية بالضغط على /admin."
            ),
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(
                            text="اختيار حساب مستخدم",
                            request_users=KeyboardButtonRequestUsers(
                                request_id=6, user_is_bot=False
                            ),
                        )
                    ]
                ],
                resize_keyboard=True,
            ),
        )
        return NEW_USER_ID


async def new_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.effective_message.users_shared:
            user = await context.bot.get_chat(
                chat_id=update.effective_message.users_shared.users[0].user_id
            )
        else:
            user = await context.bot.get_chat(chat_id=int(update.message.text))

        await models.User.add_new_user(
            user_id=user.id,
            username=user.username,
            name=user.full_name,
        )
        add_user_alert = models.Alert.get_by(
            attr="alert_type", val=models.AlertType.ADD_USER
        )
        if add_user_alert.is_on and add_user_alert.dest != models.AlertDest.NONE:
            asyncio.create_task(
                send_alert(
                    msg=f"مستخدم جديد {get_user_display_name(user=user, tagged=True)} تمت إضافته 🚨",
                    users=models.Admin.get_admin_ids(),
                    context=context,
                )
            )
        await update.message.reply_text(
            text="تمت إضافة المستخدم بنجاح ✅",
            reply_markup=ReplyKeyboardRemove(),
        )
        await update.message.reply_text(
            text=HOME_PAGE_TEXT,
            reply_markup=build_admin_keyboard(),
        )
        return ConversationHandler.END


add_user_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            callback=add_user,
            pattern="^add user$",
        ),
    ],
    states={
        NEW_USER_ID: [
            MessageHandler(
                filters=filters.Regex("^\d+$"),
                callback=new_user_id,
            ),
            MessageHandler(
                filters=filters.StatusUpdate.USERS_SHARED,
                callback=new_user_id,
            ),
        ]
    },
    fallbacks=[
        manage_users_handler,
        admin_command,
        back_to_admin_home_page_handler,
    ],
)
