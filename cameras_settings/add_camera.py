from telegram import (
    Update,
    Chat,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto,
    PhotoSize,
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
from cameras_settings.common import build_add_camera_methods_keyboard, stringify_cam
from cameras_settings.cameras_settings import cameras_settings_handler
from start import admin_command

from common.back_to_home_page import (
    back_to_admin_home_page_button,
    back_to_admin_home_page_handler,
    back_to_user_home_page_button,
    back_to_user_home_page_handler,
)
from common.constants import *
from common.keyboards import build_back_button
import models
import pathlib
import os
import re
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
        keyboard = build_add_camera_methods_keyboard()
        keyboard.append(build_back_button("back_to_cameras_settings"))
        keyboard.append(
            back_to_admin_home_page_button[0]
            if is_admin
            else back_to_user_home_page_button[0]
        )
        await update.callback_query.edit_message_text(
            text="كيف تريد إضافة الكاميرا؟",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return ENTRY_TYPE


async def choose_entry_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        back_buttons = [
            build_back_button("back_to_choose_entry_type"),
            (
                back_to_admin_home_page_button[0]
                if is_admin
                else back_to_user_home_page_button[0]
            ),
        ]
        if not update.callback_query.data.startswith("back"):
            add_cam_type = update.callback_query.data
            context.user_data["entry_type"] = add_cam_type
        else:
            add_cam_type = context.user_data["entry_type"]

        if add_cam_type == "manual_entry":
            await update.callback_query.edit_message_text(
                text="أرسل اسم المؤسسة 📌",
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
            return INSTITUTION
        elif add_cam_type == "auto_entry":
            await update.callback_query.edit_message_text(
                text=(
                    "أرسل البيانات النصية للكاميرا ✏️\n\n"
                    "مثال:\n"
                    "<code>192.168.0.1_456_admin_admin_SN-xx00xx00xx00xx0_1</code>"
                ),
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
            return CAM_INFO


back_to_choose_entry_type = add_camera


async def get_institution(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        back_buttons = [
            build_back_button("back_to_get_institution"),
            (
                back_to_admin_home_page_button[0]
                if is_admin
                else back_to_user_home_page_button[0]
            ),
        ]
        last_cam = models.Camera.get_by(last=True)
        last_cam_id = last_cam.id if last_cam else 0
        if update.message:
            inst = update.message.text
            name = f"Cam_{str(last_cam_id + 1).rjust(3, '0')}_{inst}"
            context.user_data["name"] = name
            await update.message.reply_text(
                text=(
                    f"سيكون اسم الكاميرا: <code>{name}</code>\n"
                    "أرسل الرقم التسلسلي\n"
                    "<b>يجب أن يبدأ ب-SN</b>"
                ),
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
        else:
            name = context.user_data["name"]
            await update.callback_query.edit_message_text(
                text=(
                    f"سيكون اسم الكاميرا: <code>{name}</code>\n"
                    "أرسل الرقم التسلسلي\n"
                    "<b>يجب أن يبدأ ب-SN</b>"
                ),
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
        return SERIAL


back_to_get_institution = choose_entry_type


async def get_serial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        back_buttons = [
            build_back_button("back_to_get_serial"),
            (
                back_to_admin_home_page_button[0]
                if is_admin
                else back_to_user_home_page_button[0]
            ),
        ]
        if update.message:
            serial = update.message.text
            if models.Camera.get_by(attr="serial", val=serial):
                await update.message.reply_text(
                    text="رقم تسلسلي مكرر ❗️",
                )
                return
            context.user_data["serial"] = serial
            context.user_data["temp_photos"] = []
            await update.message.reply_text(
                text=(
                    "أرسل صور الكاميرا 📸\n"
                    "<b>ملاحظة:</b> أرسل صورة واحدة في كل مرة. عند الانتهاء اضغط /get_photos_finish"
                ),
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
        else:
            await update.callback_query.edit_message_text(
                text=(
                    "أرسل صور الكاميرا 📸\n"
                    "<b>ملاحظة:</b> أرسل صورة واحدة في كل مرة. عند الانتهاء اضغط /get_photos_finish"
                ),
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
        return PHOTOS


back_to_get_serial = get_institution


async def get_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        back_buttons = [
            build_back_button("back_to_get_serial"),
            (
                back_to_admin_home_page_button[0]
                if is_admin
                else back_to_user_home_page_button[0]
            ),
        ]
        photo = update.message.photo[-1]
        context.user_data["temp_photos"].append(
            {
                "file_id": photo.file_id,
                "file_unique_id": photo.file_unique_id,
                "width": photo.width,
                "height": photo.height,
            }
        )
        cam_photos_count = len(context.user_data["temp_photos"])

        await update.message.reply_text(
            text=(
                f"تم استلام الصورة رقم <b>{cam_photos_count}</b> ✅\n"
                "عند الانتهاء اضغط /get_photos_finish"
            ),
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )


async def get_photos_finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        back_buttons = [
            build_back_button("back_to_get_photos"),
            (
                back_to_admin_home_page_button[0]
                if is_admin
                else back_to_user_home_page_button[0]
            ),
        ]
        if update.message:
            if not context.user_data["temp_photos"]:
                await update.message.reply_text(text="يجب إضافة صورة واحدة على الأقل ❗️")
                return
            await update.message.reply_text(
                text="أرسل الip",
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
        else:
            await update.callback_query.edit_message_text(
                text="أرسل الip",
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
        return IP


back_to_get_photos = get_serial


async def get_ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        back_buttons = [
            build_back_button("back_to_get_ip"),
            (
                back_to_admin_home_page_button[0]
                if is_admin
                else back_to_user_home_page_button[0]
            ),
        ]
        if update.message:
            context.user_data["ip"] = update.message.text
            await update.message.reply_text(
                text="أرسل الport",
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
        else:
            await update.callback_query.edit_message_text(
                text="أرسل الport",
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )

        return PORT


back_to_get_ip = get_photos_finish


async def get_port(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        back_buttons = [
            [
                InlineKeyboardButton(
                    text="تخطي ⏭",
                    callback_data="skip_admin",
                )
            ],
            build_back_button("back_to_get_port"),
            (
                back_to_admin_home_page_button[0]
                if is_admin
                else back_to_user_home_page_button[0]
            ),
        ]
        if update.message:
            context.user_data["port"] = update.message.text
            await update.message.reply_text(
                text=("أرسل الadmin user\n\n" "<i>اختياري</i>"),
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
        else:
            await update.callback_query.edit_message_text(
                text=("أرسل الadmin user\n\n" "<i>اختياري</i>"),
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )

        return ADMIN_USER


back_to_get_port = get_ip


async def get_admin_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        back_buttons = [
            build_back_button("back_to_get_admin_user"),
            (
                back_to_admin_home_page_button[0]
                if is_admin
                else back_to_user_home_page_button[0]
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
                        text="تخطي ⏭",
                        callback_data="skip_admin",
                    )
                ],
                build_back_button("back_to_get_port"),
                back_to_admin_home_page_button[0],
            ]
            await update.callback_query.edit_message_text(
                text=("أرسل الadmin user\n\n" "<i>اختياري</i>"),
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
            return ADMIN_USER
        else:
            await update.callback_query.edit_message_text(
                text="أرسل الadmin password",
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
        return ADMIN_PASS


back_to_get_admin_user = get_port


async def get_admin_pass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        keyboard = [
            [
                InlineKeyboardButton(
                    text="تخطي ⏭",
                    callback_data="skip_user",
                )
            ],
            build_back_button("back_to_get_admin_pass"),
            (
                back_to_admin_home_page_button[0]
                if is_admin
                else back_to_user_home_page_button[0]
            ),
        ]
        if update.message:
            context.user_data["admin_pass"] = update.message.text
            await update.message.reply_text(
                text=("أرسل الuser\n\n" "<i>اختياري</i>"),
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        else:
            if update.callback_query.data == "skip_admin":
                context.user_data["admin_user"] = ""
                context.user_data["admin_pass"] = ""
            await update.callback_query.edit_message_text(
                text=("أرسل الuser\n\n" "<i>اختياري</i>"),
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        return USER


back_to_get_admin_pass = get_admin_user


async def get_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        if update.message or update.callback_query.data.startswith("back"):
            if update.message:
                back_buttons = [
                    build_back_button("back_to_get_user"),
                    (
                        back_to_admin_home_page_button[0]
                        if is_admin
                        else back_to_user_home_page_button[0]
                    ),
                ]
                context.user_data["user"] = update.message.text
                await update.message.reply_text(
                    text="أرسل الuser pass",
                    reply_markup=InlineKeyboardMarkup(back_buttons),
                )
                return USER_PASS
            else:
                keyboard = [
                    [
                        InlineKeyboardButton(
                            text="تخطي ⏭",
                            callback_data="skip_user",
                        )
                    ],
                    build_back_button("back_to_get_admin_pass"),
                    (
                        back_to_admin_home_page_button[0]
                        if is_admin
                        else back_to_user_home_page_button[0]
                    ),
                ]
                await update.callback_query.edit_message_text(
                    text="أرسل الuser\n\n" "<i>اختياري</i>",
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
                build_back_button("back_to_get_user"),
                (
                    back_to_admin_home_page_button[0]
                    if is_admin
                    else back_to_user_home_page_button[0]
                ),
            ]
            context.user_data["user"] = ""
            context.user_data["user_pass"] = ""
            await update.callback_query.edit_message_text(
                text="اختر نوع الكاميرا",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            return CAM_TYPE


back_to_get_user = get_admin_pass


async def get_user_pass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
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
            build_back_button("back_to_get_user_pass"),
            (
                back_to_admin_home_page_button[0]
                if is_admin
                else back_to_user_home_page_button[0]
            ),
        ]
        if update.message:
            context.user_data["user_pass"] = update.message.text
            await update.message.reply_text(
                text="اختر نوع الكاميرا",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        else:
            await update.callback_query.edit_message_text(
                text="اختر نوع الكاميرا",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        return CAM_TYPE


back_to_get_user_pass = get_user


async def choose_cam_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        keyboard = [
            [
                InlineKeyboardButton(
                    text="متصل",
                    callback_data="connected",
                ),
                InlineKeyboardButton(
                    text="غير متصل",
                    callback_data="disconnected",
                ),
            ],
            build_back_button("back_to_choose_cam_type"),
            (
                back_to_admin_home_page_button[0]
                if is_admin
                else back_to_user_home_page_button[0]
            ),
        ]
        if not update.callback_query.data.startswith("back"):
            context.user_data["cam_type"] = update.callback_query.data
        await update.callback_query.edit_message_text(
            text="اختر حالة الكاميرا",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return STATUS


back_to_choose_cam_type = get_user_pass


async def choose_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        keyboard = [
            build_back_button("back_to_choose_status"),
            (
                back_to_admin_home_page_button[0]
                if is_admin
                else back_to_user_home_page_button[0]
            ),
        ]
        if not update.callback_query.data.startswith("back"):
            context.user_data["status"] = update.callback_query.data
            await update.callback_query.edit_message_text(
                text=(
                    "أرسل الموقع بالصيغة التالية: الدولة,المدينة\n"
                    "مثال:\n"
                    "<code>sa,abha</code>\n"
                    "<i>يمكنك النقر على المثال لنسخه والاستبدال مع المحافظة على التنسيق</i>"
                ),
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        else:
            await update.callback_query.delete_message()
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=(
                    "أرسل الموقع بالصيغة التالية: الدولة,المدينة\n"
                    "مثال:\n"
                    "<code>sa,abha</code>\n"
                    "<i>يمكنك النقر على المثال لنسخه والاستبدال مع المحافظة على التنسيق</i>"
                ),
                reply_markup=InlineKeyboardMarkup(keyboard),
            )

        return LOCATION


back_to_choose_status = choose_cam_type


async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        back_buttons = [
            [
                InlineKeyboardButton(
                    text="إضافة ➕",
                    callback_data="confirm_add_cam",
                )
            ],
            build_back_button("back_to_get_location"),
            (
                back_to_admin_home_page_button[0]
                if is_admin
                else back_to_user_home_page_button[0]
            ),
        ]
        if update.message:
            context.user_data["location"] = update.message.text
            await update.message.reply_media_group(
                media=[
                    InputMediaPhoto(
                        media=PhotoSize(
                            file_id=photo["file_id"],
                            file_unique_id=photo["file_unique_id"],
                            width=photo["width"],
                            height=photo["height"],
                        )
                    )
                    for photo in context.user_data["temp_photos"]
                ],
                caption=stringify_cam(cam_data=context.user_data, for_admin=is_admin),
            )
            await update.message.reply_text(
                text=(
                    "هل أنت متأكد من إضافة هذه الكاميرا؟\n\n"
                    + "للإلغاء عد إلى القائمة الرئيسية."
                ),
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
        return CONFIRM_ADD_CAM


back_to_get_location = choose_status


async def confirm_add_cam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        cam_id = await models.Camera.add(context.user_data)
        for i, p in enumerate(context.user_data["temp_photos"]):
            photo = await context.bot.get_file(file_id=p["file_id"])
            await photo.download_to_drive(
                pathlib.Path(f"uploads/{context.user_data['serial']}_{i + 1}.jpg")
            )
            archive_msg = await context.bot.send_photo(
                chat_id=int(os.getenv("PHOTOS_ARCHIVE")),
                photo=p["file_id"],
            )
            await models.CamPhoto.add(
                cam_id=cam_id,
                file_id=archive_msg.photo[-1].file_id,
                file_unique_id=archive_msg.photo[-1].file_unique_id,
                width=archive_msg.photo[-1].width,
                height=archive_msg.photo[-1].height,
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
                    msg=f"كاميرا جديدة <code>{context.user_data['name']}</code> تمت إضافتها 🚨",
                    users=users,
                    context=context,
                )
            )

        await update.callback_query.answer(
            text="تمت إضافة الكاميرا بنجاح ✅",
            show_alert=True,
        )
        await update.callback_query.edit_message_text(
            text="تمت إضافة الكاميرا بنجاح ✅"
        )
        return ConversationHandler.END


async def get_cam_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        back_buttons = [
            build_back_button("back_to_get_cam_info"),
            (
                back_to_admin_home_page_button[0]
                if is_admin
                else back_to_user_home_page_button[0]
            ),
        ]
        raw_cam_info: str = update.message.text
        context.user_data["raw_cam_info"] = raw_cam_info
        pattern = re.compile(
            r"(\d+\.\d+\.\d+\.\d+)_(\d+)_([\w\d]+)_([\w\d@]+)_(SN-[\w\d]+)_\d+"
        )
        match = pattern.match(raw_cam_info)

        ip, port, admin_user, admin_pass, serial_number = match.groups()
        if models.Camera.get_by(attr="serial", val=serial_number):
            await update.message.reply_text(
                text="الكاميرا مضافة مسبقاً ⚠️",
            )
            return
        last_cam = models.Camera.get_by(last=True)
        last_cam_id = last_cam.id if last_cam else 0
        name = f"Cam_{str(last_cam_id + 1).rjust(3, '0')}_cctv"

        cam_type = (
            "dahua"
            if port in ["37777", "80"]
            else "hikvision" if port in ["8000", "9000"] else "unknown"
        )
        context.user_data["name"] = name
        context.user_data["ip"] = ip
        context.user_data["port"] = port
        context.user_data["admin_user"] = admin_user
        context.user_data["admin_pass"] = admin_pass
        context.user_data["user"] = ""
        context.user_data["user_pass"] = ""
        context.user_data["cam_type"] = cam_type
        context.user_data["status"] = "connected"
        context.user_data["location"] = "N/A"
        context.user_data["serial"] = serial_number
        context.user_data["temp_photos"] = []

        await update.message.reply_text(
            text=(
                f"تم تحليل البيانات ✅\n\n"
                + stringify_cam(cam_data=context.user_data, for_admin=is_admin)
                + "\n\n"
                + "أرسل صور الكاميرا 📸\n"
                + "<b>ملاحظة:</b> أرسل صورة واحدة في كل مرة. عند الانتهاء اضغط /get_photos_finish"
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
        photo = update.message.photo[-1]
        context.user_data["temp_photos"].append(
            {
                "file_id": photo.file_id,
                "file_unique_id": photo.file_unique_id,
                "width": photo.width,
                "height": photo.height,
            }
        )
        cam_photos_count = len(context.user_data["temp_photos"])

        back_buttons = [
            build_back_button("back_to_get_cam_info"),
            (
                back_to_admin_home_page_button[0]
                if is_admin
                else back_to_user_home_page_button[0]
            ),
        ]

        await update.message.reply_text(
            text=(
                f"تم استلام الصورة رقم <b>{cam_photos_count}</b> ✅\n"
                "عند الانتهاء اضغط /get_photos_finish"
            ),
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )


async def get_photos_finish_in_auto_entry_mode(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        if not context.user_data["temp_photos"]:
            await update.message.reply_text(text="يجب إضافة صورة واحدة على الأقل ❗️")
            return
        cam_id = await models.Camera.add(cam_data=context.user_data)
        for i, p in enumerate(context.user_data["temp_photos"]):

            photo = await context.bot.get_file(file_id=p["file_id"])
            await photo.download_to_drive(
                pathlib.Path(f"uploads/{context.user_data['serial']}_{i + 1}.jpg")
            )
            archive_msg = await context.bot.send_photo(
                chat_id=int(os.getenv("PHOTOS_ARCHIVE")),
                photo=p["file_id"],
            )
            await models.CamPhoto.add(
                cam_id=cam_id,
                file_id=archive_msg.photo[-1].file_id,
                file_unique_id=archive_msg.photo[-1].file_unique_id,
                width=archive_msg.photo[-1].width,
                height=archive_msg.photo[-1].height,
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
                    msg=f"كاميرا جديدة <code>{context.user_data['name']}</code> تمت إضافتها 🚨",
                    users=users,
                    context=context,
                )
            )

        await update.message.reply_media_group(
            media=[
                InputMediaPhoto(
                    media=PhotoSize(
                        file_id=cam_photo.file_id,
                        file_unique_id=cam_photo.file_unique_id,
                        width=cam_photo.width,
                        height=cam_photo.height,
                    )
                )
                for cam_photo in cam_photos
            ],
            caption=(
                stringify_cam(cam_data=context.user_data, for_admin=is_admin)
                + "\n\nتمت إضافة الكاميرا بنجاح ✅"
            ),
        )
        return ConversationHandler.END


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
                    r"^(\d+\.\d+\.\d+\.\d+)_(\d+)_([\w\d]+)_([\w\d@]+)_(SN-[\w\d]+)_\d+$"
                ),
                callback=get_cam_info,
            )
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
