import os
import random
import shutil
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, CallbackQuery, Message, InputMediaPhoto
from pyrogram.errors import FloodWait
from asyncio import sleep
import humanize
from utility.database import db
from config import Config, Txt, temp


async def manulaRenameFunc(client, message):
    file = getattr(message, message.media.value)
    filename = file.file_name
    filesize = humanize.naturalsize(file.file_size)
    user_id = message.from_user.id
    user_status = await db.get_user_status(user_id)

    if user_status["plan"] == "free" and user_id not in Config.ADMIN and Config.PREMIUM and int(file.file_size) > 2000 * 1024 * 1024:
        return await message.reply_text(
            "**⚠️ ᴋɪɴᴅʟʏ ᴜᴘɢʀᴀᴅᴇ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ ᴛᴏ ʀᴇɴᴀᴍᴇ ғɪʟᴇs ᴀʙᴏᴠᴇ 2ɢʙ**\n\nᴛᴏ ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴘʟᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ /my_plan",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴜᴘɢʀᴀᴅᴇ ᴘʟᴀɴ", callback_data="upgrade")]]),
        )

    if file.file_size > 2000 * 1024 * 1024:
        if not await db.is_user_bot_exist(Config.ADMIN[0]):
            return await message.reply_text("**⚠️ sᴏʀʀʏ ᴅᴇᴀʀ ᴛʜɪs ʙᴏᴛ ᴅᴏᴇsɴ'ᴛ sᴜᴘᴘᴏʀᴛ ғɪʟᴇs ʙɪɢɢᴇʀ ᴛʜᴀɴ 2ɢʙ **")
    
    try:
        text = f"""**__What do you want me to do with this file.?__**\n\n**File Name** :- `{filename}`\n\n**File Size** :- `{filesize}`"""
        buttons = [[InlineKeyboardButton("✎ ʀᴇɴᴀᴍᴇ ✎", callback_data="manual_rename")],
                   [InlineKeyboardButton("✘ ᴄᴀɴᴄᴇʟ ✘", callback_data="close")]]
        await message.reply_text(text=text, reply_to_message_id=message.id, reply_markup=InlineKeyboardMarkup(buttons))
    except FloodWait as e:
        await sleep(e.value)
        text = f"""**__What do you want me to do with this file.?__**\n\n**File Name** :- `{filename}`\n\n**File Size** :- `{filesize}`"""
        buttons = [[InlineKeyboardButton("✎ ʀᴇɴᴀᴍᴇ ✎", callback_data="manual_rename")],
                   [InlineKeyboardButton("✘ ᴄᴀɴᴄᴇʟ ✘", callback_data="close")]]
        await message.reply_text(text=text, reply_to_message_id=message.id, reply_markup=InlineKeyboardMarkup(buttons))
    except:
        pass

@Client.on_message(filters.private & filters.command("start"))
async def start(client, message):
    
    user = message.from_user
    await db.add_user(client, message)
    button = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            'ᴜᴘᴅᴀᴛᴇ', url='https://t.me/Kdramaland'),
        InlineKeyboardButton(
            'sᴜᴘᴘᴏʀᴛ', url='https://t.me/SnowDevs')
    ], [
        InlineKeyboardButton('ʜᴇʟᴘ', callback_data='help'),
        InlineKeyboardButton('ᴀʙᴏᴜᴛ', callback_data='about')
    ], [InlineKeyboardButton('sᴇʀᴠᴇʀ sᴛᴀᴛs', callback_data='stats')]])
    if Config.PICS:
        await message.reply_photo(random.choice(Config.PICS), caption=Txt.START_TXT.format(user.mention), reply_markup=button)
    else:
        await message.reply_text(text=Txt.START_TXT.format(user.mention), reply_markup=button, disable_web_page_preview=True)


@Client.on_message(filters.private & (filters.document | filters.audio | filters.video))
async def handle_manual_rename(client, message):
    await manulaRenameFunc(client, message)

@Client.on_message(filters.private & filters.command("cc"))
async def handle_cc(client, message):
    user_id = message.from_user.id
    try:
        if os.path.exists(f"downloads/{user_id}"):
            shutil.rmtree(f"downloads/{user_id}")

        if os.path.exists(f"metadata/{user_id}"):
            shutil.rmtree(f"metadata/{user_id}")

        if user_id in temp.AUTO_RENAME_QUEUE:
            temp.AUTO_RENAME_QUEUE.pop(user_id)
            
        if user_id in temp.USERS_IN_QUEUE:
            temp.USERS_IN_QUEUE.remove(user_id)
    except:
        return await  message.reply_text("**sᴏᴍᴇ ᴘʀᴏᴄᴇss ɪs ᴏɴɢᴏɪɴɢ ᴡɪᴛʜ ʏᴏᴜʀ ᴅᴀᴛᴀ ᴀɴᴅ ᴄᴀɴɴᴏᴛ ʙᴇ ᴄʟᴇᴀʀᴇᴅ. ❌**", reply_to_message_id=message.id)
        pass
    
    return await  message.reply_text("**ᴜsᴇʀ ᴄᴀᴄʜᴇ ᴄʟᴇᴀʀᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ ✅**", reply_to_message_id=message.id)
