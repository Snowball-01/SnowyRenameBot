import re, os, time
id_pattern = re.compile(r'^.\d+$') 



class Config(object):
    # pyro client config
    API_ID    = os.environ.get("API_ID", "21508774") # ⚠️ Required
    API_HASH  = os.environ.get("API_HASH", "970a0c33fc5a27e835c31ec7811e0090") # ⚠️ Required
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "6480471455:AAETTfVpa6w2ll1aUSxTUXtYlH7X5ss4_Yc") # ⚠️ Required

    # database config
    DB_NAME = os.environ.get("DB_NAME","SnowyRename")
    DB_URL  = os.environ.get("DB_URL","mongodb+srv://TesterSnowBot:TesterSnowBot@cluster0.wp5hmpy.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0") # ⚠️ Required

    # other configs
    BOT_UPTIME  = time.time()
    PICS = os.environ.get("PICS", "https://telegra.ph/file/13c2745dcd19887d76812.jpg https://telegra.ph/file/e170c2bc5c1429e65f1ca.jpg https://telegra.ph/file/c65f5b8efd59c929b1e8b.jpg https://telegra.ph/file/8fcb3154d71285cd7af20.jpg https://telegra.ph/file/099ad55fdc723a058e12f.jpg https://telegra.ph/file/8977b1767518b6bf31312.jpg https://telegra.ph/file/52d7fc0a599a2c9b521bd.jpg").split()
    ADMIN       = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get('ADMIN', '6065594762').split()] # ⚠️ Required
    FORCE_SUB   = os.environ.get("FORCE_SUB", "Kdramalanad") # ⚠️ Required Username without @
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1001971176803")) # ⚠️ Required must start with (-100)
    PREMIUM = os.environ.get("PREMIUM", True)

    # wes response configuration
    WEBHOOK = os.environ.get("WEBHOOK", False)


