from telegram import Update, InlineKeyboardButton, Chat
from telegram.ext import ContextTypes, CallbackQueryHandler, ConversationHandler
from common.decorators import check_if_user_member_decorator
from common.keyboards import build_user_keyboard, build_admin_keyboard
from common.constants import *
from common.lang_dicts import *
from custom_filters import Admin, User


back_to_admin_home_page_button = [
    [
        InlineKeyboardButton(
            text=BACK_TO_HOME_PAGE_TEXT,
            callback_data="back to admin home page",
        )
    ],
]


# @check_if_user_member_decorator
async def back_to_user_home_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and User().filter(update):
        lang = context.user_data.get("lang", models.Language.ARABIC)
        try:
            await update.callback_query.edit_message_text(
                text=TEXTS[lang]["home_page"],
                reply_markup=build_user_keyboard(lang=lang),
            )
        except:
            await update.callback_query.delete_message()
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=TEXTS[lang]["home_page"],
                reply_markup=build_user_keyboard(lang=lang),
            )
        return ConversationHandler.END


async def back_to_admin_home_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        if not is_admin:
            return await back_to_user_home_page(update=update, context=context)
        try:
            await update.callback_query.edit_message_text(
                text=HOME_PAGE_TEXT,
                reply_markup=build_admin_keyboard(),
            )
        except:
            await update.callback_query.delete_message()
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=HOME_PAGE_TEXT,
                reply_markup=build_admin_keyboard(),
            )
        return ConversationHandler.END


back_to_user_home_page_handler = CallbackQueryHandler(
    back_to_user_home_page, "^back_to_user_home_page$"
)
back_to_admin_home_page_handler = CallbackQueryHandler(
    back_to_admin_home_page, "^back to admin home page$"
)
