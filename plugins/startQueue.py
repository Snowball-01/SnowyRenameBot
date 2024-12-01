import sys
from pyrogram import Client, filters
from pyrogram.types import Message
from config import temp
from utility.auto_rename_func import autoRenameFunc


@Client.on_message(filters.private & filters.command('start_queue'))
async def startQueue(client: Client, message: Message):
    
    userId = message.from_user.id

    if userId not in temp.AUTO_RENAME_QUEUE:
        return await message.reply_text("> ** Your queue is empty kindly add files before using this command **\n\n☞ __** How you can do that ? **__\n\n> ** First, enable the auto-rename feature to ensure proper file management. Then, upload files in the supported formats, and the bot will automatically add them to the processing queue. Once the files are queued, you can proceed with this command to complete the required action. **")
    
    if userId in temp.USERS_IN_QUEUE:
        return await message.reply_text("> ** Please wait for the current queue to complete before attempting to start a new one. **")
    
    temp.AUTO_RENAME_QUEUE[userId].sort(key= lambda x: x["file_name"])

    temp.USERS_IN_QUEUE.append(userId)
    for item in temp.AUTO_RENAME_QUEUE[userId]:
        try:
            await autoRenameFunc(client, message, item["format_template"], item["target_channel"], item["file_id"], item["file_name"], item["media_type"], int(item["message_id"]))
        except Exception as e:
            await message.reply_text(f"> **Error** : {e}")
            break
    
    await message.reply_text(
        "<b>ᴀʟʟ ǫᴜᴇᴜᴇᴅ ғɪʟᴇs ʜᴀᴠᴇ ʙᴇᴇɴ sᴜᴄᴄᴇssғᴜʟʟʏ ʀᴇɴᴀᴍᴇᴅ. ✅</b>\n\n"
        "<b> 🍀 Developer </b> <a href=https://t.me/Snowball_official>ѕησωвαℓℓ ❄️</a>",
        disable_web_page_preview=True,
    )
    ## Clearing Queues
    del temp.AUTO_RENAME_QUEUE[userId]
    temp.USERS_IN_QUEUE.remove(userId)
