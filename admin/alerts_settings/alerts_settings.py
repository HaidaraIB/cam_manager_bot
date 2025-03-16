from telegram import Chat, Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler
from custom_filters import Admin
import models
from admin.alerts_settings.common import (
    build_alert_types_keyboard,
    build_single_alert_settings_keyboard,
    update_alert,
)
from common.back_to_home_page import (
    back_to_admin_home_page_button,
    back_to_admin_home_page_handler,
)
from common.keyboards import build_back_button
from start import admin_command

ALERT_TYPE, UPDATE_OPTION = range(2)


async def alerts_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        keyboard = build_alert_types_keyboard()
        keyboard.append(back_to_admin_home_page_button[0])
        await update.callback_query.edit_message_text(
            text="إدارة التنبيهات ⚠️",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return ALERT_TYPE


async def choose_alert_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.callback_query.data.isnumeric():
            alert_id = int(update.callback_query.data)
            context.user_data["alert_id"] = alert_id
        else:
            alert_id = context.user_data["alert_id"]
            update_option = update.callback_query.data.replace("update_alert_", "")
            await update_alert(update_option=update_option, alert_id=alert_id)

        alert = models.Alert.get_by(attr="id", val=alert_id)

        keyboard = build_single_alert_settings_keyboard(alert=alert)
        keyboard.append(build_back_button("back_to_choose_alert_type"))
        keyboard.append(back_to_admin_home_page_button[0])
        await update.callback_query.edit_message_text(
            text=f"إعدادات تنبيه <b>{alert.alert_type.value['ar']}</b>",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

back_to_choose_alert_type = alerts_settings

alerts_settings_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            alerts_settings,
            "^manage_alerts$",
        ),
    ],
    states={
        ALERT_TYPE: [
            CallbackQueryHandler(
                choose_alert_type,
                "^[0-9]+$|^update_alert",
            ),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(back_to_choose_alert_type, "^back_to_choose_alert_type$"),
        admin_command,
        back_to_admin_home_page_handler,
    ],
)
