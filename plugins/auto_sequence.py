import sys
from pyrogram import Client, filters, errors
import asyncio
from helper.database import db
from pyromod.exceptions.listener_timeout import ListenerTimeout
from helper.utils import humanbytes

SEQUENCE = {}
SEQUENCE_FILES = {}
SEQUENCE_FILES_NAME = {}


def myFUNC(e):
    if isinstance(e, dict):
        return e["file_name"]
    else:
        return ""


def notSEQUENCE(_, client, message):
    if message.from_user.id not in SEQUENCE:
        return False
    return True


@Client.on_message(filters.private & filters.command("startsequence"))
async def startsequence_cmd(client, message):
    if message.from_user.id in SEQUENCE:
        return await message.reply_text(
            "<b>Yᴏᴜ ᴀʀᴇ ᴄᴜʀʀᴇɴᴛʟʏ ɪɴ ᴀ ꜰɪʟᴇ sᴇQᴜᴇɴᴄɪɴɢ ᴘʀᴏᴄᴇss. Usᴇ /endsequence ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ꜰɪɴɪsʜ ɪᴛ.</b>"
        )
    SEQUENCE[message.from_user.id] = True
    await message.reply_text(
        "ʏᴏᴜ'ᴠᴇ sᴛᴀʀᴛᴇᴅ ᴀ ꜰɪʟᴇ sᴇQᴜᴇɴᴄɪɴɢ ᴘʀᴏᴄᴇss. Sᴇɴᴅ ᴛʜᴇ ꜰɪʟᴇs ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ sᴇQᴜᴇɴᴄᴇ ᴏɴᴇ ʙʏ ᴏɴᴇ.\n\nWʜᴇɴ ʏᴏᴜ'ʀᴇ ᴅᴏɴᴇ, Usᴇ /endsequence ᴛᴏ ꜰɪɴɪsʜ ᴀɴᴅ ɢᴇᴛ ᴛʜᴇ sᴇQᴜᴇɴᴄᴇᴅ ꜰɪʟᴇs."
    )


@Client.on_message(filters.private & filters.video & filters.create(notSEQUENCE))
async def sequencefiles_vid(client, message):

    media = getattr(message, message.media.value)
    c_caption = await db.get_caption(message.from_user.id)
    c_caption = c_caption.replace("Duration : {duration}", "").replace(
        "\nSize : {filesize}", "Size : {filesize}"
    )

    if c_caption:
        caption = c_caption.format(
            filename=media.file_name,
            filesize=humanbytes(message.video.file_size),
        )
    else:
        caption = f"**{media.file_name}**"

    # Creating the media info dictionary
    info = {"file_id": media.file_id, "file_name": media.file_name, "caption": caption}
    try:
        SEQUENCE_FILES[message.from_user.id].append(info)
    except:
        vp = []
        vp.append(info)
        SEQUENCE_FILES[message.from_user.id] = vp

    await message.reply("ꜰɪʟᴇ ʀᴇᴄᴇɪᴠᴇᴅ ᴀɴᴅ ᴀᴅᴅᴇᴅ ᴛᴏ ᴛʜᴇ sᴇQᴜᴇɴᴄɪɴɢ ᴘʀᴏᴄᴇss.")


@Client.on_message(filters.private & filters.document & filters.create(notSEQUENCE))
async def sequencefiles_doc(client, message):
    media = getattr(message, message.media.value)
    c_caption = await db.get_caption(message.from_user.id)
    c_caption = c_caption.replace("Duration : {duration}", "").replace(
        "\nSize : {filesize}", "Size : {filesize}"
    )

    if c_caption:
        caption = c_caption.format(
            filename=media.file_name,
            filesize=humanbytes(message.document.file_size),
        )
    else:
        caption = f"**{media.file_name}**"

    # Creating the media info dictionary
    info = {"file_id": media.file_id, "file_name": media.file_name, "caption": caption}

    try:
        SEQUENCE_FILES[message.from_user.id].append(info)
    except:
        vp = []
        vp.append(info)
        SEQUENCE_FILES[message.from_user.id] = vp

    await message.reply("ꜰɪʟᴇ ʀᴇᴄᴇɪᴠᴇᴅ ᴀɴᴅ ᴀᴅᴅᴇᴅ ᴛᴏ ᴛʜᴇ sᴇQᴜᴇɴᴄɪɴɢ ᴘʀᴏᴄᴇss.")


