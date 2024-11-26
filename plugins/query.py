import os
import shutil
import time
from pyrogram import Client, filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    ForceReply,
)
from config import Config, Txt
from helper.database import db
import random
import psutil
from helper.utils import humanbytes
from plugins.features import feature_keyboard


@Client.on_callback_query()
async def cd_handler(client: Client, query: CallbackQuery):
    data = query.data
    user_id = query.from_user.id
    text = "** ʏᴏᴜ ᴄᴀɴ ᴛᴏɢɢʟᴇ ᴛʜᴇ ᴍᴇᴛᴀᴅᴀᴛᴀ & ᴀᴜᴛᴏ-ʀᴇɴᴀᴍᴇ **"

    if data == "home":
        await query.message.edit_text(
            text=Txt.START_TXT.format(query.from_user.mention),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "⛅ ᴜᴘᴅᴀᴛᴇ", url="https://t.me/Kdramaland"
                        ),
                        InlineKeyboardButton("🌨️ sᴜᴘᴘᴏʀᴛ", url="https://t.me/SnowDevs"),
                    ],
                    [
                        InlineKeyboardButton("❗ ʜᴇʟᴘ", callback_data="help"),
                        InlineKeyboardButton("❄️ ᴀʙᴏᴜᴛ", callback_data="about"),
                    ],
                    [InlineKeyboardButton("⚙️ sᴇʀᴠᴇʀ sᴛᴀᴛs", callback_data="stats")],
                ]
            ),
        )
    elif data == "caption":
        await query.message.edit_text(
            text=Txt.CAPTION_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("✘ ᴄʟᴏsᴇ", callback_data="close"),
                        InlineKeyboardButton("⟪ ʙᴀᴄᴋ", callback_data="help"),
                    ]
                ]
            ),
        )
    elif data == "help":
        await query.message.edit_text(
            text=Txt.HELP_TXT.format(client.mention),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🖼️ ᴛʜᴜᴍʙɴᴀɪʟ", callback_data="thumbnail"),
                        InlineKeyboardButton("✏️ ᴄᴀᴘᴛɪᴏɴ", callback_data="caption"),
                    ],
                    [
                        InlineKeyboardButton(
                            "⌨ ғɪʟᴇ sᴇǫᴜᴇɴᴄᴇ", callback_data="sequence"
                        ),
                        InlineKeyboardButton(
                            "📟 ᴍᴇᴛᴀᴅᴀᴛᴀ", callback_data="howmetadata"
                        ),
                    ],
                    [
                        InlineKeyboardButton("🏠 ʜᴏᴍᴇ", callback_data="home"),
                        InlineKeyboardButton("💰 ᴅᴏɴᴀᴛᴇ", callback_data="donate"),
                    ],
                ]
            ),
        )

    elif data == "stats":
        buttons = [
            [
                InlineKeyboardButton("⟲ ʀᴇʟᴏᴀᴅ", callback_data="stats"),
                InlineKeyboardButton("⟪ ʙᴀᴄᴋ", callback_data="home"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        currentTime = time.strftime(
            "%Hh%Mm%Ss", time.gmtime(time.time() - Config.BOT_UPTIME)
        )
        total, used, free = shutil.disk_usage(".")
        total = humanbytes(total)
        used = humanbytes(used)
        free = humanbytes(free)
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage("/").percent
        await query.message.edit_media(
            InputMediaPhoto(
                random.choice(Config.PICS),
                Txt.STATS_TXT.format(
                    currentTime, total, used, disk_usage, free, cpu_usage, ram_usage
                ),
            ),
            reply_markup=reply_markup,
        )

    elif data == "donate":
        await query.message.edit_text(
            text=Txt.DONATE_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("✘ ᴄʟᴏsᴇ", callback_data="close"),
                        InlineKeyboardButton("⟪ ʙᴀᴄᴋ", callback_data="help"),
                    ]
                ]
            ),
        )

    elif data == "thumbnail":
        await query.message.edit_caption(
            caption=Txt.THUMBNAIL_TXT,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("✘ ᴄʟᴏsᴇ", callback_data="close"),
                        InlineKeyboardButton("⟪ ʙᴀᴄᴋ", callback_data="help"),
                    ]
                ]
            ),
        )

    elif data == "sequence":
        await query.message.edit_caption(
            caption=Txt.FILE_SEQUENCE,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("✘ ᴄʟᴏsᴇ", callback_data="close"),
                        InlineKeyboardButton("⟪ ʙᴀᴄᴋ", callback_data="help"),
                    ]
                ]
            ),
        )

    elif data == "howmetadata":
        await query.message.edit_caption(
            caption=Txt.HOW_METADATA_TXT,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("✘ ᴄʟᴏsᴇ", callback_data="close"),
                        InlineKeyboardButton("⟪ ʙᴀᴄᴋ", callback_data="help"),
                    ]
                ]
            ),
        )

    elif data == "about":
        await query.message.edit_text(
            text=Txt.ABOUT_TXT.format(client.mention),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("✘ ᴄʟᴏsᴇ", callback_data="close"),
                        InlineKeyboardButton("⟪ ʙᴀᴄᴋ", callback_data="home"),
                    ]
                ]
            ),
        )

    elif data == "metadata_on":
        await db.set_metadata(user_id, False)
        await query.message.edit(
            text=text, reply_markup=await feature_keyboard(user_id)
        )

    elif data == "metadata_off":
        await db.set_metadata(user_id, True)
        await query.message.edit(
            text=text, reply_markup=await feature_keyboard(user_id)
        )

    elif data == "autorename_on":
        await db.set_autorename(user_id, False)
        await query.message.edit(
            text=text, reply_markup=await feature_keyboard(user_id)
        )

    elif data == "autorename_off":
        await db.set_autorename(user_id, True)
        await query.message.edit(
            text=text, reply_markup=await feature_keyboard(user_id)
        )

    elif data == "manual_rename":
        await query.message.delete()
        await query.message.reply_text(
            "__**ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ɴᴇᴡ ғɪʟᴇ ɴᴀᴍᴇ...**__",
            reply_to_message_id=query.message.reply_to_message.id,
            reply_markup=ForceReply(True),
        )

    elif data.startswith("media_"):
        type = data.split("_")[1]
        autorename = await db.get_autorename(query.from_user.id)
        if type == "video":
            if not autorename:
                return await query.answer(
                    f"ʜᴇʏ {query.from_user.first_name},\n\nᴀᴜᴛᴏ-ʀᴇɴᴀᴍᴇ ᴍᴜsᴛ ʙᴇ ᴇɴᴀʙʟᴇᴅ ʙᴇғᴏʀᴇ ᴄʜᴀɴɢɪɴɢ ᴛʜᴇ ғɪʟᴇ ᴛʏᴘᴇ.",
                    show_alert=True,
                )

            await db.set_media_preference(query.from_user.id, "document")
            keybaord = await feature_keyboard(query.from_user.id)
            await query.message.edit(text=text, reply_markup=keybaord)

        elif type == "document":
            if not autorename:
                return await query.answer(
                    f"ʜᴇʏ {query.from_user.first_name},\n\nᴀᴜᴛᴏ-ʀᴇɴᴀᴍᴇ ᴍᴜsᴛ ʙᴇ ᴇɴᴀʙʟᴇᴅ ʙᴇғᴏʀᴇ ᴄʜᴀɴɢɪɴɢ ᴛʜᴇ ғɪʟᴇ ᴛʏᴘᴇ.",
                    show_alert=True,
                )

            await db.set_media_preference(query.from_user.id, "audio")
            keybaord = await feature_keyboard(query.from_user.id)
            await query.message.edit(text=text, reply_markup=keybaord)

        else:
            if not autorename:
                return await query.answer(
                    f"ʜᴇʏ {query.from_user.first_name},\n\nᴀᴜᴛᴏ-ʀᴇɴᴀᴍᴇ ᴍᴜsᴛ ʙᴇ ᴇɴᴀʙʟᴇᴅ ʙᴇғᴏʀᴇ ᴄʜᴀɴɢɪɴɢ ᴛʜᴇ ғɪʟᴇ ᴛʏᴘᴇ.",
                    show_alert=True,
                )

            await db.set_media_preference(query.from_user.id, "video")
            keybaord = await feature_keyboard(query.from_user.id)
            await query.message.edit(text=text, reply_markup=keybaord)

    elif data == "userbot":
        userBot = await db.get_user_bot(query.from_user.id)

        text = f"Name: {userBot['name']}\nUserName: @{userBot['username']}\nUserId: `{userBot['user_id']}`"

        await query.message.edit(
            text=text,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("❌ ʀᴇᴍᴏᴠᴇ ❌", callback_data="rmuserbot")],
                    [InlineKeyboardButton("✘ ᴄʟᴏsᴇ ✘", callback_data="close")],
                ]
            ),
        )

    elif data == "rmuserbot":
        try:
            await db.remove_user_bot(query.from_user.id)
            await query.message.edit(
                text="**User Bot Removed Successfully ✅**",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("✘ ᴄʟᴏsᴇ ✘", callback_data="close")]]
                ),
            )
        except:
            await query.answer(
                f"Hey {query.from_user.first_name}\n\n You have already deleted the user"
            )

    elif data == "upgrade":
        btn = [
            [
                InlineKeyboardButton(
                    "ᴘᴀʏ ᴛᴏ ᴀᴅᴍɪɴ", url="https://t.me/Snowball_Official"
                )
            ],
            [InlineKeyboardButton("ᴄʟᴏsᴇ ✘", callback_data="close")],
        ]
        markup = InlineKeyboardMarkup(btn)
        await query.message.edit(Txt.UPGRADE_MSG, reply_markup=markup)

    elif data == "close":
        try:
            if os.path.exists(f"downloads/{user_id}"):
                shutil.rmtree(f"downloads/{user_id}")

            if os.path.exists(f"metadata/{user_id}"):
                shutil.rmtree(f"metadata/{user_id}")

            await query.message.delete()
            await query.message.reply_to_message.delete()
            await query.message.continue_propagation()

        except:
            if os.path.exists(f"downloads/{user_id}"):
                shutil.rmtree(f"downloads/{user_id}")

            if os.path.exists(f"metadata/{user_id}"):
                shutil.rmtree(f"metadata/{user_id}")

            await query.message.delete()
            await query.message.continue_propagation()
