from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, User
from telegram.ext import ContextTypes
from telegram.constants import ChatType
import os
import uuid
from common.keyboards import build_request_buttons
from dotenv import load_dotenv
import models

load_dotenv()

import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
# if int(os.getenv("OWNER_ID")) != 755501092:
# logging.getLogger("httpx").setLevel(logging.WARNING)


def check_hidden_keyboard(context: ContextTypes.DEFAULT_TYPE):
    if (
        not context.user_data.get("request_keyboard_hidden", None)
        or not context.user_data["request_keyboard_hidden"]
    ):
        context.user_data["request_keyboard_hidden"] = False
        request_buttons = build_request_buttons()
        reply_markup = ReplyKeyboardMarkup(request_buttons, resize_keyboard=True)
    else:
        reply_markup = ReplyKeyboardRemove()
    return reply_markup


def uuid_generator():
    return uuid.uuid4().hex


def create_folders():
    os.makedirs("data", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)


async def invalid_callback_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == ChatType.PRIVATE:
        await update.callback_query.answer("انتهت صلاحية هذا الزر")


async def send_alert(
    msg: str,
    users: list[models.User | models.Admin],
    context: ContextTypes.DEFAULT_TYPE,
):
    # Deduplicate users based on user.id
    unique_users = {user.id: user for user in users}.values()

    for user in unique_users:
        try:
            await context.bot.send_message(
                chat_id=user.id,
                text=msg,
            )
        except:
            pass


def get_user_display_name(user, tagged: bool = False):
    if isinstance(user, User):
        return (
            f"@{user.username}"
            if user.username
            else (f"<code>{user.full_name}</code>" if tagged else user.full_name)
        )
    elif isinstance(user, models.User):
        return (
            f"@{user.username}"
            if user.username
            else (f"<code>{user.name}</code>" if tagged else user.name)
        )
