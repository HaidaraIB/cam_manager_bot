from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    KeyboardButtonRequestChat,
    KeyboardButtonRequestUsers,
)
from common.lang_dicts import *


def build_user_keyboard(lang: models.Language):
    keyboard = [
        [
            InlineKeyboardButton(
                text=BUTTONS[lang]["manage_cameras"],
                callback_data="manage_cameras",
            ),
        ],
        [
            InlineKeyboardButton(
                text=BUTTONS[lang]["settings"],
                callback_data="user_settings",
            ),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_admin_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                text="إعدادات الآدمن ⚙️🎛",
                callback_data="admin settings",
            ),
            InlineKeyboardButton(
                text="إعدادات المستخدم ⚙️👤",
                callback_data="user settings",
            ),
        ],
        [
            InlineKeyboardButton(
                text="حظر/فك حظر 🔓🔒",
                callback_data="ban unban",
            )
        ],
        # [
        #     InlineKeyboardButton(
        #         text="التقارير والمتابعة 📊",
        #         callback_data="manage_reports",
        #     ),
        #     InlineKeyboardButton(
        #         text="سجل النشاطات 📝",
        #         callback_data="manage_logs",
        #     ),
        # ],
        # [
        #     InlineKeyboardButton(
        #         text="استيراد وتصدير الكاميرات 📂",
        #         callback_data="import_export",
        #     )
        # ],
        [
            InlineKeyboardButton(
                text="إدارة الكاميرات 📷",
                callback_data="manage_cameras",
            ),
            InlineKeyboardButton(
                text="إدارة التنبيهات ⚠️",
                callback_data="manage_alerts",
            ),
        ],
        # [
        #     InlineKeyboardButton(
        #         text="التقارير 📊",
        #         callback_data="reports",
        #     )
        # ],
        [
            InlineKeyboardButton(
                text="إخفاء/إظهار كيبورد معرفة الآيديات 🪄",
                callback_data="hide ids keyboard",
            )
        ],
        [
            InlineKeyboardButton(
                text="رسالة جماعية 👥",
                callback_data="broadcast",
            )
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_back_button(data: str, lang: models.Language = models.Language.ARABIC):
    return [
        InlineKeyboardButton(
            text=BUTTONS[lang]["back_button"],
            callback_data=data,
        ),
    ]


def build_back_to_user_home_page_button(lang: models.Language = models.Language.ARABIC):
    button = [
        [
            InlineKeyboardButton(
                text=BUTTONS[lang]["back_to_home_page"],
                callback_data=f"back_to_user_home_page",
            )
        ],
    ]
    return button


def build_confirmation_keyboard(
    data: str, lang: models.Language = models.Language.ARABIC
):
    return [
        [
            InlineKeyboardButton(
                text=BUTTONS[lang]["yes"], callback_data=f"yes_{data}"
            ),
            InlineKeyboardButton(text=BUTTONS[lang]["no"], callback_data=f"no_{data}"),
        ]
    ]


def build_request_buttons():
    keyboard = [
        [
            KeyboardButton(
                text="معرفة id مستخدم 🆔",
                request_users=KeyboardButtonRequestUsers(
                    request_id=0, user_is_bot=False
                ),
            ),
            KeyboardButton(
                text="معرفة id قناة 📢",
                request_chat=KeyboardButtonRequestChat(
                    request_id=1, chat_is_channel=True
                ),
            ),
        ],
        [
            KeyboardButton(
                text="معرفة id مجموعة 👥",
                request_chat=KeyboardButtonRequestChat(
                    request_id=2, chat_is_channel=False
                ),
            ),
            KeyboardButton(
                text="معرفة id بوت 🤖",
                request_users=KeyboardButtonRequestUsers(
                    request_id=3, user_is_bot=True
                ),
            ),
        ],
    ]
    return keyboard


def build_keyboard(columns: int, texts, buttons_data):
    keyboard = []
    for i in range(0, len(buttons_data), columns):
        row = []
        for j in range(columns):
            try:
                row.append(
                    InlineKeyboardButton(
                        text=texts[i + j],
                        callback_data=buttons_data[i + j],
                    )
                )
            except IndexError:
                keyboard.append(row)
                return keyboard
        keyboard.append(row)
    return keyboard
