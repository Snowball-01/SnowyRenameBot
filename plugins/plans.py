from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from helper.database import db
from config import Txt, Config


@Client.on_message(filters.private & filters.command(['myplan', 'my_plan']))
async def handle_plan(bot: Client, message: Message):

    if not Config.PREMIUM:
        return

    user = message.from_user
    user_status = await db.get_user_status(user.id)
    if user.id in Config.ADMIN:
        return await message.reply_text(Txt.YOU_ARE_ADMIN_TEXT.format(user.mention))

    text = f"**❄️ ʜᴇʟʟᴏ {user_status['plan']} ᴜsᴇʀ ʏᴏᴜ ᴄᴜʀʀᴇɴᴛ ᴘʟᴀɴ ɪs ʙᴇʟᴏᴡ**\n\nʏᴏᴜʀ ɴᴀᴍᴇ : {user.first_name}\nᴄᴜʀʀᴇɴᴛ ᴘʟᴀɴ : {user_status['plan']}\nᴘʟᴀɴ ᴇxᴘɪʀᴇ ᴏɴ : {user_status['plan_expire_on']}"

    btn = []

    if user_status['plan'] == 'free':
        btn.append([InlineKeyboardButton('ᴜᴘɢʀᴀᴅᴇ', callback_data='upgrade')])

    btn.append([InlineKeyboardButton('ᴄʟᴏsᴇ ✘', callback_data='close')])

    await message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(btn))

@Client.on_message(filters.private & filters.command('upgrade'))
async def handle_upgrade(bot: Client, message: Message):

    if not Config.PREMIUM:
        return

    user = message.from_user

    if user.id in Config.ADMIN:
        return await message.reply_text(Txt.YOU_ARE_ADMIN_TEXT.format(user.mention))

    user_status = await db.get_user_status(user.id)
    if user_status['plan'] == 'free':
        btn = [[InlineKeyboardButton('ᴜᴘɢʀᴀᴅᴇ', callback_data='upgrade')], [
            InlineKeyboardButton('ᴄʟᴏsᴇ ✘', callback_data='close')]]

        return await message.reply_text(Txt.UPGRADE_MSG, reply_markup=InlineKeyboardMarkup(btn))


    await message.reply_text(f"Hᴇʏ {user.mention},**Yᴏᴜ'ʀᴇ ᴀʟʀᴇᴀᴅʏ ᴀ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀ 👑**")


@Client.on_message(filters.private & filters.command(['add_premium', 'premium']) & filters.user(Config.ADMIN))
async def handle_add_premium(bot: Client, message:Message):

    if not Config.PREMIUM:
        return

    if len(message.command) == 1 or len(message.command) > 2:
        return await message.reply_text('❗ **ᴘʟᴇᴀsᴇ sᴇɴᴅ ʟɪᴋᴇ ᴛʜɪs** `/add_premium 986277343`', reply_to_message_id=message.id)

    elif not message.command[1].isdigit():
        return await message.reply_text('❗ **ɪɴᴠᴀʟɪᴅ ғᴏʀᴍᴀᴛ**', reply_to_message_id=message.id)

    else:
        try:
            client_id = int(message.command[1])
            await db.add_premium(client_id, 'premium')
            user = await bot.get_users(int(client_id))
            await bot.send_message(chat_id=client_id, text=f"Hᴇʏ {user.first_name},\n**Yᴏᴜ'ʀᴇ ᴜᴘɢʀᴀᴅᴇ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ** ✅\n\n** ɴᴏᴡ ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ᴍᴇ ᴡɪᴛʜᴏᴜᴛ ᴀɴʏ ʀᴇsᴛʀɪᴄᴛɪᴏɴ **")
            await message.reply_text("**Usᴇʀ ʜᴀs ʙᴇᴇɴ ᴜᴘɢʀᴀᴅᴇ ᴀɴᴅ ɴᴏᴛɪғɪᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ ✅**", reply_to_message_id=message.id)
        except Exception as e:
            return await message.reply_text(f"**sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ**\n\n⚠️ **ERROR**: {e}")