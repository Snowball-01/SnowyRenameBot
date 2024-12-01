from datetime import datetime
from pytz import timezone
from pyrogram import Client, __version__
from pyrogram.errors import FloodWait
from pyrogram.raw.all import layer
from config import Config
from aiohttp import web
from utility import web_server
from utility.database import db
import pyrogram.utils
import logging
import logging.config
import asyncio

pyrogram.utils.MIN_CHANNEL_ID = -1009147483647

logging.config.fileConfig("logging.conf")
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("pymongo").setLevel(logging.ERROR)


class Bot(Client):

    def __init__(self):
        super().__init__(
            name="SnowyRename",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            workers=200,
            plugins={"root": "plugins"},
            sleep_threshold=15,
            max_concurrent_transmissions=64
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.mention = me.mention
        self.username = me.username  
        self.uptime = Config.BOT_UPTIME 
            
        if Config.WEBHOOK:
            app = web.AppRunner(await web_server())
            await app.setup()       
            await web.TCPSite(app, "0.0.0.0", 8080).start()     
        logging.info(f"{me.first_name} ✅ BOT STARTED SUCCESSFULLY ✅")
            
        if Config.LOG_CHANNEL:
            try:
                curr = datetime.now(timezone("Asia/Kolkata"))
                date = curr.strftime('%d %B, %Y')
                time = curr.strftime('%I:%M:%S %p')
                await self.send_message(Config.LOG_CHANNEL, f"**{me.mention} Is Restarted !!**\n\n📅 Date : `{date}`\n⏰ Time : `{time}`\n🌐 Timezone : `Asia/Kolkata`\n\n🉐 Version : `v{__version__} (Layer {layer})`</b>")                                
            except:
                logging.info("Please Make This Is Admin In Your Log Channel")

        success = failed = 0
        users = await db.get_all_users()
        async for user in users:
            chat_id = user["_id"]
            try:
                await self.send_message(
                    chat_id=chat_id, text="**๏[-ิ_•ิ]๏ bot restarted !**"
                )
                success += 1

            except FloodWait as e:
                await asyncio.sleep(e.value + 1)
                await self.send_message(
                    chat_id=chat_id, text="**๏[-ิ_•ิ]๏ bot restarted !**"
                )
                success += 1
            except Exception:
                pass
    
    async def stop(self, *args):
        await super().stop()
        logging.info("Bot Stopped ❌")
    
Bot().run()