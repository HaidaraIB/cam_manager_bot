from telegram import Update
from telegram.ext import CallbackQueryHandler, InvalidCallbackData
from start import start_command, admin_command
from common.common import invalid_callback_data, create_folders
from common.back_to_home_page import (
    back_to_admin_home_page_handler,
    back_to_user_home_page_handler,
)
from common.error_handler import error_handler
from common.force_join import check_joined_handler

from user.user_calls import *
from user.user_settings import *

from admin.alerts_settings import *
from admin.admin_calls import *
from admin.admin_settings import *
from admin.manage_users import *
from admin.broadcast import *
from admin.ban import *
from cameras_settings import *

from models import create_tables

from MyApp import MyApp


def main():
    create_folders()
    create_tables()

    app = MyApp.build_app()

    app.add_handler(
        CallbackQueryHandler(
            callback=invalid_callback_data, pattern=InvalidCallbackData
        )
    )

    app.add_handler(user_settings_handler)
    app.add_handler(change_lang_handler)

    app.add_handler(add_camera_handler)
    app.add_handler(list_cameras_handler)
    app.add_handler(cameras_settings_handler)

    app.add_handler(alerts_settings_handler)

    # USER SETTINGS
    app.add_handler(manage_users_handler)
    app.add_handler(show_users_handler)
    app.add_handler(add_user_handler)
    app.add_handler(remove_user_handler)

    # ADMIN SETTINGS
    app.add_handler(admin_settings_handler)
    app.add_handler(show_admins_handler)
    app.add_handler(add_admin_handler)
    app.add_handler(remove_admin_handler)

    app.add_handler(broadcast_message_handler)

    app.add_handler(check_joined_handler)

    app.add_handler(ban_unban_user_handler)

    app.add_handler(admin_command)
    app.add_handler(start_command)
    app.add_handler(find_id_handler)
    app.add_handler(hide_ids_keyboard_handler)
    app.add_handler(back_to_user_home_page_handler)
    app.add_handler(back_to_admin_home_page_handler)

    app.add_error_handler(error_handler)

    app.run_polling(allowed_updates=Update.ALL_TYPES)
