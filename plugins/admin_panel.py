import traceback
from config import Config, Txt
from utility.database import db
from pyrogram.types import Message
from pyrogram import Client, filters
from pyrogram.errors import (
    FloodWait,
    InputUserDeactivated,
    UserIsBlocked,
    PeerIdInvalid,
)
import os, sys, time, asyncio, logging, datetime
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from utility.utils import start_clone_bot, user_client

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ADMIN_USER_ID = Config.ADMIN

# Flag to indicate if the bot is restarting
is_restarting = False


@Client.on_message(
    filters.private & filters.command("restart") & filters.user(ADMIN_USER_ID)
)
async def restart_bot(b, m):
    global is_restarting
    if not is_restarting:
        is_restarting = True
        await m.reply_text("**🔄 Restarting.....**")

        # Gracefully stop the bot's event loop
        b.stop()
        time.sleep(2)  # Adjust the delay duration based on your bot's shutdown time

        # Restart the bot process
        os.execl(sys.executable, sys.executable, *sys.argv)


@Client.on_message(filters.private & filters.command(["tutorial"]))
async def tutorial(bot, message):
    user_id = message.from_user.id
    format_template = await db.get_format_template(user_id)
    await message.reply_text(
        text=Txt.FILE_NAME_TXT.format(format_template=format_template),
        disable_web_page_preview=True,
    )


@Client.on_message(filters.command(["stats", "status"]) & filters.user(Config.ADMIN))
async def get_stats(bot, message):
    total_users = await db.total_users_count()
    uptime = time.strftime("%Hh%Mm%Ss", time.gmtime(time.time() - bot.uptime))
    start_t = time.time()
    st = await message.reply("**Accessing The Details.....**")
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    await st.edit(
        text=f"**--Bot Status--** \n\n**⌚️ Bot Uptime :** {uptime} \n**🐌 Current Ping :** `{time_taken_s:.3f} ms` \n**👭 Total Users :** `{total_users}`"
    )


@Client.on_message(
    filters.command("broadcast") & filters.user(Config.ADMIN) & filters.reply
)
async def broadcast_handler(bot: Client, m: Message):
    await bot.send_message(
        Config.LOG_CHANNEL,
        f"{m.from_user.mention} or {m.from_user.id} Is Started The Broadcast......",
    )
    all_users = await db.get_all_users()
    broadcast_msg = m.reply_to_message
    sts_msg = await m.reply_text("Broadcast Started..!")
    done = 0
    failed = 0
    success = 0
    start_time = time.time()
    total_users = await db.total_users_count()
    async for user in all_users:
        sts = await send_msg(user["_id"], broadcast_msg)
        if sts == 200:
            success += 1
        else:
            failed += 1
        if sts == 400:
            await db.delete_user(user["_id"])
        done += 1
        if not done % 20:
            await sts_msg.edit(
                f"Broadcast In Progress: \n\nTotal Users {total_users} \nCompleted : {done} / {total_users}\nSuccess : {success}\nFailed : {failed}"
            )
    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts_msg.edit(
        f"Bʀᴏᴀᴅᴄᴀꜱᴛ Cᴏᴍᴩʟᴇᴛᴇᴅ: \nCᴏᴍᴩʟᴇᴛᴇᴅ Iɴ `{completed_in}`.\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nFailed: {failed}"
    )


async def send_msg(user_id, message):
    try:
        await message.copy(chat_id=int(user_id))
        return 200
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return send_msg(user_id, message)
    except InputUserDeactivated:
        logger.info(f"{user_id} : Deactivated")
        return 400
    except UserIsBlocked:
        logger.info(f"{user_id} : Blocked The Bot")
        return 400
    except PeerIdInvalid:
        logger.info(f"{user_id} : User ID Invalid")
        return 400
    except Exception as e:
        logger.error(f"{user_id} : {e}")
        return 500
    
    

@Client.on_message(filters.private & filters.command("ban_user") & filters.user(Config.ADMIN))
async def ban(c: Client, m: Message):

    if len(m.command) == 1:
        await m.reply_text(
            f"Use this command to ban any user from the bot.\n\n"
            f"Usage:\n\n"
            f"`/ban_user user_id ban_duration ban_reason`\n\n"
            f"Eg: `/ban_user 1234567 28 You misused me.`\n"
            f"This will ban user with id `1234567` for `28` days for the reason `You misused me`.",
            quote=True
        )
        return

    try:
        user_id = int(m.command[1])
        ban_duration = int(m.command[2])
        ban_reason = ' '.join(m.command[3:])
        ban_log_text = f"Banning user {user_id} for {ban_duration} days for the reason {ban_reason}."
        try:
            await c.send_message(
                user_id,
                f"You are banned to use this bot for **{ban_duration}** day(s) for the reason __{ban_reason}__ \n\n"
                f"**Message from the admin**"
            )
            ban_log_text += '\n\nUser notified successfully!'
        except:
            traceback.print_exc()
            ban_log_text += f"\n\nUser notification failed! \n\n`{traceback.format_exc()}`"

        await db.ban_user(user_id, ban_duration, ban_reason)
        print(ban_log_text)
        await m.reply_text(
            ban_log_text,
            quote=True
        )
    except:
        traceback.print_exc()
        await m.reply_text(
            f"Error occoured! Traceback given below\n\n`{traceback.format_exc()}`",
            quote=True
        )


