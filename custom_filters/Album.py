from telegram import Update
from telegram.ext.filters import UpdateFilter

class Album(UpdateFilter):

    def filter(self, update: Update):
        return update.message.photo and update.message.media_group_id
