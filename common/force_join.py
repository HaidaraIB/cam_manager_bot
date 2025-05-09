from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from telegram.constants import ChatMemberStatus
from common.keyboards import build_user_keyboard
from common.lang_dicts import *
import os


async def check_if_user_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_member = await context.bot.get_chat_member(
        chat_id=int(os.getenv("CHANNEL_ID")), user_id=update.effective_user.id
    )
    lang = context.user_data.get('lang', models.Language.ARABIC)
    if chat_member.status == ChatMemberStatus.LEFT:
        text = TEXTS[lang]['force_join']
        markup = InlineKeyboardMarkup.from_button(
            InlineKeyboardButton(text=BUTTONS[lang]['check_joined'], callback_data="check joined")
        )
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=text, reply_markup=markup
            )
        else:
            await update.message.reply_text(text=text, reply_markup=markup)
        return False
    return True


async def check_joined(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_memeber = await context.bot.get_chat_member(
        chat_id=int(os.getenv("CHANNEL_ID")), user_id=update.effective_user.id
    )
    lang = context.user_data.get('lang', models.Language.ARABIC)
    if chat_memeber.status == ChatMemberStatus.LEFT:
        await update.callback_query.answer(
            text=TEXTS[lang]['join_first'], show_alert=True
        )
        return
    await update.callback_query.edit_message_text(
        text=TEXTS[lang]['welcome'],
        reply_markup=build_user_keyboard(lang=lang),
    )


check_joined_handler = CallbackQueryHandler(
    callback=check_joined, pattern="^check joined$"
)
