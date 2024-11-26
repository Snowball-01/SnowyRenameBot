import random
from helper.ffmpeg import fix_thumb, take_screen_shot
from pyrogram import Client, filters
from pyrogram.enums import MessageMediaType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from helper.utils import progress_for_pyrogram, convert, humanbytes
from helper.database import db
from PIL import Image
import asyncio
import os
import time
from helper.utils import add_prefix_suffix, user_client, start_clone_bot
from config import Config



# Define the main message handler for private messages with replies
@Client.on_message(filters.private & filters.reply)
async def refunc(client, message):
    reply_message = message.reply_to_message
    if isinstance(reply_message.reply_markup, ForceReply):
        new_name = message.text
        await message.delete()
        msg = await client.get_messages(message.chat.id, reply_message.id)
        file = msg.reply_to_message
        media = getattr(file, file.media.value)
        if not "." in new_name:
            if "." in media.file_name:
                extn = media.file_name.rsplit('.', 1)[-1]
            else:
                extn = "mkv"
            new_name = new_name + "." + extn
        await reply_message.delete()

        # Use a list to store the inline keyboard buttons
        button = [
            [InlineKeyboardButton(
                "📁 ᴅᴏᴄᴜᴍᴇɴᴛ", callback_data="upload_document")]
        ]
        if file.media in [MessageMediaType.VIDEO, MessageMediaType.DOCUMENT]:
            button.append([InlineKeyboardButton(
                "🎥 ᴠɪᴅᴇᴏ", callback_data="upload_video")])
        elif file.media == MessageMediaType.AUDIO:
            button.append([InlineKeyboardButton(
                "🎵 ᴀᴜᴅɪᴏ", callback_data="upload_audio")])

        # Use a single call to reply with both text and inline keyboard
        await message.reply(
            text=f"**sᴇʟᴇᴄᴛ ᴛʜᴇ ᴏᴜᴛᴘᴜᴛ ғɪʟᴇ ᴛʏᴘᴇ**\n**• ғɪʟᴇ ɴᴀᴍᴇ :-**  `{new_name}`",
            reply_to_message_id=file.id,
            reply_markup=InlineKeyboardMarkup(button)
        )

# Define the callback for the 'upload' buttons