@Client.on_message(filters.private & filters.audio & filters.create(notSEQUENCE))
async def sequencefiles_aud(client, message):
    if message.from_user.id not in SEQUENCE:
        return

    media = getattr(message, message.media.value)
    c_caption = await db.get_caption(message.from_user.id)
    c_caption = c_caption.replace("Duration : {duration}", "").replace(
        "\nSize : {filesize}", "Size : {filesize}"
    )

    if c_caption:
        caption = c_caption.format(
            filename=media.file_name,
            filesize=humanbytes(message.audio.file_size),
        )
    else:
        caption = f"**{media.file_name}**"

    # Creating the media info dictionary
    info = {"file_id": media.file_id, "file_name": media.file_name, "caption": caption}
    try:
        SEQUENCE_FILES[message.from_user.id].append(info)
    except:
        vp = []
        vp.append(info)
        SEQUENCE_FILES[message.from_user.id] = vp

    await message.reply("ꜰɪʟᴇ ʀᴇᴄᴇɪᴠᴇᴅ ᴀɴᴅ ᴀᴅᴅᴇᴅ ᴛᴏ ᴛʜᴇ sᴇQᴜᴇɴᴄɪɴɢ ᴘʀᴏᴄᴇss.")


@Client.on_message(filters.command("endsequence") & filters.private)
async def endsequence_cmd(client: Client, message):
    if message.from_user.id not in SEQUENCE:
        return await message.reply(
            "You have not started a sequence yet. Use /startsequence command to start a new sequence."
        )
    if len(SEQUENCE_FILES) == 0:
        return await message.reply(
            "No files to sequence. Send some files with /startsequence first."
        )
    sequence_files_names = sorted(
        SEQUENCE_FILES[message.from_user.id],
        key=lambda x: (type(x) is dict and x.get("file_name")) or x,
    )

    try:
        channel = await client.ask(
            message.chat.id,
            "** (FORWRAD MESSAGE)\n\n Forward me message the channel you want to send these sequenced files to (make sure I'm admin in that channel).**\n\nIf you want files here send /no",
            timeout=60,
        )
        if channel.text == "/no":

            for file_name in sequence_files_names:
                try:
                    vp = file_name
                    await message.reply_cached_media(
                        file_id=vp["file_id"], caption=vp["caption"]
                    )
                except errors.FloodWait as e:
                    await asyncio.sleep(e.value)
                    await message.reply_cached_media(
                        file_id=vp["file_id"], caption=vp["file_name"]
                    )
                    continue
                except Exception as e:
                    print(e)
                    continue

        elif channel.forward_from_chat:
            for file_name in sequence_files_names:
                try:
                    vp = file_name
                    await client.send_cached_media(
                        chat_id=int(channel.forward_from_chat.id),
                        file_id=vp["file_id"],
                        caption=vp["file_name"],
                    )
                except errors.FloodWait as e:
                    await asyncio.sleep(e.value)
                    await client.send_cached_media(
                        chat_id=int(channel.forward_from_chat.id),
                        file_id=vp["file_id"],
                        caption=vp["file_name"],
                    )
                    continue
                except Exception as e:
                    print(e)
        else:
            return await message.reply(
                "**Invalid channel. Send /startsequence again. **"
            )
    except ListenerTimeout:
        for file_name in sequence_files_names:
            try:
                vp = file_name
                msg = await message.reply_cached_media(
                    file_id=vp["file_id"], caption=vp["file_name"]
                )
            except errors.FloodWait as e:
                await asyncio.sleep(e.value)
                await message.reply_cached_media(
                    file_id=vp["file_id"], caption=vp["file_name"]
                )
                continue

    del SEQUENCE_FILES[message.from_user.id]
    del SEQUENCE[message.from_user.id]
    await message.reply(
        f"File sequencing completed. You have received or sent to target channel {len(sequence_files_names)} sequenced files."
    )