class Txt(object):
    # part of text configuration
        
    START_TXT = """Hello {} 
    
➻ ** This Is An Advanced And Yet Powerful Rename Bot. **
    
➻ ** Using This Bot You Can Auto Rename Of Your Files. **
    
➻ ** This Bot Also Supports Custom Thumbnail And Custom Caption. **
"""
    
    FILE_NAME_TXT = """<b><u>SETUP AUTO RENAME FORMAT</u></b>

Use These Keywords To Setup Custom File Name

✓ episode :- To Replace Episode Number
✓ quality :- To Replace Video Resolution

<b>➻ Example :</b> <code> /autorename Naruto Shippuden S02 - Episode - quality  [Dual Audio] - @Kdramaland </code>

<b>➻ Your Current Auto Rename Format :</b> <code>{format_template}</code> """

    FILE_SEQUENCE = """
<b><u>⌨  HOW TO USE FILE SEQUENCE FEATURE</u></b>

1. Usᴇ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ /startsequence ᴛᴏ ʙᴇɢɪɴ ᴀ ꜰɪʟᴇ sᴇQᴜᴇɴᴄɪɴɢ ᴘʀᴏᴄᴇss.
2. Sᴇɴᴅ ᴛʜᴇ ꜰɪʟᴇs ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ sᴇQᴜᴇɴᴄᴇ ᴏɴᴇ ʙʏ ᴏɴᴇ.
3. Wʜᴇɴ ʏᴏᴜ'ʀᴇ ᴅᴏɴᴇ, Usᴇ /endsequence ᴛᴏ ꜰɪɴɪsʜ ᴀɴᴅ ɢᴇᴛ ᴛʜᴇ sᴇQᴜᴇɴᴄᴇᴅ ꜰɪʟᴇs.
"""

    HOW_METADATA_TXT = """
<b><u>📟  HOW TO SET & USE METADATA FEATURE</u></b>

1. Usᴇ /metadata ᴛᴏ sᴇᴛ ᴄᴜsᴛᴏᴍ ᴍᴇᴛᴀᴅᴀᴛᴀ ᴄᴏᴅᴇ
2. Sᴇɴᴅ /features ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ᴛᴏɢɢʟᴇ (ᴇɴᴀʙʟᴇ ᴏʀ ᴅɪsᴀʙʟᴇ) ᴍᴇᴛᴀᴅᴀᴛᴀ
"""
    
    ABOUT_TXT = """
<b>
➥ ᴍy ɴᴀᴍᴇ : {}
➥ Pʀᴏɢʀᴀᴍᴇʀ : <a href=https://t.me/Snowball_Official>ѕησωвαℓℓ ❄️</a> 
➥ ꜰᴏᴜɴᴅᴇʀ ᴏꜰ : <a href=https://t.me/Kdramaland>K-Lᴀɴᴅ</a>
➥ Lɪʙʀᴀʀy : <a href=https://github.com/pyrogram>Pyʀᴏɢʀᴀᴍ</a>
➥ Lᴀɴɢᴜᴀɢᴇ: <a href=https://www.python.org>Pyᴛʜᴏɴ 3</a>
➥ Dᴀᴛᴀ Bᴀꜱᴇ: <a href=https://cloud.mongodb.com>Mᴏɴɢᴏ DB</a>
➥ ᴍʏ ꜱᴇʀᴠᴇʀ : <a href=https://dashboard.heroku.com>Heroku</a>
➥ ᴠᴇʀsɪᴏɴ : v3.0.0
</b>
"""

    STATS_TXT = """
╔════❰ sᴇʀᴠᴇʀ sᴛᴀᴛs  ❱═❍⊱❁۪۪
║╭━━━━━━━━━━━━━━━➣
║┣⪼ ᴜᴩᴛɪᴍᴇ: `{0}`
║┣⪼ ᴛᴏᴛᴀʟ sᴘᴀᴄᴇ: `{1}`
║┣⪼ ᴜsᴇᴅ: `{2} ({3}%)`
║┣⪼ ꜰʀᴇᴇ: `{4}`
║┣⪼ ᴄᴘᴜ: `{5}%`
║┣⪼ ʀᴀᴍ: `{6}%`
║╰━━━━━━━━━━━━━━━➣
╚══════════════════❍⊱❁۪۪        
"""

    AUTO_RENAME_TEXT = """**__SETUP AUTO RENAME FORMAT__**

Use These Keywords To Setup Custom File Name

✓ episode :- To Replace Episode Number
✓ quality :- To Replace Video Resolution

**➻ Example :** 

> • ** Step 1: Use the /setrenameformat command. **
** This will prompt you to set a renaming format. **

For example:
`Naruto Shippuden S02 - EPepisode - quality [Dual Audio] - @Klands`

> • ** Step 2: Set the trigger. **
** The trigger is used to identify files for automatic renaming. If a file matches the trigger, it will be renamed according to the format you’ve set. **

**__Note:__**

> ** If no matching trigger is found, the system will prompt you to manually rename the file. ** \n
> ** Ensure your trigger is relevant and specific to your file patterns for seamless renaming. **

**➻ Your Current Auto Rename Format :** /seeformats """
    
    THUMBNAIL_TXT = """<b><u>🖼️  HOW TO SET THUMBNAIL</u></b>
    
⦿ You Can Add Custom Thumbnail Simply By Sending A Photo To Me....
    
⦿ /viewthumb - Use This Command To See Your Thumbnail
⦿ /delthumb - Use This Command To Delete Your Thumbnail"""

    CAPTION_TXT = """<b><u>📝  HOW TO SET CAPTION</u></b>
    
⦿ /set_caption - Use This Command To Set Your Caption
⦿ /see_caption - Use This Command To See Your Caption
⦿ /del_caption - Use This Command To Delete Your Caption"""

    PROGRESS_BAR = """<b>\n
╭━━━━❰ᴘʀᴏɢʀᴇss ʙᴀʀ❱━➣
┣⪼ 🗃️ Sɪᴢᴇ: {1} | {2}
┣⪼ ⏳️ Dᴏɴᴇ : {0}%
┣⪼ 🚀 Sᴩᴇᴇᴅ: {3}/s
┣⪼ ⏰️ Eᴛᴀ: {4}
╰━━━━━━━━━━━━━━━➣ </b>"""
    
    
    DONATE_TXT = """<b>🥲 Thanks For Showing Interest In Donation! ❤️</b>
    
<b>Your generous donation, no matter the amount, is sincerely appreciated and will greatly support our bot's development.</b>
    
<b>🇮🇳 UPI ID:</b> <code>riteshraushan30@oksbi</code> """
    
    HELP_TXT = """<b>Hey</b> {}
    
Here Is The Help For My Commands."""

    UPGRADE_MSG = """
💸 ᴡʜᴀᴛ ʏᴏᴜ'ʟʟ ɢᴇᴛ ɪғ ʏᴏᴜ'ʀᴇ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀ ? 

💠 **Nᴏ ʀᴇsᴛʀɪᴄᴛɪᴏɴ**
💠 **Aᴄᴄᴇss ᴛᴏ ᴀʟʟ ғᴇᴀᴛᴜʀᴇs**
💠 **4ɢ ʀᴇɴᴀᴍᴇs**
💠 **ᴄᴀɴ ᴜsᴇ ᴀᴜᴛᴏ ʀᴇɴᴀᴍᴇ ғᴇᴀᴛᴜʀᴇ**

☛ Pʀɪᴄᴇ : ₹50/month

**sᴏ ᴡʜᴀᴛ ʏᴏᴜ'ʀᴇ ᴡᴀɪᴛɪɴɢ ғᴏʀ ᴜᴘɢʀᴀᴅᴇ ɴᴏᴡ 🔥**

🇮🇳 UPI ID : `riteshraushan30@oksbi`
"""
    YOU_ARE_ADMIN_TEXT = """
Hᴇʏ {},

**Yᴏᴜ ᴀʀᴇ ᴀᴅᴍɪɴ ʏᴏᴜ ᴅᴏɴ'ᴛ ɴᴇᴇᴅ ᴘʀᴇᴍɪᴜᴍ ʏᴏᴜ ᴄᴀɴ ᴀᴄᴄᴇss ᴀʟʟ ᴛʜᴇ ғᴇᴀᴛᴜʀᴇs 🔰**
"""

    SEND_METADATA = """
❪ SET CUSTOM METADATA ❫

☞ Fᴏʀ Exᴀᴍᴘʟᴇ:-

◦ <code> -map 0 -c:s copy -c:a copy -c:v copy -metadata title="Powered By:- @Kdramaland" -metadata author="@Snowball_Official" -metadata:s:s title="Subtitled By :- @Kdramaland" -metadata:s:a title="By :- @Kdramaland" -metadata:s:v title="By:- @Snowball_Official" </code>

📥 Fᴏʀ Hᴇʟᴘ Cᴏɴᴛ. @Snowball_Official
"""

class temp(object):
    TEMPLATE_CHANNELS = {}
    AUTO_RENAME_QUEUE = {}
    USERS_IN_QUEUE = []
