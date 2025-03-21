from telegram import Update, Chat, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from custom_filters import Admin, User
import models
import re
import pathlib
import os
import asyncio
from common.keyboards import (
    build_keyboard,
    build_back_button,
    build_confirmation_keyboard,
)
from cameras_settings.common import (
    stringify_cam,
    build_single_camera_settings_keyboard,
    build_cameras_settings_keyboard,
    build_update_camera_keyboard,
    USER_UPDATE_CAM_CONSTRUCITONS,
    ADMIN_UPDATE_CAM_CONSTRUCTIONS,
)
from common.back_to_home_page import (
    back_to_admin_home_page_button,
    back_to_admin_home_page_handler,
    back_to_user_home_page_button,
    back_to_user_home_page_handler,
)
from common.common import send_alert
from cameras_settings.cameras_settings import cameras_settings_handler
from start import admin_command

(
    CAMERA,
    SETTING,
    CONFIRM_DELETE,
    UPDATE_SETTING,
    NEW_VAL,
    UPDATE_CAM_TYPE_AND_STATUS,
    CONFIRM_UPDATE,
) = range(7)


async def list_cameras(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        cameras = models.Camera.get_by(all=True)
        if not cameras:
            await update.callback_query.answer(
                text="ليس لديك كاميرات بعد ❗️",
                show_alert=True,
            )
            return ConversationHandler.END
        keyboard = build_keyboard(
            columns=1,
            texts=[cam.name for cam in cameras],
            buttons_data=[cam.id for cam in cameras],
        )
        keyboard.append(build_back_button("back_to_cameras_settings"))
        keyboard.append(
            back_to_admin_home_page_button[0]
            if is_admin
            else back_to_user_home_page_button[0]
        )
        await update.callback_query.delete_message()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="اختر الكاميرا",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return CAMERA


async def choose_camera(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        if not update.callback_query.data.startswith("back"):
            cam_id = int(update.callback_query.data)
            context.user_data["cam_id"] = cam_id
        else:
            cam_id = context.user_data["cam_id"]
        cam = models.Camera.get_by(attr="id", val=cam_id)
        keyboard = build_single_camera_settings_keyboard(for_admin=is_admin)
        keyboard.append(build_back_button("back_to_choose_camera"))
        keyboard.append(
            back_to_admin_home_page_button[0]
            if is_admin
            else back_to_user_home_page_button[0]
        )
        await update.callback_query.delete_message()
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=cam.photo,
            caption=stringify_cam(cam=cam, for_admin=is_admin),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return SETTING


back_to_choose_camera = list_cameras


async def choose_setting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        if not update.callback_query.data.startswith("back"):
            setting = update.callback_query.data
            context.user_data["chosen_setting"] = setting
        else:
            setting = context.user_data["chosen_setting"]

        if setting.startswith("update"):
            keyboard = build_update_camera_keyboard(for_admin=is_admin)
            keyboard.append(build_back_button("back_to_choose_setting"))
            keyboard.append(
                back_to_admin_home_page_button[0]
                if is_admin
                else back_to_user_home_page_button[0]
            )
            if update.effective_message.photo:
                await update.callback_query.edit_message_caption(
                    caption=(
                        update.effective_message.caption
                        + "\n\n"
                        + (
                            ADMIN_UPDATE_CAM_CONSTRUCTIONS
                            if is_admin
                            else USER_UPDATE_CAM_CONSTRUCITONS
                        )
                    ),
                    reply_markup=InlineKeyboardMarkup(keyboard),
                )
            else:
                await update.callback_query.delete_message()
            return UPDATE_SETTING
        elif setting.startswith("delete"):
            if not is_admin:
                await update.callback_query.answer(
                    text="ليس لديك الصلاحيات الكافية للحذف ❗️",
                    show_alert=True,
                )
                return
            keyboard = build_confirmation_keyboard(f"delete_camera")
            keyboard.append(build_back_button("back_to_choose_setting"))
            keyboard.append(back_to_admin_home_page_button[0])
            await update.callback_query.edit_message_caption(
                caption=(
                    update.effective_message.caption
                    + "\n\n<b>هل أنت متأكد من أنك تريد حذف هذه الكاميرا؟</b>"
                ),
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            return CONFIRM_DELETE


back_to_choose_setting = choose_camera


async def auto_update_camera(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        cam_id = context.user_data["cam_id"]
        cam = models.Camera.get_by(attr="id", val=cam_id)
        raw_cam_info = update.message.text
        context.user_data["raw_cam_info"] = raw_cam_info
        pattern = re.compile(
            r"(\d+\.\d+\.\d+\.\d+)_(\d+)_([\w\d]+)_([\w\d@]+)_(SN-[\w\d]+)_\d+"
        )
        match = pattern.match(raw_cam_info)

        ip, port, admin_user, admin_pass, serial_number = match.groups()

        cam_type = (
            "dahua"
            if port in ["37777", "80"]
            else "hikvision" if port in ["8000", "9000"] else "unknown"
        )
        context.user_data["name"] = cam.name
        context.user_data["ip"] = ip
        context.user_data["port"] = port
        context.user_data["admin_user"] = admin_user
        context.user_data["admin_pass"] = admin_pass
        context.user_data["user"] = cam.user
        context.user_data["user_pass"] = cam.user_password
        context.user_data["cam_type"] = cam_type
        context.user_data["status"] = cam.status
        context.user_data["location"] = cam.location
        context.user_data["serial"] = serial_number

        keyboard = build_confirmation_keyboard("update_camera")
        keyboard.append(build_back_button("back_to_auto_update_camera"))
        keyboard.append(back_to_admin_home_page_button[0])
        await update.message.reply_text(
            text=(
                f"تم تحليل البيانات ✅\n\n"
                + stringify_cam(cam_data=context.user_data, for_admin=True)
                + "\n\n"
                + "هل أنت متأكد من أنك تريد تحديث الكاميرا؟"
            ),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return CONFIRM_UPDATE


back_to_auto_update_camera = choose_setting


async def confirm_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        cam_id = context.user_data["cam_id"]
        if update.callback_query.data.startswith("yes"):
            await models.Camera.update(
                cam_id=cam_id,
                attrs=[
                    "ip",
                    "port",
                    "admin_user",
                    "admin_password",
                    "cam_type",
                    "serial",
                ],
                new_vals=[
                    context.user_data["ip"],
                    context.user_data["port"],
                    context.user_data["admin_user"],
                    context.user_data["admin_pass"],
                    context.user_data["cam_type"],
                    context.user_data["serial"],
                ],
            )
            await update_cam_success(
                update=update,
                context=context,
                cam_id=cam_id,
            )
            return SETTING
        else:
            keyboard = build_update_camera_keyboard(for_admin=True)
            keyboard.append(build_back_button("back_to_choose_setting"))
            keyboard.append(back_to_admin_home_page_button[0])
            await update.callback_query.edit_message_caption(
                caption=(
                    update.effective_message.caption
                    + "\n\n"
                    + ADMIN_UPDATE_CAM_CONSTRUCTIONS
                ),
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            return UPDATE_SETTING


async def choose_update_setting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        cam_id = context.user_data["cam_id"]
        cam = models.Camera.get_by(attr="id", val=cam_id)
        back_buttons = [
            build_back_button("back_to_choose_update_setting"),
            (
                back_to_admin_home_page_button[0]
                if is_admin
                else back_to_user_home_page_button[0]
            ),
        ]
        if not update.callback_query.data.startswith("back"):
            attr = update.callback_query.data.replace("update_cam_", "")
            context.user_data["attr_to_update"] = attr
        else:
            attr = context.user_data["attr_to_update"]

        if (attr != "status" and not is_admin) or (
            attr == "status" and not is_user and not is_admin
        ):
            await update.callback_query.answer(
                text="ليس لديك الصلاحيات الكافية لهذا التعديل ❗️",
                show_alert=True,
            )
            return

        if attr in ["cam_type", "status"]:
            if attr == "cam_type":
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
                    *back_buttons,
                ]
            else:
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
                    *back_buttons,
                ]
            await update.callback_query.edit_message_caption(
                caption=(
                    stringify_cam(cam=cam, for_admin=is_admin)
                    + "\n\nاختر القيمة الجديدة"
                ),
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            return UPDATE_CAM_TYPE_AND_STATUS

        await update.callback_query.answer()
        if attr == "photo":
            text = "أرسل الصورة الجديدة 🖼"
        else:
            text = (
                "أرسل القيمة الجديدة 🆕\n"
                f"القيمة الحالية هي: <code>{getattr(cam, attr)}</code>"
            )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )
        return NEW_VAL


back_to_choose_update_setting = choose_setting


async def get_new_val(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        attr = context.user_data["attr_to_update"]
        new_val = update.message.text
        pattern = None
        if attr == "ip":
            pattern = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$")
        elif attr == "port":
            pattern = re.compile(r"^[0-9]+$")
        elif attr == "serial":
            pattern = re.compile(r"^SN-.+$")
        elif attr == "location":
            pattern = re.compile(r"^[a-zA-Z]+,[a-zA-Z]+$")

        if pattern and not pattern.match(new_val):
            return

        cam_id = context.user_data["cam_id"]
        cam = models.Camera.get_by(attr="id", val=cam_id)
        if attr == "serial":
            if models.Camera.get_by(attr="serial", val=new_val):
                await update.message.reply_text(
                    text="رقم تسلسلي مكرر ❗️",
                )
                return
            else:
                os.rename(
                    src=pathlib.Path(f"uploads/{cam.serial}.jpg"),
                    dst=pathlib.Path(f"uploads/{new_val}.jpg"),
                )

        await models.Camera.update(
            cam_id=cam_id,
            attrs=[attr],
            new_vals=[new_val],
        )
        await update_cam_success(
            update=update,
            context=context,
            cam_id=cam_id,
        )
        return SETTING


async def get_new_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        cam_id = context.user_data["cam_id"]
        cam = models.Camera.get_by(attr="id", val=cam_id)
        photo = await context.bot.get_file(update.message.photo[-1].file_id)
        os.remove(pathlib.Path(f"uploads/{cam.serial}.jpg"))
        await photo.download_to_drive(pathlib.Path(f"uploads/{cam.serial}.jpg"))

        archive_msg = await context.bot.send_photo(
            chat_id=int(os.getenv("PHOTOS_ARCHIVE")),
            photo=update.message.photo[-1].file_id,
        )
        await models.Camera.update(
            cam_id=cam_id,
            attrs=["photo"],
            new_vals=[archive_msg.photo[-1].file_id],
        )
        await update_cam_success(
            update=update,
            context=context,
            cam_id=cam_id,
        )
        return SETTING


async def update_cam_type_and_status(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    is_admin = Admin().filter(update)
    is_user = User().filter(update)
    if update.effective_chat.type == Chat.PRIVATE and (is_admin or is_user):
        cam_id = context.user_data["cam_id"]
        cam = models.Camera.get_by(attr="id", val=cam_id)
        new_val = update.callback_query.data
        attr = "status" if new_val in ["connected", "disconnected"] else "cam_type"
        if not getattr(cam, attr) == new_val:
            await models.Camera.update(
                cam_id=cam_id,
                attrs=[attr],
                new_vals=[new_val],
            )
            status_update_alert = models.Alert.get_by(
                attr="alert_type", val=models.AlertType.STATUS_UPDATE
            )
            if (
                new_val in ["connected", "disconnected"]
                and status_update_alert.is_on
                and status_update_alert.dest != models.AlertDest.NONE
            ):
                if status_update_alert.dest == models.AlertDest.BOTH:
                    users = models.Admin.get_admin_ids() + models.User.get_users()
                elif status_update_alert.dest == models.AlertDest.ADMINS:
                    users = models.Admin.get_admin_ids()
                elif status_update_alert.dest == models.AlertDest.USERS:
                    users = models.User.get_users()
                asyncio.create_task(
                    send_alert(
                        msg=f"تم تحديث حالة الكاميرا <code>{cam.name}</code> إلى <code>{'متصل' if new_val=='connected' else 'غير متصل'}</code> 🚨",
                        users=users,
                        context=context,
                    )
                )
        await update.callback_query.answer(
            text="تم تحديث الكاميرا بنجاح ✅",
            show_alert=True,
        )
        await update.callback_query.delete_message()
        await update_cam_success(
            update=update,
            context=context,
            cam_id=cam_id,
        )
        return SETTING


async def confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        cam_id = context.user_data["cam_id"]
        cam = models.Camera.get_by(attr="id", val=cam_id)
        if update.callback_query.data.startswith("yes"):
            await models.Camera.delete(cam_id)
            await update.callback_query.answer(
                text="تم حذف الكاميرا بنجاح ✅",
                show_alert=True,
            )
            await update.callback_query.edit_message_caption(
                caption=(
                    stringify_cam(cam=cam, for_admin=True)
                    + "\n\nتم حذف الكاميرا بنجاح ✅"
                ),
            )
            cameras = models.Camera.get_by(all=True)
            if not cameras:
                keyboard = build_cameras_settings_keyboard()
                keyboard.append(back_to_admin_home_page_button[0])
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="إدارة الكاميرات 📷",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                )
                return ConversationHandler.END

            keyboard = build_keyboard(
                columns=1,
                texts=[cam.name for cam in cameras],
                buttons_data=[cam.id for cam in cameras],
            )
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="اختر الكاميرا",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            return CAMERA
        else:
            cam = models.Camera.get_by(attr="id", val=cam_id)
            keyboard = build_single_camera_settings_keyboard(for_admin=True)
            keyboard.append(build_back_button("back_to_choose_camera"))
            keyboard.append(back_to_admin_home_page_button[0])
            await update.callback_query.edit_message_caption(
                caption=stringify_cam(cam=cam, for_admin=True),
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            return SETTING


async def update_cam_success(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    cam_id: int,
):
    is_admin = Admin().filter(update)
    if update.message:
        await update.message.reply_text(text="تم تحديث الكاميرا بنجاح ✅")
    else:
        await update.callback_query.answer(
            text="تم تحديث الكاميرا بنجاح ✅",
            show_alert=True,
        )
    cam = models.Camera.get_by(attr="id", val=cam_id)
    keyboard = build_single_camera_settings_keyboard(for_admin=is_admin)
    keyboard.append(build_back_button("back_to_choose_camera"))
    keyboard.append(
        back_to_admin_home_page_button[0]
        if is_admin
        else back_to_user_home_page_button[0]
    )
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=cam.photo,
        caption=stringify_cam(cam=cam, for_admin=is_admin),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


list_cameras_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            list_cameras,
            "^list_cameras$",
        )
    ],
    states={
        CAMERA: [
            CallbackQueryHandler(
                choose_camera,
                "^[0-9]+$",
            ),
        ],
        SETTING: [
            CallbackQueryHandler(
                choose_setting,
                "^((update)|(delete))_cameras?$",
            ),
        ],
        CONFIRM_DELETE: [
            CallbackQueryHandler(
                confirm_delete,
                "^((yes)|(no))_delete_camera$",
            ),
        ],
        UPDATE_SETTING: [
            CallbackQueryHandler(
                choose_update_setting,
                "^update_cam",
            ),
            MessageHandler(
                filters=filters.Regex(
                    r"^(\d+\.\d+\.\d+\.\d+)_(\d+)_([\w\d]+)_([\w\d@]+)_(SN-[\w\d]+)_\d+$"
                ),
                callback=auto_update_camera,
            ),
        ],
        NEW_VAL: [
            MessageHandler(
                filters=filters.TEXT & ~filters.COMMAND,
                callback=get_new_val,
            ),
            MessageHandler(
                filters=filters.PHOTO,
                callback=get_new_photo,
            ),
        ],
        UPDATE_CAM_TYPE_AND_STATUS: [
            CallbackQueryHandler(
                update_cam_type_and_status,
                "^((hikvision)|(dahua)|(connected)|(disconnected))$",
            )
        ],
        CONFIRM_UPDATE: [
            CallbackQueryHandler(
                confirm_update,
                "^((yes)|(no))_update_camera$",
            ),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(back_to_choose_camera, "^back_to_choose_camera$"),
        CallbackQueryHandler(back_to_choose_setting, "^back_to_choose_setting$"),
        CallbackQueryHandler(
            back_to_auto_update_camera, "^back_to_auto_update_camera$"
        ),
        CallbackQueryHandler(
            back_to_choose_update_setting, "^back_to_choose_update_setting$"
        ),
        back_to_admin_home_page_handler,
        back_to_user_home_page_handler,
        cameras_settings_handler,
        admin_command,
    ],
    name="list_cameras_conversation",
    persistent=True,
)
