import models

TEXTS = {
    models.Language.ARABIC: {
        "welcome": "أهلاً بك...",
        "force_join": (
            f"لبدء استخدام البوت يجب عليك الانضمام الى قناة البوت أولاً\n\n"
            "اشترك أولاً 👇\n"
            "ثم اضغط <b>تحقق ✅</b>"
        ),
        "join_first": "قم بالاشتراك بالقناة أولاً ❗️",
        "settings": "الإعدادات ⚙️",
        "change_lang": "اختر اللغة 🌐",
        "change_lang_success": "تم تغيير اللغة بنجاح ✅",
        "home_page": "القائمة الرئيسية 🔝",
        "search_by": "البحث حسب: ",
        "no_cameras": "ليس لديك كاميرات بعد ❗️",
        "no_results": "لم يتم العثور على نتائج ❗️",
        "choose_camera": "اختر الكاميرا",
        "choose_option": "اختر أحد الخيارات أدناه",
        "cameras_settings": "إدارة الكاميرات 📷",
        "no_priv": "ليس لديك الصلاحيات الكافية ❗️",
        "delete_confirm": "<b>هل أنت متأكد من أنك تريد حذف هذه الكاميرا؟</b>",
        "choose_new_val": "اختر القيمة الجديدة",
        "status_update_alert": "تم تحديث حالة الكاميرا <code>{}</code> إلى <code>{}</code> 🚨",
        "new_cam_alert": "كاميرا جديدة <code>{}</code> تمت إضافتها 🚨",
        "cam_update_success": "تم تحديث الكاميرا بنجاح ✅",
        "choose_add_type": "كيف تريد إضافة الكاميرا؟",
        "send_inst_name": "أرسل اسم المؤسسة 📌",
        "send_cam_info": (
            "أرسل البيانات النصية للكاميرا ✏️\n\n"
            "مثال:\n"
            "<code>192.168.0.1_456_admin_admin_SN-xx00xx00xx00xx0_1</code>"
        ),
        "send_serial": (
            "سيكون اسم الكاميرا: <code>{}</code>\n"
            "أرسل الرقم التسلسلي\n"
            "<b>يجب أن يبدأ ب-SN</b>"
        ),
        "duplicate_serial": "رقم تسلسلي مكرر ❗️",
        "send_photos": (
            "أرسل صور الكاميرا 📸\n" "عند الانتهاء اضغط /get_photos_finish"
        ),
        "got_photo": (
            "تم استلام الصورة رقم <b>{}</b> ✅\n" "عند الانتهاء اضغط /get_photos_finish"
        ),
        "one_photo_at_least": "يجب إضافة صورة واحدة على الأقل ❗️",
        "send_ip": "أرسل عنوان IP",
        "send_port": "أرسل الport",
        "send_admin_user": ("أرسل الadmin user\n\n" "<i>اختياري</i>"),
        "send_admin_pass": "أرسل ال admin password",
        "send_user": ("أرسل الuser\n\n" "<i>اختياري</i>"),
        "send_user_pass": "أرسل الuser pass",
        "choose_cam_type": "اختر نوع الكاميرا",
        "choose_cam_status": "اختر حالة الكاميرا",
        "send_location": (
            "أرسل الموقع بالصيغة التالية: الدولة,المدينة\n"
            "مثال:\n"
            "<code>sa,abha</code>\n"
            "<i>يمكنك النقر على المثال لنسخه والاستبدال مع المحافظة على التنسيق</i>"
        ),
        "confirm_add_cam": (
            "هل أنت متأكد من إضافة هذه الكاميرا؟\n\n"
            "للإلغاء اضغط <b>العودة إلى القائمة الرئيسية 🔙</b>"
        ),
        "add_cam_success": "تمت إضافة الكاميرا بنجاح ✅",
        "add_cam_right_away": "يمكنك إضافة كاميرا أخرى مباشرة ⚡️\n",
        "duplicate_cam": "الكاميرا مضافة مسبقاً ⚠️",
        "wrong_format": "خطأ في التنسيق ⚠️",
        "analyze_info_success": f"تم تحليل البيانات ✅\n\n",
        "analyzing_info_wait": f"تحليل البيانات جارٍ، الرجاء الانتظار ⏳",
        "add_cam_fail": "خطأ أثناء تحليل البيانات يرجى إعادة المحاولة من جديد ❗️",
        "choose_update_field": "اختر حقلاً لتعديله",
        "search_by_serial": "أرسل الرقم التسلسلي",
        "search_by_ip": "أرسل عنوان الIP",
        "search_by_id": "أرسل رقم الكاميرا بين ",
    },
    models.Language.ENGLISH: {
        "welcome": "Welcome...",
        "force_join": (
            f"You have to join the bot's channel in order to be able to use it\n\n"
            "Join First 👇\n"
            "And then press <b>Verify ✅</b>"
        ),
        "join_first": "Join the channel first ❗️",
        "settings": "Settings ⚙️",
        "change_lang": "Choose a language 🌐",
        "change_lang_success": "Language changed ✅",
        "home_page": "Home page 🔝",
        "search_by": "Search By: ",
        "no_cameras": "You don't have any cameras yet ❗️",
        "no_results": "No results found ❗️",
        "choose_camera": "Choose Camera",
        "choose_option": "Choose one of the options below",
        "cameras_settings": "Cameras Settings 📷",
        "no_priv": "You don't have the privilage to do this ❗️",
        "delete_confirm": "<b>Are you sure you want to delete this camera?</b>",
        "choose_new_val": "Choose the new value",
        "status_update_alert": "Camera status updated <code>{}</code> to <code>{}</code> 🚨",
        "new_cam_alert": "New Camera <code>{}</code> Added 🚨",
        "cam_update_success": "Camera updated successfully ✅",
        "choose_add_type": "Choose add type",
        "send_inst_name": "Send the institution name 📌",
        "send_cam_info": (
            "Send the camera info ✏️\n\n"
            "e.g:\n"
            "<code>192.168.0.1_456_admin_admin_SN-xx00xx00xx00xx0_1</code>"
        ),
        "send_serial": (
            "Camera name will be: <code>{}</code>\n"
            "Send the serial number\n"
            "<b>it must start with a SN-</b>"
        ),
        "duplicate_serial": "Duplicate Serial Number ❗️",
        "send_photos": ("Send cam's photos 📸\n" "On finish press /get_photos_finish"),
        "got_photo": (
            "Got photo number <b>{}</b> ✅\n" "On finish press /get_photos_finish"
        ),
        "one_photo_at_least": "You must add at least one photo ❗️",
        "send_ip": "Send the IP address",
        "send_port": "Send the port number",
        "send_admin_user": ("Send the admin user\n\n" "<i>Optional</i>"),
        "send_admin_pass": "Send the admin password",
        "send_user": ("Send the user\n\n" "<i>Optional</i>"),
        "send_user_pass": "Send the user password",
        "choose_cam_type": "Choose Camera type",
        "choose_cam_status": "Choose Camera status",
        "send_location": (
            "Send the location in the following format: country,city\n"
            "e.g:\n"
            "<code>sa,abha</code>\n"
            "<i>You can click on the example to copy it</i>"
        ),
        "confirm_add_cam": (
            "Are you sure you want to add this camera?\n\n"
            "Press <b>Back to home page 🔙</b> to cancel."
        ),
        "add_cam_success": "Camera added successfully ✅",
        "add_cam_right_away": "You can add another camera right away ⚡️\n",
        "duplicate_cam": "Duplicate Camera ⚠️",
        "wrong_format": "Wrong format ⚠️",
        "analyze_info_success": f"Camera info analyzed successfully ✅\n\n",
        "analyzing_info_wait": f"Analyzing info, please wait ⏳",
        "add_cam_fail": "Error while adding camera, please try again ❗️",
        "choose_update_field": "Choose a field to update",
        "search_by_serial": "Send the Serial Number",
        "search_by_ip": "Send the IP Address",
        "search_by_id": "Send the Camera Number Between ",
    },
}

