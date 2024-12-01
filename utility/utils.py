import os
import re
import math, time
from datetime import datetime
import humanize
from pytz import timezone
from config import Config, Txt
from pyrogram import Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def start_clone_bot(Renameclient):
    await Renameclient.start()
    return Renameclient


def user_client(session):
    return Client("USERclient", Config.API_ID, Config.API_HASH, session_string=session)


async def progress_for_pyrogram(current, total, ud_type, message, start):
    now = time.time()
    diff = now - start
    if round(diff % 5.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)

        progress = "{0}{1}".format(
            "".join(["█" for i in range(math.floor(percentage / 5))]),
            "".join(["▒" for i in range(20 - math.floor(percentage / 5))]),
        )
        tmp = progress + Txt.PROGRESS_BAR.format(
            round(percentage, 2),
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            estimated_total_time if estimated_total_time != "" else "0 s",
        )
        try:
            await message.edit(
                text=f"{ud_type}\n\n{tmp}",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("✘ ᴄᴀɴᴄᴇʟ ✘", callback_data="close")]]
                ),
            )
        except:
            pass


def humanbytes(size):
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: " ", 1: "K", 2: "M", 3: "G", 4: "T"}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + "b"


def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (
        ((str(days) + "d, ") if days else "")
        + ((str(hours) + "h, ") if hours else "")
        + ((str(minutes) + "m, ") if minutes else "")
        + ((str(seconds) + "s, ") if seconds else "")
        + ((str(milliseconds) + "upload_message, ") if milliseconds else "")
    )
    return tmp[:-2]


def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%d:%02d:%02d" % (hour, minutes, seconds)


async def send_log(b, u):
    if Config.LOG_CHANNEL is not None:
        curr = datetime.now(timezone("Asia/Kolkata"))
        date = curr.strftime("%d %B, %Y")
        time = curr.strftime("%I:%M:%S %p")
        await b.send_message(
            Config.LOG_CHANNEL,
            f"<b><u>New User Started The client</u></b> \n\n<b>User ID</b> : `{u.id}` \n<b>First Name</b> : {u.first_name} \n<b>Last Name</b> : {u.last_name} \n<b>User Name</b> : @{u.username} \n<b>User Mention</b> : {u.mention} \n<b>User Link</b> : <a href='tg://openmessage?user_id={u.id}'>Click Here</a>\n\nDate: {date}\nTime: {time}\n\nBy: {b.mention}",
        )

def add_prefix_suffix(input_string, prefix='', suffix=''):
    pattern = r'(?P<filename>.*?)(\.\w+)?$'
    match = re.search(pattern, input_string)
    if match:
        filename = match.group('filename')
        extension = match.group(2) or ''
        if prefix == None:
            if suffix == None:
                return f"{filename}{extension}"
            return f"{filename} {suffix}{extension}"
        elif suffix == None:
            if prefix == None:
                return f"{filename}{extension}"
            return f"{prefix}{filename}{extension}"
        else:
            return f"{prefix}{filename} {suffix}{extension}"

    else:
        return input_string
    
async def uploadFiles(
    bot, message, media, metadata_path, target_channel=None, bool_metadata=None, 
    file_path=None, ms=None, ph_path=None, caption="", width=0, height=0, 
    path=None, duration=0, user_bot=None, type=None
):
    """
    Upload files to a channel or chat. Supports documents, videos, and audio files.

    Parameters:
    - bot: Main bot instance.
    - message: Pyrogram message object.
    - media: Media object containing file details.
    - metadata_path, file_path, ph_path: Paths for files and thumbnails.
    - target_channel: Optional channel for uploads (default is Config.LOG_CHANNEL).
    - bool_metadata: Whether metadata is applied.
    - ms: Status message object for progress updates.
    - caption: Caption for the uploaded media.
    - width, height: Video dimensions (optional).
    - duration: Media duration in seconds.
    - user_bot: User bot session for large file uploads.
    - type: Media type (document, video, or audio).
    - file_id: Optional unique identifier for the file.
    """
    try:
        # Determine the target channel
        target_channel = target_channel or Config.LOG_CHANNEL

        # Handle files larger than 2GB
        if media.file_size < 2000 * 1024 * 1024:
            if user_bot:
                app = await start_clone_bot(user_client(user_bot['session']))
            else:
                raise ValueError("File size exceeds 2GB limit and no user bot is available.")
            
            # Upload with user bot
            if type == "document":
                filw = await app.send_document(
                    target_channel,
                    document=metadata_path if bool_metadata else file_path,
                    thumb=ph_path,
                    caption=caption,
                    progress=progress_for_pyrogram,
                    progress_args=("🌨️ ** ᴜᴘʟᴏᴀᴅɪɴɢ sᴛᴀʀᴛᴇᴅ.... **", ms, time.time())
                )
            elif type == "video":
                filw = await app.send_video(
                    target_channel,
                    video=metadata_path if bool_metadata else file_path,
                    caption=caption,
                    thumb=ph_path,
                    width=width,
                    height=height,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=("🌨️ ** ᴜᴘʟᴏᴀᴅɪɴɢ sᴛᴀʀᴛᴇᴅ.... **", ms, time.time())
                )
            elif type == "audio":
                filw = await app.send_audio(
                    target_channel,
                    audio=metadata_path if bool_metadata else file_path,
                    caption=caption,
                    thumb=ph_path,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=("🌨️ ** ᴜᴘʟᴏᴀᴅɪɴɢ sᴛᴀʀᴛᴇᴅ.... **", ms, time.time())
                )

            # Copy message and clean up
            from_chat, mg_id = filw.chat.id, filw.id
            await bot.copy_message(message.chat.id, from_chat, mg_id)
            await ms.delete()
            await bot.delete_messages(from_chat, mg_id)
            if user_bot:
                await app.stop()

        # Upload directly for files <= 2GB
        else:
            if type == "document":
                await bot.send_document(
                    message.chat.id,
                    document=metadata_path if bool_metadata else file_path,
                    thumb=ph_path,
                    caption=caption,
                    progress=progress_for_pyrogram,
                    progress_args=("🌨️ ** ᴜᴘʟᴏᴀᴅɪɴɢ sᴛᴀʀᴛᴇᴅ.... **", ms, time.time())
                )
            elif type == "video":
                await bot.send_video(
                    message.chat.id,
                    video=metadata_path if bool_metadata else file_path,
                    caption=caption,
                    thumb=ph_path,
                    width=width,
                    height=height,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=("🌨️ ** ᴜᴘʟᴏᴀᴅɪɴɢ sᴛᴀʀᴛᴇᴅ.... **", ms, time.time())
                )
            elif type == "audio":
                await bot.send_audio(
                    message.chat.id,
                    audio=metadata_path if bool_metadata else file_path,
                    caption=caption,
                    thumb=ph_path,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=("🌨️ ** ᴜᴘʟᴏᴀᴅɪɴɢ sᴛᴀʀᴛᴇᴅ.... **", ms, time.time())
                )

    except Exception as e:
        await ms.edit(f"Error: {e}")
        
        # Clean up files
        for f in [file_path, ph_path, metadata_path, path]:
            if f and os.path.exists(f):
                os.remove(f)
        return

    # Clean up files after successful upload
    for f in [file_path, ph_path, metadata_path]:
        if f and os.path.exists(f):
            os.remove(f)
    await ms.delete()



