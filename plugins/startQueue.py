import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from config import temp
from utility.auto_rename_func import autoRenameFunc

MAX_CONCURRENT_TASKS = 4  # Define the maximum number of concurrent renaming tasks

@Client.on_message(filters.private & filters.command('start_queue'))
async def startQueue(client: Client, message: Message):
    userId = message.from_user.id

    if userId not in temp.AUTO_RENAME_QUEUE:
        return await message.reply_text(
            "> ** Your queue is empty. Kindly add files before using this command. **\n\n"
            "☞ __** How to proceed? **__\n\n"
            "> ** Enable the auto-rename feature, upload files in supported formats, and the bot will add them to the processing queue. Use this command after files are queued to process them. **"
        )
    
    if userId in temp.USERS_IN_QUEUE:
        return await message.reply_text("> ** Please wait for the current queue to complete before starting a new one. **")
    
    # Sort the queue by file name
    temp.AUTO_RENAME_QUEUE[userId].sort(key=lambda x: x["file_name"])
    temp.USERS_IN_QUEUE.append(userId)

    queue = temp.AUTO_RENAME_QUEUE[userId]
    try:
        # Process files in batches
        for i in range(0, len(queue), MAX_CONCURRENT_TASKS):
            batch = queue[i:i + MAX_CONCURRENT_TASKS]
            
            # Process each batch sequentially
            tasks = [
                autoRenameFunc(
                    client,
                    message,
                    item["format_template"],
                    item["target_channel"],
                    item["file_id"],
                    item["file_name"],
                    item["media_type"],
                    int(item["message_id"])
                )
                for item in batch
            ]

            # Wait for all tasks in the batch to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Handle exceptions for each task
            for idx, result in enumerate(results):
                if isinstance(result, Exception):
                    failed_item = batch[idx]
                    await message.reply_text(
                        f"> **Error processing file:** {failed_item['file_name']}\n"
                        f"> **Reason:** {result}"
                    )

    except Exception as e:
        await message.reply_text(f"> **Unexpected Error:** {e}")
    finally:
        # Final cleanup
        del temp.AUTO_RENAME_QUEUE[userId]
        temp.USERS_IN_QUEUE.remove(userId)
        await message.reply_text(
            "<b>All queued files have been successfully renamed. ✅</b>\n\n"
            "<b> 🍀 Developer </b> <a href=https://t.me/Snowball_official>ѕησωвαℓℓ ❄️</a>",
            disable_web_page_preview=True,
        )