BUTTONS = {
    models.Language.ARABIC: {
        "check_joined": "تحقق ✅",
        "bot_channel": "قناة البوت 📢",
        "back_button": "الرجوع 🔙",
        "settings": "الإعدادات ⚙️",
        "lang": "اللغة 🌐",
        "back_to_home_page": "العودة إلى القائمة الرئيسية 🔙",
        "search_by_serial": "الرقم التسلسلي",
        "search_by_ip": "عنوان IP",
        "search_by_id": "رقم الكاميرا",
        "connected_status": "متصل",
        "disconnected_status": "غير متصل",
        "skip": "تخطي ⏭",
        "confirm_add_cam": "إضافة ➕",
        "manual_entry": "يدوياً 📝",
        "auto_entry": "تلقائياً ⚙️",
        "update_cam_status": "الحالة",
        "update_cam": "تعديل 🔄",
        "add_cam": "إضافة كاميرا 📷",
        "search_cams": "إضافة كاميرا 📷",
        "list_cams": "قائمة الكاميرات 📋",
        "manage_cameras": "إدارة الكاميرات 📷",
        "yes": "نعم 👍",
        "no": "لا 👎",
    },
    models.Language.ENGLISH: {
        "check_joined": "Verify ✅",
        "bot_channel": "Bot's Channel 📢",
        "back_button": "Back 🔙",
        "settings": "Settings ⚙️",
        "lang": "Language 🌐",
        "back_to_home_page": "Back to home page 🔙",
        "search_by_serial": "Serial Number",
        "search_by_ip": "IP Address",
        "search_by_id": "Camera Number",
        "connected_status": "Connected",
        "disconnected_status": "Disconnected",
        "skip": "Skip ⏭",
        "confirm_add_cam": "Add ➕",
        "manual_entry": "Manual 📝",
        "auto_entry": "Auto ⚙️",
        "update_cam_status": "Status",
        "update_cam": "Update 🔄",
        "add_cam": "Add Camera 📷",
        "search_cams": "Search 🔎",
        "list_cams": "List Cameras 📋",
        "manage_cameras": "Manage Cameras 📷",
        "yes": "Yes 👍",
        "no": "No 👎",
    },
}