@Client.on_callback_query(filters.regex("upload"))
async def doc(bot, update):
    # Creating Directory for Metadata
    os.makedirs(f"metadata/{update.from_user.id}", exist_ok=True)

    # Extracting necessary information
    prefix = await db.get_prefix(update.message.chat.id)
    suffix = await db.get_suffix(update.message.chat.id)
    new_name = update.message.text
    new_filename_ = new_name.split(":-")[1]

    try:
        # adding prefix and suffix
        new_filename = add_prefix_suffix(new_filename_, prefix, suffix)

    except Exception as e:
        return await update.message.edit(f"⚠️ Something went wrong can't able to set Prefix or Suffix ☹️ \n\n❄️ Contact My Creator -> @Snowball_Official\nError: {e}")

    file_path = f"downloads/{update.from_user.id}/{new_filename.strip()}"
    file = update.message.reply_to_message

    ms = await update.message.edit("⚠️ ** ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ... **\n** ᴛʀʏɪɴɢ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ... **")
    try:
        path = await bot.download_media(message=file, file_name=file_path, progress=progress_for_pyrogram, progress_args=("❄️ ** ᴅᴏᴡɴʟᴏᴀᴅ sᴛᴀʀᴛᴇᴅ... **", ms, time.time()))
    except Exception as e:
        return await ms.edit(e)

    _bool_metadata = await db.get_metadata(update.message.chat.id)

    if (_bool_metadata):
        metadata_path = f"metadata/{update.from_user.id}/{new_filename.strip()}"
        metadata = await db.get_metadata_code(update.from_user.id)
        if metadata:
            await ms.edit("ɪ ғᴏᴜɴᴅ ʏᴏᴜʀ ᴍᴇᴛᴀᴅᴀᴛᴀ ᴄᴏᴅᴇ\n\n__** ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ... **__\n** ᴀᴅᴅɪɴɢ ᴍᴇᴛᴀᴅᴛᴀ ᴛᴏ ᴛʜᴇ ғɪʟᴇ... **")
            cmd = f"""ffmpeg -i "{path}" {metadata} "{metadata_path}" """

            process = await asyncio.create_subprocess_shell(
                cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()
            er = stderr.decode().strip()
            
            try:
                if er:
                    await ms.edit(f"Error occurred:\n\n{er}\n\n**Error**")
                    os.remove(path)
                    os.remove(metadata_path)
                    return
            except:
                pass

        await ms.edit("**ᴍᴇᴛᴀᴅᴀᴛᴀ ᴀᴅᴅᴇᴅ ᴛᴏ ᴛʜᴇ ғɪʟᴇ ✅**\n\n⚠️ __** ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ... **__\n\n** ᴛʀʏɪɴɢ ᴛᴏ ᴜᴘʟᴏᴀᴅ.... **")
    else:
        await ms.edit("⚠️ __** ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ... **__\n\n** ᴛʀʏɪɴɢ ᴛᴏ ᴜᴘʟᴏᴀᴅ.... **")

    duration = 0
    try:
        parser = createParser(file_path)
        metadata = extractMetadata(parser)
        if metadata.has("duration"):
            duration = metadata.get('duration').seconds
        parser.close()

    except:
        pass
    ph_path = None
    media = getattr(file, file.media.value)
    c_caption = await db.get_caption(update.message.chat.id)
    c_thumb = await db.get_thumbnail(update.message.chat.id)

    if c_caption:
        try:
            caption = c_caption.format(filename=new_filename, filesize=humanbytes(
                media.file_size), duration=convert(duration))
        except Exception as e:
            return await ms.edit(text=f"Yᴏᴜʀ Cᴀᴩᴛɪᴏɴ Eʀʀᴏʀ Exᴄᴇᴩᴛ Kᴇyᴡᴏʀᴅ Aʀɢᴜᴍᴇɴᴛ ●> ({e})")
    else:
        caption = f"**{new_filename}**"

    if (media.thumbs or c_thumb):
        if c_thumb:
            ph_path = await bot.download_media(c_thumb)
            width, height, ph_path = await fix_thumb(ph_path)
        else:
            try:
                ph_path_ = await take_screen_shot(file_path, os.path.dirname(os.path.abspath(file_path)), random.randint(0, duration - 1))
                width, height, ph_path = await fix_thumb(ph_path_)
            except Exception as e:
                ph_path = None
                print(e)

    type = update.data.split("_")[1]
    user_bot = await db.get_user_bot(Config.ADMIN[0])

    if media.file_size > 2000 * 1024 * 1024:
        try:
            if user_bot:
                app = await start_clone_bot(user_client(user_bot['session']))
            else:
                if file_path:
                    os.remove(file_path)
                if ph_path:
                    os.remove(ph_path)
                if metadata_path:
                    os.remove(metadata_path)
                if path:
                    os.remove(path)
                return await update.message.reply_text("**⚠️ sᴏʀʀʏ ᴅᴇᴀʀ ᴛʜɪs ʙᴏᴛ ᴅᴏᴇsɴ'ᴛ sᴜᴘᴘᴏʀᴛ ғɪʟᴇs ʙɪɢɢᴇʀ ᴛʜᴀɴ 2ɢʙ **")

            if type == "document":

                filw = await app.send_document(
                    Config.LOG_CHANNEL,
                    document=metadata_path if _bool_metadata else file_path,
                    thumb=ph_path,
                    caption=caption,
                    progress=progress_for_pyrogram,
                    progress_args=("🌨️ ** ᴜᴘʟᴏᴀᴅɪɴɢ sᴛᴀʀᴛᴇᴅ.... **", ms, time.time()))

                from_chat = filw.chat.id
                mg_id = filw.id
                time.sleep(2)
                await bot.copy_message(update.from_user.id, from_chat, mg_id)
                await ms.delete()
                await bot.delete_messages(from_chat, mg_id)

            elif type == "video":
                filw = await app.send_video(
                    Config.LOG_CHANNEL,
                    video=metadata_path if _bool_metadata else file_path,
                    caption=caption,
                    thumb=ph_path,
                    width=width,
                    height=height,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=("🌨️ ** ᴜᴘʟᴏᴀᴅɪɴɢ sᴛᴀʀᴛᴇᴅ.... **", ms, time.time()))

                from_chat = filw.chat.id
                mg_id = filw.id
                time.sleep(2)
                await bot.copy_message(update.from_user.id, from_chat, mg_id)
                await ms.delete()
                await bot.delete_messages(from_chat, mg_id)
            elif type == "audio":
                filw = await app.send_audio(
                    Config.LOG_CHANNEL,
                    audio=metadata_path if _bool_metadata else file_path,
                    caption=caption,
                    thumb=ph_path,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=("🌨️ ** ᴜᴘʟᴏᴀᴅɪɴɢ sᴛᴀʀᴛᴇᴅ.... **", ms, time.time()))

                from_chat = filw.chat.id
                mg_id = filw.id
                time.sleep(2)
                await bot.copy_message(update.from_user.id, from_chat, mg_id)
                await ms.delete()
                await bot.delete_messages(from_chat, mg_id)

            if user_bot:
                await app.stop()
            
        except Exception as e:
            os.remove(file_path)
            if ph_path:
                os.remove(ph_path)
            if metadata_path:
                os.remove(metadata_path)
            if path:
                os.remove(path)
            return await ms.edit(f" Eʀʀᴏʀ {e}")

    else:

        try:
            if type == "document":
                await bot.send_document(
                    update.message.chat.id,
                    document=metadata_path if _bool_metadata else file_path,
                    thumb=ph_path,
                    caption=caption,
                    progress=progress_for_pyrogram,
                    progress_args=("🌨️ ** ᴜᴘʟᴏᴀᴅɪɴɢ sᴛᴀʀᴛᴇᴅ.... **", ms, time.time()))
            elif type == "video":
                await bot.send_video(
                    update.message.chat.id,
                    video=metadata_path if _bool_metadata else file_path,
                    caption=caption,
                    thumb=ph_path,
                    width=width,
                    height=height,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=("🌨️ ** ᴜᴘʟᴏᴀᴅɪɴɢ sᴛᴀʀᴛᴇᴅ.... **", ms, time.time()))
            elif type == "audio":
                await bot.send_audio(
                    update.message.chat.id,
                    audio=metadata_path if _bool_metadata else file_path,
                    caption=caption,
                    thumb=ph_path,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=("🌨️ ** ᴜᴘʟᴏᴀᴅɪɴɢ sᴛᴀʀᴛᴇᴅ.... **", ms, time.time()))
        except Exception as e: 
            os.remove(file_path)
            if ph_path:
                os.remove(ph_path)
            if metadata_path:
                os.remove(metadata_path)
            if path:
                os.remove(path)
            return await ms.edit(f" Eʀʀᴏʀ {e}")

    await ms.delete()

    if ph_path:
        os.remove(ph_path)
    if file_path:
        os.remove(file_path)
    if metadata_path:
        os.remove(metadata_path)