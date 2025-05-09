from telegram import (
    Update,
    Chat,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto,
    InputMediaPhoto,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    CommandHandler,
    filters,
)
from custom_filters import Admin, User
from common.common import send_alert
from cameras_settings.common import (
    build_add_camera_methods_keyboard,
    stringify_cam,
    extract_cam_info,
    media_group_sender,
    CAM_INFO_PATTERN,
)
from cameras_settings.cameras_settings import cameras_settings_handler
from start import admin_command

from common.back_to_home_page import (
    back_to_admin_home_page_button,
    back_to_admin_home_page_handler,
    back_to_user_home_page_handler,
)
from common.constants import *
from common.keyboards import build_back_button, build_back_to_user_home_page_button
from common.lang_dicts import *
import pathlib
import os
import asyncio

(
    ENTRY_TYPE,
    INSTITUTION,
    CAM_INFO,
    PHOTOS_IN_AUTO_ENTRY_MODE,
    PHOTOS,
    IP,
    PORT,
    ADMIN_USER,
    ADMIN_PASS,
    USER,
    USER_PASS,
    SERIAL,
    CAM_TYPE,
    STATUS,
    LOCATION,
    CONFIRM_ADD_CAM,
) = range(16)


async def add_camera(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        lang = context.user_data.get("lang", models.Language.ARABIC)
        keyboard = build_add_camera_methods_keyboard(lang=lang)
        keyboard.append(build_back_button("back_to_cameras_settings", lang=lang))
        keyboard.append(
            back_to_admin_home_page_button[0]
            if is_admin
            else build_back_to_user_home_page_button(lang)[0]
        )
        await update.callback_query.edit_message_text(
            text=TEXTS[lang]["choose_add_type"],
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return ENTRY_TYPE


async def choose_entry_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        lang = context.user_data.get("lang", models.Language.ARABIC)
        back_buttons = [
            build_back_button("back_to_choose_entry_type", lang=lang),
            (
                back_to_admin_home_page_button[0]
                if is_admin
                else build_back_to_user_home_page_button(lang)[0]
            ),
        ]
        if not update.callback_query.data.startswith("back"):
            add_cam_type = update.callback_query.data
            context.user_data["entry_type"] = add_cam_type
        else:
            add_cam_type = context.user_data["entry_type"]
        context.user_data["photos"] = []

        if add_cam_type == "manual_entry":
            await update.callback_query.edit_message_text(
                text=TEXTS[lang]["send_inst_name"],
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
            return INSTITUTION
        elif add_cam_type == "auto_entry":
            await update.callback_query.edit_message_text(
                text=TEXTS[lang]["send_cam_info"],
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
            return CAM_INFO


back_to_choose_entry_type = add_camera


async def get_institution(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        lang = context.user_data.get("lang", models.Language.ARABIC)
        back_buttons = [
            build_back_button("back_to_get_institution", lang=lang),
            (
                back_to_admin_home_page_button[0]
                if is_admin
                else build_back_to_user_home_page_button(lang)[0]
            ),
        ]
        last_cam = models.Camera.get_by(last=True)
        last_cam_id = last_cam.id if last_cam else 0
        if update.message:
            inst = update.message.text
            name = f"Cam_{str(last_cam_id + 1).rjust(3, '0')}_{inst}"
            context.user_data["name"] = name
            await update.message.reply_text(
                text=TEXTS[lang]["send_serial"].format(name),
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
        else:
            name = context.user_data["name"]
            await update.callback_query.edit_message_text(
                text=TEXTS[lang]["send_serial"].format(name),
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
        return SERIAL


back_to_get_institution = choose_entry_type


async def get_serial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        lang = context.user_data.get("lang", models.Language.ARABIC)
        back_buttons = [
            build_back_button("back_to_get_serial", lang=lang),
            (
                back_to_admin_home_page_button[0]
                if is_admin
                else build_back_to_user_home_page_button(lang)[0]
            ),
        ]
        if update.message:
            serial = update.message.text[3:]
            if models.Camera.get_by(attr="serial", val=serial):
                await update.message.reply_text(
                    text=TEXTS[lang]["duplicate_serial"],
                )
                return
            context.user_data["serial"] = serial
            await update.message.reply_text(
                text=TEXTS[lang]["send_photos"],
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
        else:
            await update.callback_query.edit_message_text(
                text=TEXTS[lang]["send_photos"],
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
        return PHOTOS


back_to_get_serial = get_institution


async def get_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        lang = context.user_data.get("lang", models.Language.ARABIC)
        back_buttons = [
            build_back_button("back_to_get_serial", lang=lang),
            (
                back_to_admin_home_page_button[0]
                if is_admin
                else build_back_to_user_home_page_button(lang)[0]
            ),
        ]
        photo = update.message.photo[-1]
        context.user_data["photos"].append(photo.file_id)
        cam_photos_count = len(context.user_data["photos"])

        await update.message.reply_text(
            text=TEXTS[lang]["got_photo"].format(cam_photos_count),
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )


async def get_photos_finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        lang = context.user_data.get("lang", models.Language.ARABIC)
        back_buttons = [
            build_back_button("back_to_get_photos", lang=lang),
            (
                back_to_admin_home_page_button[0]
                if is_admin
                else build_back_to_user_home_page_button(lang)[0]
            ),
        ]
        if update.message:
            if not context.user_data["photos"]:
                await update.message.reply_text(text=TEXTS[lang]["one_photo_at_least"])
                return
            await update.message.reply_text(
                text=TEXTS[lang]["send_ip"],
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
        else:
            await update.callback_query.edit_message_text(
                text=TEXTS[lang]["send_ip"],
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
        return IP


back_to_get_photos = get_serial


async def get_ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        lang = context.user_data.get("lang", models.Language.ARABIC)
        back_buttons = [
            build_back_button("back_to_get_ip", lang=lang),
            (
                back_to_admin_home_page_button[0]
                if is_admin
                else build_back_to_user_home_page_button(lang)[0]
            ),
        ]
        if update.message:
            context.user_data["ip"] = update.message.text
            await update.message.reply_text(
                text=TEXTS[lang]["send_port"],
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
        else:
            await update.callback_query.edit_message_text(
                text=TEXTS[lang]["send_port"],
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )

        return PORT


back_to_get_ip = get_photos_finish


async def get_port(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        lang = context.user_data.get("lang", models.Language.ARABIC)
        back_buttons = [
            [
                InlineKeyboardButton(
                    text=BUTTONS[lang]["skip"],
                    callback_data="skip_admin",
                )
            ],
            build_back_button("back_to_get_port", lang=lang),
            (
                back_to_admin_home_page_button[0]
                if is_admin
                else build_back_to_user_home_page_button(lang)[0]
            ),
        ]
        if update.message:
            context.user_data["port"] = update.message.text
            await update.message.reply_text(
                text=TEXTS[lang]["send_admin_user"],
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
        else:
            await update.callback_query.edit_message_text(
                text=TEXTS[lang]["send_admin_user"],
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )

        return ADMIN_USER


back_to_get_port = get_ip


async def get_admin_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        lang = context.user_data.get("lang", models.Language.ARABIC)
        back_buttons = [
            build_back_button("back_to_get_admin_user", lang=lang),
            (
                back_to_admin_home_page_button[0]
                if is_admin
                else build_back_to_user_home_page_button(lang)[0]
            ),
        ]
        if update.message:
            context.user_data["admin_user"] = update.message.text
            await update.message.reply_text(
                text="أرسل الadmin password",
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
        elif not context.user_data.get("admin_user", ""):
            back_buttons = [
                [
                    InlineKeyboardButton(
                        text=BUTTONS[lang]["skip"],
                        callback_data="skip_admin",
                    )
                ],
                build_back_button("back_to_get_port", lang=lang),
                back_to_admin_home_page_button[0],
            ]
            await update.callback_query.edit_message_text(
                text=TEXTS[lang]["send_admin_user"],
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
            return ADMIN_USER
        else:
            await update.callback_query.edit_message_text(
                text=TEXTS[lang]["send_admin_pass"],
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
        return ADMIN_PASS


back_to_get_admin_user = get_port


async def get_admin_pass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        lang = context.user_data.get("lang", models.Language.ARABIC)
        keyboard = [
            [
                InlineKeyboardButton(
                    text=BUTTONS[lang]["skip"],
                    callback_data="skip_user",
                )
            ],
            build_back_button("back_to_get_admin_pass", lang=lang),
            (
                back_to_admin_home_page_button[0]
                if is_admin
                else build_back_to_user_home_page_button(lang)[0]
            ),
        ]
        if update.message:
            context.user_data["admin_pass"] = update.message.text
            await update.message.reply_text(
                text=TEXTS[lang]["send_user"],
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        else:
            if update.callback_query.data == "skip_admin":
                context.user_data["admin_user"] = ""
                context.user_data["admin_pass"] = ""
            await update.callback_query.edit_message_text(
                text=TEXTS[lang]["send_user"],
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        return USER


back_to_get_admin_pass = get_admin_user


async def get_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        lang = context.user_data.get("lang", models.Language.ARABIC)
        if update.message or update.callback_query.data.startswith("back"):
            if update.message:
                back_buttons = [
                    build_back_button("back_to_get_user", lang=lang),
                    (
                        back_to_admin_home_page_button[0]
                        if is_admin
                        else build_back_to_user_home_page_button(lang)[0]
                    ),
                ]
                context.user_data["user"] = update.message.text
                await update.message.reply_text(
                    text=TEXTS[lang]["send_user_pass"],
                    reply_markup=InlineKeyboardMarkup(back_buttons),
                )
                return USER_PASS
            else:
                keyboard = [
                    [
                        InlineKeyboardButton(
                            text=BUTTONS[lang]["skip"],
                            callback_data="skip_user",
                        )
                    ],
                    build_back_button("back_to_get_admin_pass", lang=lang),
                    (
                        back_to_admin_home_page_button[0]
                        if is_admin
                        else build_back_to_user_home_page_button(lang)[0]
                    ),
                ]
                await update.callback_query.edit_message_text(
                    text=TEXTS[lang]["send_user"],
                    reply_markup=InlineKeyboardMarkup(keyboard),
                )
                return USER

        elif update.callback_query.data == "skip_user":
            keyboard = [
                [
                    InlineKeyboardButton(
                        text="37777,80 (dahua)",
                        callback_data="dahua",
                    ),
                    InlineKeyboardButton(
                        text="9000-8000 (hikvision)",
                        callback_data="hikvision",
                    ),
                ],
                build_back_button("back_to_get_user", lang=lang),
                (
                    back_to_admin_home_page_button[0]
                    if is_admin
                    else build_back_to_user_home_page_button(lang)[0]
                ),
            ]
            context.user_data["user"] = ""
            context.user_data["user_pass"] = ""
            await update.callback_query.edit_message_text(
                text=TEXTS[lang]["choose_cam_type"],
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            return CAM_TYPE


back_to_get_user = get_admin_pass


async def get_user_pass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        lang = context.user_data.get("lang", models.Language.ARABIC)
        keyboard = [
            [
                InlineKeyboardButton(
                    text="37777,80 (dahua)",
                    callback_data="dahua",
                ),
                InlineKeyboardButton(
                    text="9000-8000 (hikvision)",
                    callback_data="hikvision",
                ),
            ],
            build_back_button("back_to_get_user_pass", lang=lang),
            (
                back_to_admin_home_page_button[0]
                if is_admin
                else build_back_to_user_home_page_button(lang)[0]
            ),
        ]
        if update.message:
            context.user_data["user_pass"] = update.message.text
            await update.message.reply_text(
                text=TEXTS[lang]["choose_cam_type"],
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        else:
            await update.callback_query.edit_message_text(
                text=TEXTS[lang]["choose_cam_type"],
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        return CAM_TYPE


back_to_get_user_pass = get_user


async def choose_cam_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        lang = context.user_data.get("lang", models.Language.ARABIC)
        keyboard = [
            [
                InlineKeyboardButton(
                    text=BUTTONS[lang]["connected_status"],
                    callback_data="connected",
                ),
                InlineKeyboardButton(
                    text=BUTTONS[lang]["disconnected_status"],
                    callback_data="disconnected",
                ),
            ],
            build_back_button("back_to_choose_cam_type", lang=lang),
            (
                back_to_admin_home_page_button[0]
                if is_admin
                else build_back_to_user_home_page_button(lang)[0]
            ),
        ]
        if not update.callback_query.data.startswith("back"):
            context.user_data["cam_type"] = update.callback_query.data
        await update.callback_query.edit_message_text(
            text=TEXTS[lang]["choose_cam_status"],
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return STATUS


back_to_choose_cam_type = get_user_pass


async def choose_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        lang = context.user_data.get("lang", models.Language.ARABIC)
        keyboard = [
            build_back_button("back_to_choose_status", lang=lang),
            (
                back_to_admin_home_page_button[0]
                if is_admin
                else build_back_to_user_home_page_button(lang)[0]
            ),
        ]
        if not update.callback_query.data.startswith("back"):
            context.user_data["status"] = update.callback_query.data
            await update.callback_query.edit_message_text(
                text=TEXTS[lang]["send_location"],
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        else:
            await update.callback_query.delete_message()
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=TEXTS[lang]["send_location"],
                reply_markup=InlineKeyboardMarkup(keyboard),
            )

        return LOCATION


back_to_choose_status = choose_cam_type


async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        lang = context.user_data.get("lang", models.Language.ARABIC)
        back_buttons = [
            [
                InlineKeyboardButton(
                    text=BUTTONS[lang]["confirm_add_cam"],
                    callback_data="confirm_add_cam",
                )
            ],
            build_back_button("back_to_get_location", lang=lang),
            (
                back_to_admin_home_page_button[0]
                if is_admin
                else build_back_to_user_home_page_button(lang)[0]
            ),
        ]
        if update.message:
            context.user_data["location"] = update.message.text
            await update.message.reply_media_group(
                media=[
                    InputMediaPhoto(media=file_id)
                    for file_id in context.user_data["photos"]
                ],
                caption=stringify_cam(cam_data=context.user_data, for_admin=is_admin),
            )
            await update.message.reply_text(
                text=TEXTS[lang]["confirm_add_cam"],
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
        return CONFIRM_ADD_CAM


back_to_get_location = choose_status


async def confirm_add_cam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        lang = context.user_data.get("lang", models.Language.ARABIC)
        cam_id = await models.Camera.add(context.user_data)
        for i, file_id in enumerate(context.user_data["photos"]):
            photo = await context.bot.get_file(file_id=file_id)
            path = await photo.download_to_drive(
                pathlib.Path(f"uploads/{context.user_data['serial']}_{i + 1}.jpg")
            )
            archive_msg = await context.bot.send_photo(
                chat_id=int(os.getenv("PHOTOS_ARCHIVE")),
                photo=file_id,
            )
            await models.CamPhoto.add(
                cam_id=cam_id,
                path=str(path),
                file_id=archive_msg.photo[-1].file_id,
            )

        add_cam_alert = models.Alert.get_by(
            attr="alert_type", val=models.AlertType.ADD_CAM
        )
        if add_cam_alert.is_on and add_cam_alert.dest != models.AlertDest.NONE:
            if add_cam_alert.dest == models.AlertDest.BOTH:
                users = models.Admin.get_admin_ids() + models.User.get_users()
            elif add_cam_alert.dest == models.AlertDest.ADMINS:
                users = models.Admin.get_admin_ids()
            elif add_cam_alert.dest == models.AlertDest.USERS:
                users = models.User.get_users()
            asyncio.create_task(
                send_alert(
                    msg=TEXTS[lang]["new_cam_alert"].format(context.user_data["name"]),
                    users=users,
                    context=context,
                )
            )
        context.user_data["photos"] = []
        await update.callback_query.answer(
            text=TEXTS[lang]["add_cam_success"],
            show_alert=True,
        )
        await update.callback_query.edit_message_text(
            text=TEXTS[lang]["add_cam_success"],
        )
        if context.user_data["entry_type"] == "auto_entry":
            back_buttons = [
                build_back_button("back_to_choose_entry_type", lang=lang),
                (
                    back_to_admin_home_page_button[0]
                    if is_admin
                    else build_back_to_user_home_page_button(lang)[0]
                ),
            ]
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=TEXTS[lang]["add_cam_right_away"] + TEXTS[lang]["send_cam_info"],
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
            return CAM_INFO
        return ConversationHandler.END


async def get_cam_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        lang = context.user_data.get("lang", models.Language.ARABIC)
        back_buttons = [
            build_back_button("back_to_get_cam_info", lang=lang),
            (
                back_to_admin_home_page_button[0]
                if is_admin
                else build_back_to_user_home_page_button(lang)[0]
            ),
        ]
        res = await extract_cam_info(
            raw_cam_info=update.message.text,
            context=context,
            chat_id=update.effective_chat.id,
        )
        if res == "duplicate":
            await update.message.reply_text(text=TEXTS[lang]["duplicate_camera"])
            return
        elif res == "no match":
            await update.message.reply_text(text=TEXTS[lang]["wrong_format"])
            return

        await update.message.reply_text(
            text=(
                TEXTS[lang]["analyze_info_success"]
                + stringify_cam(cam_data=context.user_data, for_admin=is_admin)
                + "\n\n"
                + TEXTS[lang]["send_photos"]
            ),
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )
        return PHOTOS_IN_AUTO_ENTRY_MODE


back_to_get_cam_info = choose_entry_type


async def get_photos_in_auto_entry_mode(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        lang = context.user_data.get("lang", models.Language.ARABIC)
        photo = update.message.photo[-1]
        context.user_data["photos"].append(photo.file_id)
        cam_photos_count = len(context.user_data["photos"])

        back_buttons = [
            build_back_button("back_to_get_cam_info", lang=lang),
            (
                back_to_admin_home_page_button[0]
                if is_admin
                else build_back_to_user_home_page_button(lang)[0]
            ),
        ]

        await update.message.reply_text(
            text=TEXTS[lang]["got_photo"].format(cam_photos_count),
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )


async def get_photos_finish_in_auto_entry_mode(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        lang = context.user_data.get("lang", models.Language.ARABIC)
        if not context.user_data["photos"]:
            await update.message.reply_text(text=TEXTS[lang]["one_photo_at_least"])
            return
        cam_id = await models.Camera.add(cam_data=context.user_data)
        for i, file_id in enumerate(context.user_data["photos"]):

            photo = await context.bot.get_file(file_id=file_id)
            path = await photo.download_to_drive(
                pathlib.Path(f"uploads/{context.user_data['serial']}_{i + 1}.jpg")
            )
            archive_msg = await context.bot.send_photo(
                chat_id=int(os.getenv("PHOTOS_ARCHIVE")),
                photo=file_id,
            )
            await models.CamPhoto.add(
                cam_id=cam_id,
                path=str(path),
                file_id=archive_msg.photo[-1].file_id,
            )
        cam_photos = models.CamPhoto.get_by(attr="cam_id", val=cam_id, all=True)

        add_cam_alert = models.Alert.get_by(
            attr="alert_type", val=models.AlertType.ADD_CAM
        )
        if add_cam_alert.is_on and add_cam_alert.dest != models.AlertDest.NONE:
            if add_cam_alert.dest == models.AlertDest.BOTH:
                users = models.Admin.get_admin_ids() + models.User.get_users()
            elif add_cam_alert.dest == models.AlertDest.ADMINS:
                users = models.Admin.get_admin_ids()
            elif add_cam_alert.dest == models.AlertDest.USERS:
                users = models.User.get_users()
            asyncio.create_task(
                send_alert(
                    msg=TEXTS[lang]["new_cam_alert"].format(context.user_data["name"]),
                    users=users,
                    context=context,
                )
            )
        context.user_data["photos"] = []
        await update.message.reply_media_group(
            media=[
                InputMediaPhoto(media=cam_photo.file_id) for cam_photo in cam_photos
            ],
            caption=(
                stringify_cam(cam_data=context.user_data, for_admin=is_admin)
                + "\n\n"
                + TEXTS[lang]["add_cam_success"]
            ),
        )
        back_buttons = [
            build_back_button("back_to_choose_entry_type", lang=lang),
            (
                back_to_admin_home_page_button[0]
                if is_admin
                else build_back_to_user_home_page_button(lang)[0]
            ),
        ]
        await update.message.reply_text(
            text=(TEXTS[lang]["add_cam_right_away"] + TEXTS[lang]["get_cam_info"]),
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )
        return CAM_INFO


async def get_cam_info_with_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        lang = context.user_data.get("lang", models.Language.ARABIC)
        message = update.effective_message
        photo = message.photo[-1]
        photo_data = {"file_id": photo.file_id, "caption": message.caption}
        jobs = context.job_queue.get_jobs_by_name(str(message.media_group_id))
        if jobs:
            context.user_data["photos_data"].append(photo_data)
        else:
            context.user_data["photos_data"] = [photo_data]
            context.job_queue.run_once(
                callback=media_group_sender,
                when=10,
                data=is_admin,
                name=str(message.media_group_id),
                chat_id=update.effective_chat.id,
                user_id=update.effective_user.id,
            )
            await update.message.reply_text(text=TEXTS[lang]["analyzing_info_wait"])


add_camera_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            add_camera,
            "^add_camera$",
        )
    ],
    states={
        ENTRY_TYPE: [
            CallbackQueryHandler(
                choose_entry_type,
                "^((manual)|(auto))_entry$",
            )
        ],
        INSTITUTION: [
            MessageHandler(
                filters=filters.TEXT & ~filters.COMMAND,
                callback=get_institution,
            )
        ],
        CAM_INFO: [
            MessageHandler(
                filters=filters.Regex(
                    r"^{}$".format(CAM_INFO_PATTERN)
                    # {ip}_{port}_{username}_{password}_SN-{serial}_ID-{index}
                    # {ip}_{port}_{username}_{password}_SN-{serial}_ID-{index}_HD
                    # {ip}_{port}_{username}_{password}_SN-_ID-{index}
                ),
                callback=get_cam_info,
            ),
            MessageHandler(
                filters=filters.PHOTO,
                callback=get_cam_info_with_photos,
            ),
            CallbackQueryHandler(
                confirm_add_cam,
                "^confirm_add_cam$",
            ),
        ],
        PHOTOS_IN_AUTO_ENTRY_MODE: [
            MessageHandler(
                filters=filters.PHOTO,
                callback=get_photos_in_auto_entry_mode,
            ),
            CommandHandler(
                "get_photos_finish",
                get_photos_finish_in_auto_entry_mode,  # returns ConversationHandler.END
            ),
        ],
        SERIAL: [
            MessageHandler(
                filters=filters.Regex("^SN-.+$"),
                callback=get_serial,
            )
        ],
        PHOTOS: [
            MessageHandler(
                filters=filters.PHOTO,
                callback=get_photos,
            ),
            CommandHandler(
                "get_photos_finish",
                get_photos_finish,
            ),
        ],
        IP: [
            MessageHandler(
                filters=filters.Regex("^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$"),
                callback=get_ip,
            )
        ],
        PORT: [
            MessageHandler(
                filters=filters.Regex("^[0-9]+$"),
                callback=get_port,
            )
        ],
        ADMIN_USER: [
            MessageHandler(
                filters=filters.TEXT & ~filters.COMMAND,
                callback=get_admin_user,
            ),
            CallbackQueryHandler(get_admin_pass, "^skip_admin$"),
        ],
        ADMIN_PASS: [
            MessageHandler(
                filters=filters.TEXT & ~filters.COMMAND,
                callback=get_admin_pass,
            )
        ],
        USER: [
            MessageHandler(
                filters=filters.TEXT & ~filters.COMMAND,
                callback=get_user,
            ),
            CallbackQueryHandler(get_user, "^skip_user$"),
        ],
        USER_PASS: [
            MessageHandler(
                filters=filters.TEXT & ~filters.COMMAND,
                callback=get_user_pass,
            )
        ],
        CAM_TYPE: [
            CallbackQueryHandler(
                choose_cam_type,
                "^((hikvision)|(dahua))$",
            )
        ],
        STATUS: [
            CallbackQueryHandler(
                choose_status,
                "^((connected)|(disconnected))$",
            )
        ],
        LOCATION: [
            MessageHandler(
                filters=filters.Regex("^[a-zA-Z]+,[a-zA-Z]+$"),
                callback=get_location,
            )
        ],
        CONFIRM_ADD_CAM: [
            CallbackQueryHandler(
                confirm_add_cam,
                "^confirm_add_cam$",
            ),
        ],
    },
    fallbacks=[
        cameras_settings_handler,
        CallbackQueryHandler(back_to_choose_entry_type, "^back_to_choose_entry_type$"),
        CallbackQueryHandler(back_to_get_institution, "^back_to_get_institution$"),
        CallbackQueryHandler(back_to_get_cam_info, "^back_to_get_cam_info$"),
        CallbackQueryHandler(back_to_get_photos, "^back_to_get_photos$"),
        CallbackQueryHandler(back_to_get_ip, "^back_to_get_ip$"),
        CallbackQueryHandler(back_to_get_port, "^back_to_get_port$"),
        CallbackQueryHandler(back_to_get_admin_user, "^back_to_get_admin_user$"),
        CallbackQueryHandler(back_to_get_admin_pass, "^back_to_get_admin_pass$"),
        CallbackQueryHandler(back_to_get_user, "^back_to_get_user$"),
        CallbackQueryHandler(back_to_get_user_pass, "^back_to_get_user_pass$"),
        CallbackQueryHandler(back_to_get_serial, "^back_to_get_serial$"),
        CallbackQueryHandler(back_to_choose_cam_type, "^back_to_choose_cam_type$"),
        CallbackQueryHandler(back_to_choose_status, "^back_to_choose_status$"),
        CallbackQueryHandler(back_to_get_location, "^back_to_get_location$"),
        back_to_admin_home_page_handler,
        back_to_user_home_page_handler,
        admin_command,
    ],
    name="add_camera_conversation",
    persistent=True,
)
