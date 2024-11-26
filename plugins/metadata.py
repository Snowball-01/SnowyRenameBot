from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from helper.database import db
from config import Txt
from pyromod.exceptions.listener_timeout import ListenerTimeout

@Client.on_message(filters.private & filters.command('metadata'))
async def handle_metadata(bot: Client, message: Message):

    ms = await message.reply_text("**Please Wait...**", reply_to_message_id=message.id)
    user_metadata = await db.get_metadata_code(message.from_user.id)
    await ms.delete()
    try:
        await message.reply_text(f"** Your Current Metadata **\n\n➠ `{user_metadata}` ", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('sᴇᴛ ᴄᴜsᴛᴏᴍ ᴍᴇᴛᴀᴅᴀᴛᴀ', callback_data='cutom_metadata')]]))
    except Exception as e:
        print(e)


@Client.on_callback_query(filters.regex('^cutom_metadata'))
async def query_metadata(bot: Client, query: CallbackQuery):
    await query.message.delete()
    try:
        try:
            metadata = await bot.ask(text=Txt.SEND_METADATA, chat_id=query.from_user.id, filters=filters.text, timeout=30, disable_web_page_preview=True)
        except ListenerTimeout:
            await query.message.reply_text("⚠️ **Error!!**\n\n**Request timed out.**\nRestart by using /metadata", reply_to_message_id=query.message.id)
            return
        ms = await query.message.reply_text("**Please Wait...**", reply_to_message_id=metadata.id)
        await db.set_metadata_code(query.from_user.id, metadata_code=metadata.text)
        await ms.edit("**Your Metadta Code Set Successfully ✅**")
    except Exception as e:
        print(e)