import os
from pyrogram import Client, filters
from pyrogram.types import Message
from config import temp
from helper.database import db
from pyromod.exceptions.listener_timeout import ListenerTimeout


async def cancelled(message):
    if "/cancel" in message.text:
        await message.reply_text("**Process Cancelled.**")
        return True
    else:
        return False


@Client.on_message(
    filters.private & filters.command(["setrenameformats", "setrenameformat"])
)
async def setrenameformats(client: Client, message: Message):
    user_id = message.from_user.id
    try:
        askformat = await client.ask(
            chat_id=user_id,
            text="__**Send the rename format**__ **/cancel - cancel this process**",
            filters=filters.text,
            timeout=120,
        )
        if await cancelled(askformat):
            return
    except ListenerTimeout:
        await message.reply_text(
            "**You took too long..**\n\n⚠️ Restart by sending /SetRenameFormats"
        )
        return

    try:
        asktriggerr = await client.ask(
            chat_id=user_id,
            text="__**Send the trigger word**__ **/cancel - cancel this process**",
            filters=filters.text,
            timeout=120,
        )
        if await cancelled(asktriggerr):
            return
    except ListenerTimeout:
        await message.reply_text(
            "**You took too long..**\n\n⚠️ Restart by sending /SetRenameFormats"
        )
        return

    try:
        while True:
            askchannel = await client.ask(
                chat_id=user_id,
                text="__**❪ SET TARGET CHAT ❫**__\n\n**Forward a message from Your target chat /cancel - cancel this process or /no to avoid adding channel**\n\n __**⚠️Send /done when you are done adding channels**__",
                timeout=120,
                filters=filters.forwarded | filters.text,
            )

            if askchannel.text == "/no":
                if user_id not in temp.TEMPLATE_CHANNELS:
                    temp.TEMPLATE_CHANNELS.update({user_id: [None]})
                break

            elif askchannel.forward_from_chat:
                askchannel = askchannel.forward_from_chat.id
                if user_id not in temp.TEMPLATE_CHANNELS:
                    temp.TEMPLATE_CHANNELS.update({user_id: [askchannel]})

                else:
                    temp.TEMPLATE_CHANNELS[user_id].append(askchannel)
                continue

            elif await cancelled(askchannel):
                return

            else:
                if user_id not in temp.TEMPLATE_CHANNELS:
                    temp.TEMPLATE_CHANNELS.update({user_id: [None]})
                break

    except ListenerTimeout:
        await message.reply_text(
            "**You took too long..**\n\n⚠️ Restart by sending /SetRenameFormats"
        )
        return

    check = await db.set_rename_template(
        user_id, askformat.text, asktriggerr.text, temp.TEMPLATE_CHANNELS[user_id]
    )

    if not check:
        return await message.reply_text(
            "⚠️ **Be cautious make sure your trigger word is unique otherwise it'll conflict with files if same trigger word found in different files**\n\nTry Again..."
        )

    await message.reply_text(
        "**Your Format and Trigger has been saved Saved Successfully ✅**\n\n**To see all the saved formats send /SeeFormats**"
    )

    temp.TEMPLATE_CHANNELS.pop(user_id)


@Client.on_message(filters.private & filters.command(["seeformats", "seeformat"]))
async def getformats(client: Client, message: Message):
    user_id = message.from_user.id
    template = await db.get_rename_templates(user_id)

    if not template:
        return await message.reply_text("**You haven't saved any formats yet. 😑**")

    saved_formats = []

    for index, (key, value) in enumerate(template.items(), start=1):
        channels_info = []

        for idx, channel in enumerate(value[1], start=1):
            if value[1] is None:
                channels_info.append(f"**Channel :** Not Set\n")
            else:
                try:
                    channel_title = await client.get_chat(int(channel))
                    title = channel_title.title
                except:
                    title = "Not Set" if not channel else f"Not Admin ({channel})"

                channels_info.append(f"**Channel {index} ({idx}):** `{title}`\n")

        saved_formats.append(
            f"**Format {index}:** `{value[0]}`\n"
            f"**Trigger {index}:** `{key}`\n"
            f"{''.join(channels_info)}"
        )

    try:

        await message.reply_text("\n".join(saved_formats))

    except:
        s = await message.reply_text(
            "**Please Wait...**", reply_to_message_id=message.id
        )
        with open(
            f"{message.from_user.first_name}_formats.txt", "w", encoding="utf-8"
        ) as f:
            f.write("\n".join(saved_formats))
        await message.reply_document(f"{message.from_user.first_name}_formats.txt")
        await s.delete()
        os.remove(f"{message.from_user.first_name}_formats.txt")


@Client.on_message(filters.private & filters.command(["delformats", "delformat"]))
async def delformats(client: Client, message: Message):
    user_id = message.from_user.id

    if len(message.command) == 1:
        await db.remove_rename_template(user_id)
        return await message.reply_text(
            "**All Formats Deleted Successfully ✅**\n\n** To Delete Specific Format send `/delformat {Trigger Word}` **"
        )

    else:
        await db.remove_rename_template(user_id, message.command[1])
        return await message.reply_text(
            f"**The Format Related To This `{message.command[1]}` Trigger Has Been Deleted Successfully ✅**"
        )
