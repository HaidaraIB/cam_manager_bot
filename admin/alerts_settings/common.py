from telegram import InlineKeyboardButton
import models


def build_alert_types_keyboard() -> list[list[InlineKeyboardButton]]:
    keyboard = []
    alerts = models.Alert.get_by()
    for alert, alert_type in zip(alerts, models.AlertType):
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=alert_type.value["ar"] + (" 🟢" if alert.is_on else " 🔴"),
                    callback_data=alert.id,
                )
            ]
        )
    return keyboard


def build_single_alert_settings_keyboard(alert: models.Alert):
    keyboard = [
        [
            InlineKeyboardButton(
                text="تفعيل 🔴" if not alert.is_on else "إلغاء تفعيل 🟢",
                callback_data="update_alert_is_on",
            ),
        ],
        [
            InlineKeyboardButton(
                text=(
                    "مستخدمين "
                    + (
                        "🟢"
                        if alert.dest in [models.AlertDest.USERS, models.AlertDest.BOTH]
                        else "🔴"
                    )
                ),
                callback_data="update_alert_dest_users",
            ),
            InlineKeyboardButton(
                text=(
                    "آدمنز "
                    + (
                        "🟢"
                        if alert.dest
                        in [models.AlertDest.ADMINS, models.AlertDest.BOTH]
                        else "🔴"
                    )
                ),
                callback_data="update_alert_dest_admins",
            ),
        ],
    ]
    return keyboard


async def update_alert(update_option: str, alert_id: int):
    alert = models.Alert.get_by(attr="id", val=alert_id)
    if update_option == "is_on":
        await models.Alert.update(
            alert_id=alert.id,
            attrs=["is_on"],
            new_vals=[not alert.is_on],
        )
    elif update_option.startswith("dest"):
        await models.Alert.update(
            alert_id=alert.id,
            attrs=["dest"],
            new_vals=[
                (
                    models.AlertDest.BOTH
                    if (
                        (
                            alert.dest == models.AlertDest.ADMINS
                            and update_option.endswith("users")
                        )
                        or (
                            alert.dest == models.AlertDest.USERS
                            and update_option.endswith("admins")
                        )
                    )
                    else (
                        (
                            models.AlertDest.ADMINS
                            if (
                                (
                                    alert.dest == models.AlertDest.NONE
                                    and update_option.endswith("admins")
                                )
                                or (
                                    alert.dest == models.AlertDest.BOTH
                                    and update_option.endswith("users")
                                )
                            )
                            else (
                                models.AlertDest.USERS
                                if (
                                    (
                                        alert.dest == models.AlertDest.NONE
                                        and update_option.endswith("users")
                                    )
                                    or (
                                        alert.dest == models.AlertDest.BOTH
                                        and update_option.endswith("admins")
                                    )
                                )
                                else models.AlertDest.NONE
                            )
                        )
                    )
                )
            ],
        )
