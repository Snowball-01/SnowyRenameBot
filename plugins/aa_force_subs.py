from pyrogram import Client, filters, enums 
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.errors import UserNotParticipant
from config import Config
from utility.database import db

async def not_subscribed(_, client, message):
    await db.add_user(client, message)
    if not Config.FORCE_SUB:
        return False
    try:             
        user = await client.get_chat_member(Config.FORCE_SUB, message.from_user.id) 
        if user.status == enums.ChatMemberStatus.BANNED:
            return True 
        else:
            return False                
    except UserNotParticipant:
        pass
    return True


@Client.on_message(filters.private & filters.create(not_subscribed))
async def forces_sub(client:Client, message:Message):
    buttons = [[InlineKeyboardButton(text="ᴊᴏɪɴ ɴᴏᴡ", url=f"https://t.me/{Config.FORCE_SUB}") ]]
    text = f"<b>Hello Dear {message.from_user.mention}\n\nYou Need To Join In My Channel To Use Me\n\nKindly Please Join Channel</b>"
    try:
        user = await client.get_chat_member(Config.FORCE_SUB, message.from_user.id)    
        if user.status == enums.ChatMemberStatus.BANNED:                                   
            return await client.send_message(message.from_user.id, text="Sorry You Are Banned To Use Me")  
    except UserNotParticipant:                       
        return await message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))
    return await message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))
          
@Client.on_message(filters.private | filters.text | filters.command)
async def handle_permit_user(client: Client, message: Message):
    userId = message.from_user.id
    permitUser = await db.get_permit_user(Config.ADMIN[0])
    print(userId)
    print(permitUser)
    if userId in list(map(int, permitUser)) or userId in Config.ADMIN:
        return await message.continue_propagation()
    
    else:
        return await message.reply_text("** __Don't Be Smart 😒__\nYou don't have enough permission to use me ! **\n\n** Cont. @Snowball_Official **")