@Client.on_message(filters.private & filters.command("unban_user") & filters.user(Config.ADMIN))
async def unban(c: Client, m: Message):

    if len(m.command) == 1:
        await m.reply_text(
            f"Use this command to unban any user.\n\n"
            f"Usage:\n\n`/unban_user user_id`\n\n"
            f"Eg: `/unban_user 1234567`\n"
            f"This will unban user with id `1234567`.",
            quote=True
        )
        return

    try:
        user_id = int(m.command[1])
        unban_log_text = f"Unbanning user {user_id}"
        try:
            await c.send_message(
                user_id,
                f"Your ban is lifted!"
            )
            unban_log_text += '\n\nUser notified successfully!'
        except:
            traceback.print_exc()
            unban_log_text += f"\n\nUser notification failed! \n\n`{traceback.format_exc()}`"
        await db.remove_ban(user_id)
        print(unban_log_text)
        await m.reply_text(
            unban_log_text,
            quote=True
        )
    except:
        traceback.print_exc()
        await m.reply_text(
            f"Error occurred! Traceback given below\n\n`{traceback.format_exc()}`",
            quote=True
        )


@Client.on_message(filters.private & filters.command("banned_users") & filters.user(Config.ADMIN))
async def _banned_users(_, m: Message):

    all_banned_users = await db.get_all_banned_users()
    banned_usr_count = 0
    text = ''

    async for banned_user in all_banned_users:
        user_id = banned_user['id']
        ban_duration = banned_user['ban_status']['ban_duration']
        banned_on = banned_user['ban_status']['banned_on']
        ban_reason = banned_user['ban_status']['ban_reason']
        banned_usr_count += 1
        text += f"> **user_id**: `{user_id}`, **Ban Duration**: `{ban_duration}`, " \
                f"**Banned on**: `{banned_on}`, **Reason**: `{ban_reason}`\n\n"
    reply_text = f"Total banned user(s): `{banned_usr_count}`\n\n{text}"
    if len(reply_text) > 4096:
        with open('banned-users.txt', 'w') as f:
            f.write(reply_text)
        await m.reply_document('banned-users.txt', True)
        os.remove('banned-users.txt')
        return
    await m.reply_text(reply_text, True)
 

    
@Client.on_message(filters.private & filters.command('add_userbot') & filters.user(Config.ADMIN))
async def add_userbot(bot: Client, message: Message):
    try:
        bot_exist = await db.is_user_bot_exist(message.from_user.id)

        if bot_exist:
            return await message.reply_text('**⚠️ User Bot Already Exists**', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('User Bot', callback_data='userbot')]]))
    except:
        pass

    user_id = int(message.from_user.id)

    text = "<b>⚠️ DISCLAIMER ⚠️</b>\n\n<code>\nPlease add your pyrogram session with your own risk. Their is a chance to ban your account. My developer is not responsible if your account may get banned.</code>"
    await bot.send_message(user_id, text=text)
    msg = await bot.ask(chat_id=user_id, text="<b>send your pyrogram session.\nget it from @SnowStringGenBot - /cancel the process</b>")
    if msg.text == '/cancel':
        return await msg.reply('<b>process cancelled !</b>')
    elif len(msg.text) < 351:
        return await msg.reply('<b>invalid session sring</b>')
    try:
        user_account = await start_clone_bot(user_client(msg.text))
    except Exception as e:
        await message.reply_text(f"<b>USER BOT ERROR:</b> `{e}`")
        print('Error on line {}'.format(
            sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

    user = user_account.me

    details = {
        'id': user.id,
        'is_bot': False,
        'user_id': user_id,
        'name': user.first_name,
        'session': msg.text,
        'username': user.username
    }
    await db.add_user_bot(details)

    await message.reply_text("**User Bot Added Successfully ✅**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('❮ Back', callback_data='userbot')]]))


@Client.on_message(filters.private & filters.command('add_user') & filters.user(Config.ADMIN))
async def add_permit_user(client: Client, message:Message):

    if len(message.command) == 1:
        return await message.reply_text("** Wrong Command ❗**\n\n**Example :** `add_user 6852603512`")
    
    else:
        response = await db.add_permit_user(message.command[1])
        if response:
            return await message.reply_text(f"** User `{message.command[1]}` Added Successfully ** ✅")
        else:
            return await message.reply_text(f"** Something Went Wrong ** 🤔")


@Client.on_message(filters.private & filters.command('rmv_user') & filters.user(Config.ADMIN))
async def remove_permit_user(client: Client, message:Message):

    if len(message.command) == 1:
        return await message.reply_text("** Wrong Command ❗**\n\n**Example :** `rmv_user 6852603512`")
    
    else:
        response = await db.remove_permit_user(message.command[1])
        if response:
            return await message.reply_text(f"** User `{message.command[1]}` Removed Successfully ** ✅")
        else:
            return await message.reply_text(f"** Something Went Wrong ** 🤔")