import asyncio
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
    
    # Sort the queue
    temp.AUTO_RENAME_QUEUE[userId].sort(key=lambda x: x["file_name"])
    temp.USERS_IN_QUEUE.append(userId)

    queued_files = temp.AUTO_RENAME_QUEUE[userId]

    async def process_file_with_delay(index, file_item):
        # Introduce a delay based on the index within the group
        await asyncio.sleep(index * 5)
        try:
            await autoRenameFunc(
                client, message, file_item["format_template"], file_item["target_channel"],
                file_item["file_id"], file_item["file_name"], file_item["media_type"],
                int(file_item["message_id"]), int(file_item["to_edit"])
            )
        except Exception as e:
            await message.reply_text(f"> **Error** : {e}")

    try:
        for i in range(0, len(queued_files), 4):  # Process in chunks of 3
            group = queued_files[i:i + 4]
            tasks = [
                asyncio.create_task(process_file_with_delay(index, file_item))
                for index, file_item in enumerate(group)
            ]
            # Wait for the current group of tasks to complete
            await asyncio.gather(*tasks)
    except Exception as e:
        await message.reply_text(f"> **Error** : {e}")
    else:
        await message.reply_text(
            "<b>ᴀʟʟ ǫᴜᴇᴜᴇᴅ ғɪʟᴇs ʜᴀᴠᴇ ʙᴇᴇɴ sᴜᴄᴄᴇssғᴜʟʟʏ ʀᴇɴᴀᴍᴇᴅ. ✅</b>\n\n"
            "<b> 🍀 Developer </b> <a href=https://t.me/Snowball_official>ѕησωвαℓℓ ❄️</a>",
            disable_web_page_preview=True,
        )
    finally:
        # Clear the queue and remove user from the active users list
        del temp.AUTO_RENAME_QUEUE[userId]
        temp.USERS_IN_QUEUE.remove(userId)
