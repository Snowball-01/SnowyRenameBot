from pyrogram import Client, filters
from pyrogram.types import *
from helper.database import db


async def feature_keyboard(user_id):
    metadata = await db.get_metadata(int(user_id))
    autorename = await db.get_autorename(int(user_id))
    media_type = await db.get_media_preference(int(user_id))
    
    keyboard = [[InlineKeyboardButton('ᴍᴇᴛᴀᴅᴀᴛᴀ', callback_data='metadata_{}'.format('on' if metadata else 'off')),
                 InlineKeyboardButton('✅' if metadata else '❌', callback_data='metadata_{}'.format('on' if metadata else 'off'))],
                
                [InlineKeyboardButton('ᴀᴜᴛᴏ-ʀᴇɴᴀᴍᴇ', callback_data='autorename_{}'.format('on' if autorename else 'off')),
                 InlineKeyboardButton('✅' if autorename else '❌', callback_data='autorename_{}'.format('on' if autorename else 'off'))]]
    
    
    if media_type == 'video':
        keyboard.append([InlineKeyboardButton('ғɪʟᴇ-ᴛʏᴘᴇ', callback_data='media_video'), InlineKeyboardButton('ᴠɪᴅᴇᴏ 🎥', callback_data='media_video')])
    
    elif media_type == 'document':
        keyboard.append([InlineKeyboardButton('ғɪʟᴇ-ᴛʏᴘᴇ', callback_data='media_document'), InlineKeyboardButton('ᴅᴏᴄᴜᴍᴇɴᴛ 📂', callback_data='media_document')])
    
    elif media_type == 'audio':
        keyboard.append([InlineKeyboardButton('ғɪʟᴇ-ᴛʏᴘᴇ', callback_data='media_audio'), InlineKeyboardButton('ᴀᴜᴅɪᴏ 🎵', callback_data='media_audio')])
        
    
    return InlineKeyboardMarkup(keyboard)

@Client.on_message(filters.private & filters.command("features"))
async def handle_features(client: Client, message: Message):
    user_id = message.from_user.id
    await message.reply_text(
        text="** ʏᴏᴜ ᴄᴀɴ ᴛᴏɢɢʟᴇ ᴛʜᴇ ᴍᴇᴛᴀᴅᴀᴛᴀ & ᴀᴜᴛᴏ-ʀᴇɴᴀᴍᴇ **",
        reply_markup=await feature_keyboard(user_id)
    )
