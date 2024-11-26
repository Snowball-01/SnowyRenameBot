import asyncio
import random
import sys
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import (
    InputMediaDocument,
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from PIL import Image
from datetime import datetime
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from helper.ffmpeg import fix_thumb, take_screen_shot
from helper.utils import (
    progress_for_pyrogram,
    humanbytes,
    convert,
    start_clone_bot,
    user_client,
)
from helper.database import db
from config import Config
import os
import time
import re

renaming_operations = {}

# Pattern 1: S01E02 or S01EP02
pattern1 = re.compile(r"S(\d+)(?:E|EP)(\d+)")
# Pattern 2: S01 E02 or S01 EP02 or S01 - E01 or S01 - EP02
pattern2 = re.compile(r"S(\d+)\s*(?:E|EP|-\s*EP)(\d+)")
# Pattern 3: Episode Number After "E" or "EP"
pattern3 = re.compile(r"(?:[([<{]?\s*(?:E|EP)\s*(\d+)\s*[)\]>}]?)")
# Pattern 3_2: episode number after - [hyphen]
pattern3_2 = re.compile(r"(?:\s*-\s*(\d+)\s*)")
# Pattern 4: S2 09 ex.
pattern4 = re.compile(r"S(\d+)[^\d]*(\d+)", re.IGNORECASE)
# Pattern X: Standalone Episode Number
patternX = re.compile(r"(\d+)")
# QUALITY PATTERNS
# Pattern 5: 3-4 digits before 'p' as quality
pattern5 = re.compile(r"\b(?:.*?(\d{3,4}[^\dp]*p).*?|.*?(\d{3,4}p))\b", re.IGNORECASE)
# Pattern 6: Find 4k in brackets or parentheses
pattern6 = re.compile(r"[([<{]?\s*4k\s*[)\]>}]?", re.IGNORECASE)
# Pattern 7: Find 2k in brackets or parentheses
pattern7 = re.compile(r"[([<{]?\s*2k\s*[)\]>}]?", re.IGNORECASE)
# Pattern 8: Find HdRip without spaces
pattern8 = re.compile(r"[([<{]?\s*HdRip\s*[)\]>}]?|\bHdRip\b", re.IGNORECASE)
# Pattern 9: Find 4kX264 in brackets or parentheses
pattern9 = re.compile(r"[([<{]?\s*4kX264\s*[)\]>}]?", re.IGNORECASE)
# Pattern 10: Find 4kx265 in brackets or parentheses
pattern10 = re.compile(r"[([<{]?\s*4kx265\s*[)\]>}]?", re.IGNORECASE)


def extract_quality(filename):
    # Try Quality Patterns
    match5 = re.search(pattern5, filename)
    if match5:
        print("Matched Pattern 5")
        quality5 = match5.group(1) or match5.group(
            2
        )  # Extracted quality from both patterns
        print(f"Quality: {quality5}")
        return quality5

    match6 = re.search(pattern6, filename)
    if match6:
        print("Matched Pattern 6")
        quality6 = "4k"
        print(f"Quality: {quality6}")
        return quality6

    match7 = re.search(pattern7, filename)
    if match7:
        print("Matched Pattern 7")
        quality7 = "2k"
        print(f"Quality: {quality7}")
        return quality7

    match8 = re.search(pattern8, filename)
    if match8:
        print("Matched Pattern 8")
        quality8 = "HdRip"
        print(f"Quality: {quality8}")
        return quality8

    match9 = re.search(pattern9, filename)
    if match9:
        print("Matched Pattern 9")
        quality9 = "4kX264"
        print(f"Quality: {quality9}")
        return quality9

    match10 = re.search(pattern10, filename)
    if match10:
        print("Matched Pattern 10")
        quality10 = "4kx265"
        print(f"Quality: {quality10}")
        return quality10

    # Return "Unknown" if no pattern matches
    unknown_quality = "Unknown"
    print(f"Quality: {unknown_quality}")
    return unknown_quality


def extract_episode_number(filename):
    # Try Pattern 1
    match = re.search(pattern1, filename)
    if match:
        print("Matched Pattern 1")
        return match.group(2)  # Extracted episode number

    # Try Pattern 2
    match = re.search(pattern2, filename)
    if match:
        print("Matched Pattern 2")
        return match.group(2)  # Extracted episode number

    # Try Pattern 3
    match = re.search(pattern3, filename)
    if match:
        print("Matched Pattern 3")
        return match.group(1)  # Extracted episode number

    # Try Pattern 3_2
    match = re.search(pattern3_2, filename)
    if match:
        print("Matched Pattern 3_2")
        return match.group(1)  # Extracted episode number

    # Try Pattern 4
    match = re.search(pattern4, filename)
    if match:
        print("Matched Pattern 4")
        return match.group(2)  # Extracted episode number

    # Try Pattern X
    match = re.search(patternX, filename)
    if match:
        print("Matched Pattern X")
        return match.group(1)  # Extracted episode number

    # Return None if no pattern matches
    return None


# Check if autorename is enabled
async def is_autorename(_, client, message):
    autorename = await db.get_autorename(message.from_user.id)

    if autorename:
        return True

    return False


# Example Usage:
filename = "Naruto Shippuden S01 - EP07 - 1080p [Dual Audio] @Madflix_Bots.mkv"
episode_number = extract_episode_number(filename)
print(f"Extracted Episode Number: {episode_number}")


# Inside the handler for file uploads
@Client.on_message(
    filters.private
    & (filters.document | filters.video | filters.audio)
    & filters.create(is_autorename)
)
async def auto_rename_files(client, message):

    user_id = message.from_user.id
    target_channel = None
    rename_template = await db.get_rename_templates(user_id)
    media_preference = await db.get_media_preference(user_id)

    user_status = await db.get_user_status(user_id)

    if (
        user_status["plan"] == "free"
        and user_id not in Config.ADMIN
        and Config.PREMIUM
    ):
        return await message.reply_text(
            "**⚠️ ᴋɪɴᴅʟʏ ᴜᴘɢʀᴀᴅᴇ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ ᴛᴏ ᴀᴜᴛᴏ ʀᴇᴀɴᴍᴇ**\n\nᴛᴏ ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴘʟᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ /my_plan",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("ᴜᴘɢʀᴀᴅᴇ ᴘʟᴀɴ", callback_data="upgrade")]]
            ),
        )

    if not rename_template:
        return await message.reply_text(
            "Please Set An Auto Rename Format First Using /autorename"
        )

    # Extract information from the incoming file name
    if message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name
        media_type = (
            media_preference or "document"
        )  # Use preferred media type or default to document
    elif message.video:
        file_id = message.video.file_id
        file_name = f"{message.video.file_name}.mp4"
        media_type = (
            media_preference or "video"
        )  # Use preferred media type or default to video
    elif message.audio:
        file_id = message.audio.file_id
        file_name = f"{message.audio.file_name}.mp3"
        media_type = (
            media_preference or "audio"
        )  # Use preferred media type or default to audio
    else:
        return await message.reply_text("Unsupported File Type")

    print(f"Original File Name: {file_name}")

    if rename_template:

        trigger = [keys.lower() for keys in rename_template.keys()]
        trigger_word = [word for word in trigger if word in file_name.lower()][0]

        if not trigger_word:
            trigger_word = None

        print("Trigger Word: ", trigger_word)

        format_template = next(
            (
                rename_template[key]
                for key in rename_template
                if key.lower() == trigger_word
            ),
            None,
        )
        target_channel = format_template[1]
        format_template = format_template[0]
        print("Format Template: ", format_template)
        print("Channel : ", target_channel)

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
        file = message

        download_msg = await message.reply_text(
            text="⚠️ __** ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ... **__\n** ᴛʀʏɪɴɢ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ... **",
            reply_to_message_id=message.id,
        )
        try:
            path = await client.download_media(
                message=file,
                file_name=file_path,
                progress=progress_for_pyrogram,
                progress_args=("Download Started....", download_msg, time.time()),
            )
        except Exception as e:
            # Mark the file as ignored
            del renaming_operations[file_id]
            return await download_msg.edit(e)

        bool_metadata = await db.get_metadata(message.from_user.id)

        if bool_metadata:
            metadata_path = f"metadata/{message.from_user.id}/{new_file_name}"
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

        type = media_type  # Use 'media_type' variable instead
        user_bot = await db.get_user_bot(Config.ADMIN[0])

        if media.file_size > 2000 * 1024 * 1024:
            try:

                if user_bot:
                    app = await start_clone_bot(user_client(user_bot["session"]))
                else:
                    if file_path:
                        os.remove(file_path)
                    if ph_path:
                        os.remove(ph_path)
                    if metadata_path:
                        os.remove(metadata_path)
                    if path:
                        os.remove(path)
                    return await message.reply_text(
                        "**⚠️ sᴏʀʀʏ ᴅᴇᴀʀ ᴛʜɪs ʙᴏᴛ ᴅᴏᴇsɴ'ᴛ sᴜᴘᴘᴏʀᴛ ғɪʟᴇs ʙɪɢɢᴇʀ ᴛʜᴀɴ 2ɢʙ **"
                    )

                if type == "document":
                    for chnlId in target_channel:
                        
                        filw = await app.send_document(
                            Config.LOG_CHANNEL,
                            document=metadata_path if bool_metadata else file_path,
                            thumb=ph_path,
                            caption=caption,
                            progress=progress_for_pyrogram,
                            progress_args=(
                                "⚠️ __**Please wait...**__\n\n🌨️ **Uᴩʟᴏᴅ Sᴛᴀʀᴛᴇᴅ....**",
                                upload_msg,
                                time.time(),
                            ),
                        )

                        from_chat = filw.chat.id
                        mg_id = filw.id
                        time.sleep(2)
                        await client.copy_message(
                            int(chnlId) if chnlId else message.chat.id, from_chat, mg_id
                        )
                        await upload_msg.delete()
                        await client.delete_messages(from_chat, mg_id)

                elif type == "video":
                    for chnlId in target_channel:
                        filw = await app.send_video(
                            Config.LOG_CHANNEL,
                            video=metadata_path if bool_metadata else file_path,
                            caption=caption,
                            thumb=ph_path,
                            width=width,
                            height=height,
                            duration=duration,
                            progress=progress_for_pyrogram,
                            progress_args=(
                                "⚠️ __**Please wait...**__\n\n🌨️ **Uᴩʟᴏᴅ Sᴛᴀʀᴛᴇᴅ....**",
                                upload_msg,
                                time.time(),
                            ),
                        )

                        from_chat = filw.chat.id
                        mg_id = filw.id
                        time.sleep(2)
                        await client.copy_message(
                            int(chnlId) if chnlId else message.chat.id, from_chat, mg_id
                        )
                        await upload_msg.delete()
                        await client.delete_messages(from_chat, mg_id)
                elif type == "audio":
                    for chnlId in target_channel:
                        filw = await app.send_audio(
                            Config.LOG_CHANNEL,
                            audio=metadata_path if bool_metadata else file_path,
                            caption=caption,
                            thumb=ph_path,
                            duration=duration,
                            progress=progress_for_pyrogram,
                            progress_args=(
                                "⚠️ __**Please wait...**__\n\n🌨️ **Uᴩʟᴏᴅ Sᴛᴀʀᴛᴇᴅ....**",
                                upload_msg,
                                time.time(),
                            ),
                        )

                        from_chat = filw.chat.id
                        mg_id = filw.id
                        time.sleep(2)
                        await client.copy_message(
                            int(chnlId) if chnlId else message.chat.id, from_chat, mg_id
                        )
                        await upload_msg.delete()
                        await client.delete_messages(from_chat, mg_id)

            except Exception as e:
                os.remove(file_path)
                if ph_path:
                    os.remove(ph_path)
                if metadata_path:
                    os.remove(metadata_path)
                if path:
                    os.remove(path)
                return await upload_msg.edit(f" Eʀʀᴏʀ {e}")

        else:

            try:
                if type == "document":
                    for chnlId in target_channel:
                        await client.send_document(
                            int(chnlId) if chnlId else message.chat.id,
                            document=file_path,
                            thumb=ph_path,
                            caption=caption,
                            progress=progress_for_pyrogram,
                            progress_args=(
                                "⚠️ __** ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ... **__\n\n🌨️ ** ᴜᴘʟᴏᴀᴅɪɴɢ sᴛᴀʀᴛᴇᴅ.... **",
                                upload_msg,
                                time.time(),
                            ),
                        )
                elif type == "video":
                    for chnlId in target_channel:
                        await client.send_video(
                            int(chnlId) if chnlId else message.chat.id,
                            video=file_path,
                            caption=caption,
                            thumb=ph_path,
                            duration=duration,
                            progress=progress_for_pyrogram,
                            progress_args=(
                                "⚠️ __** ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ... **__\n\n🌨️ ** ᴜᴘʟᴏᴀᴅɪɴɢ sᴛᴀʀᴛᴇᴅ.... **",
                                upload_msg,
                                time.time(),
                            ),
                        )
                elif type == "audio":
                    for chnlId in target_channel:
                        await client.send_audio(
                            int(chnlId) if chnlId else message.chat.id,
                            audio=file_path,
                            caption=caption,
                            thumb=ph_path,
                            duration=duration,
                            progress=progress_for_pyrogram,
                            progress_args=(
                                "⚠️ __** ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ... **__\n\n🌨️ ** ᴜᴘʟᴏᴀᴅɪɴɢ sᴛᴀʀᴛᴇᴅ.... **",
                                upload_msg,
                                time.time(),
                            ),
                        )
            except Exception as e:
                os.remove(file_path)
                if ph_path:
                    os.remove(ph_path)
                if metadata_path:
                    os.remove(metadata_path)
                # Mark the file as ignored
                return await upload_msg.edit(f"Error: {e}")

        await download_msg.delete()

        os.remove(file_path)
        if ph_path:
            os.remove(ph_path)
        if metadata_path:
            os.remove(metadata_path)

        # Remove the entry from renaming_operations after successful renaming
        del renaming_operations[file_id]
