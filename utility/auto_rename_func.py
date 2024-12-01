import time
from config import Config
from plugins.file_rename import extract_episode_number, extract_quality, renaming_operations, db
import asyncio
import random
from datetime import datetime
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from utility.ffmpeg import fix_thumb, take_screen_shot
from utility.utils import (
    humanbytes,
    convert,
    progress_for_pyrogram,
    uploadFiles,
)
import os


async def autoRenameFunc(client, message, format_template, target_channel, file_id, file_name, media_type, messageId):
    # Check whether the file is already being renamed or has been renamed recently
    if file_id in renaming_operations:
        elapsed_time = (datetime.now() - renaming_operations[file_id]).seconds
        if elapsed_time < 10:
            print(
                "File is being ignored as it is currently being renamed or was renamed recently."
            )
            return  # Exit the handler if the file is being ignored

    # Mark the file as currently being renamed
    renaming_operations[file_id] = datetime.now()

    # Extract episode number and qualities
    episode_number = extract_episode_number(file_name)

    print(f"Extracted Episode Number: {episode_number}")

    if episode_number:
        placeholders = ["episode", "Episode", "EPISODE", "{episode}"]
        for placeholder in placeholders:
            format_template = format_template.replace(
                placeholder, str(episode_number), 1
            )

        # Add extracted qualities to the format template
        quality_placeholders = ["quality", "Quality", "QUALITY", "{quality}"]
        for quality_placeholder in quality_placeholders:
            if quality_placeholder in format_template:
                extracted_qualities = extract_quality(file_name)
                if extracted_qualities == "Unknown":
                    await message.reply_text(
                        "I Was Not Able To Extract The Quality Properly. Renaming As 'Unknown'..."
                    )
                    # Mark the file as ignored
                    del renaming_operations[file_id]
                    return  # Exit the handler if quality extraction fails

                format_template = format_template.replace(
                    quality_placeholder, "".join(extracted_qualities)
                )

        # Creating Directory for Metadata
        os.makedirs(f"metadata/{message.from_user.id}", exist_ok=True)

        _, file_extension = os.path.splitext(file_name)
        new_file_name = f"{format_template}{file_extension}"
        file_path = f"downloads/{message.from_user.id}/{new_file_name}"
        file = await client.get_messages(message.chat.id, messageId)
        download_msg = await message.reply_text(
            text="⚠️ __** ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ... **__\n** ᴛʀʏɪɴɢ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ... **",
            reply_to_message_id=messageId,
        )
        
        try:
            path = await client.download_media(
                message=file,
                file_name=file_path,
                progress=progress_for_pyrogram,
                progress_args=("> ❄️ ** ᴅᴏᴡɴʟᴏᴀᴅ sᴛᴀʀᴛᴇᴅ... **", download_msg, time.time()),
            )
        except Exception as e:
            # Mark the file as ignored
            del renaming_operations[file_id]
            return await download_msg.edit(e)

        _bool_metadata = await db.get_metadata(message.from_user.id)
        metadata_path = f"metadata/{message.from_user.id}/{new_file_name}"

        if _bool_metadata:
            metadata = await db.get_metadata_code(message.from_user.id)
            if metadata:

                await download_msg.edit(
                    "ɪ ғᴏᴜɴᴅ ʏᴏᴜʀ ᴍᴇᴛᴀᴅᴀᴛᴀ ᴄᴏᴅᴇ\n\n__** ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ... **__\n** ᴀᴅᴅɪɴɢ ᴍᴇᴛᴀᴅᴛᴀ ᴛᴏ ᴛʜᴇ ғɪʟᴇ... **"
                )
                cmd = f"""ffmpeg -i "{path}" {metadata} "{metadata_path}" """

                process = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )

                stdout, stderr = await process.communicate()
                er = stderr.decode().strip()

                try:
                    if er:
                        await download_msg.edit(
                            f"Error occurred:\n\n{er}\n\n**Error**"
                        )
                        os.remove(path)
                        os.remove(metadata_path)
                        return
                except:
                    pass

            upload_msg = await download_msg.edit(
                "**ᴍᴇᴛᴀᴅᴀᴛᴀ ᴀᴅᴅᴇᴅ ᴛᴏ ᴛʜᴇ ғɪʟᴇ ✅**\n\n⚠️ __** ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ... **__\n\n** ᴛʀʏɪɴɢ ᴛᴏ ᴜᴘʟᴏᴀᴅ.... **"
            )
        else:
            upload_msg = await download_msg.edit(
                "⚠️ __** ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ... **__\n\n** ᴛʀʏɪɴɢ ᴛᴏ ᴜᴘʟᴏᴀᴅ.... **"
            )

        duration = 0
        try:
            parser = createParser(file_path)
            metadata = extractMetadata(parser)
            if metadata.has("duration"):
                duration = metadata.get("duration").seconds
            parser.close()
        except Exception as e:
            print(f"Error getting duration: {e}")

        ph_path = None
        c_caption = await db.get_caption(message.chat.id)
        c_thumb = await db.get_thumbnail(message.chat.id)
        media = getattr(file, file.media.value)

        caption = (
            c_caption.format(
                filename=new_file_name,
                filesize=humanbytes(message.document.file_size),
                duration=convert(duration),
            )
            if c_caption
            else f"**{new_file_name}**"
        )

        if media.thumbs or c_thumb:
            if c_thumb:
                ph_path = await client.download_media(c_thumb)
                width, height, ph_path = await fix_thumb(ph_path)
            else:
                try:
                    ph_path_ = await take_screen_shot(
                        file_path,
                        os.path.dirname(os.path.abspath(file_path)),
                        random.randint(0, duration - 1),
                    )
                    width, height, ph_path = await fix_thumb(ph_path_)
                except Exception as e:
                    ph_path = None
                    print(e)

        type = media_type if media_type else "document"  # Use 'media_type' variable instead
        user_bot = await db.get_user_bot(Config.ADMIN[0])

        await uploadFiles(client, message, media, metadata_path, target_channel, _bool_metadata, file_path, upload_msg, ph_path, caption, width, height, path, duration, user_bot, type)

        # Remove the entry from renaming_operations after successful renaming
        del renaming_operations[file_id]