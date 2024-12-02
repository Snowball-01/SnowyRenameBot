import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from config import temp
from utility.auto_rename_func import autoRenameFunc


@Client.on_message(filters.private & filters.command('start_queue'))
async def startQueue(client: Client, message: Message):
    userId = message.from_user.id

    if userId not in temp.AUTO_RENAME_QUEUE:
        return await message.reply_text(
            "> **Your queue is empty. Kindly add files before using this command.**\n\n"
            "☞ __**How to add files?**__\n\n"
            "> **First, enable the auto-rename feature. Then upload files in the supported formats. "
            "The bot will automatically add them to the processing queue. Once queued, use this command to process them.**"
        )

    if userId in temp.USERS_IN_QUEUE:
        return await message.reply_text(
            "> **Please wait for the current queue to complete before starting a new one.**"
        )

    # Sort the queue
    temp.AUTO_RENAME_QUEUE[userId].sort(key=lambda x: x["file_name"])
    temp.USERS_IN_QUEUE.append(userId)

    queued_files = temp.AUTO_RENAME_QUEUE[userId]
    success_count = 0
    failure_count = 0

    async def process_file_with_delay(index, file_item):
        nonlocal success_count, failure_count
        await asyncio.sleep(index * 5)
        retries = 3
        while retries > 0:
            try:
                await autoRenameFunc(
                    client, message, file_item["format_template"], file_item["target_channel"],
                    file_item["file_id"], file_item["file_name"], file_item["media_type"],
                    int(file_item["message_id"]), int(file_item["to_edit"])
                )
                success_count += 1
                break
            except Exception as e:
                retries -= 1
                if retries == 0:
                    failure_count += 1
                    await message.reply_text(f"> **Error processing file {file_item['file_name']}**: {e}")

    try:
        for i in range(0, len(queued_files), 4):  # Process in chunks of 4
            group = queued_files[i:i + 4]
            tasks = [
                asyncio.create_task(process_file_with_delay(index, file_item))
                for index, file_item in enumerate(group)
            ]
            # Wait for the current group of tasks to complete
            await asyncio.gather(*tasks)
    except Exception as e:
        await message.reply_text(f"> **An unexpected error occurred:** {e}")
    else:
        await message.reply_text(
            f"<b>All queued files have been processed. ✅</b>\n\n"
            f"<b>✅ Successfully Renamed:</b> {success_count}\n"
            f"<b>❌ Failed:</b> {failure_count}\n\n"
            "<b>🍀 Developer</b> <a href=https://t.me/Snowball_official>ѕησωвαℓℓ ❄️</a>",
            disable_web_page_preview=True,
        )
    finally:
        # Clear the queue and remove the user from the active users list
        del temp.AUTO_RENAME_QUEUE[userId]
        temp.USERS_IN_QUEUE.remove(userId)
