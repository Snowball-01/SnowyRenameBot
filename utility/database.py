import datetime
import motor.motor_asyncio
from config import Config
from .utils import send_log
from dateutil.relativedelta import relativedelta


class Database:

    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.user
        self.bot = self.db.bot
        self.config = self.db.config
    
    def admin_user(self, id):
        return dict(
            _id=int(id),
            join_date=datetime.date.today().isoformat(),
            permit_user = []
        )

    def new_user(self, id):
        return dict(
            _id=int(id),  # Add this line for the user id
            join_date=datetime.date.today().isoformat(),
            user_type=dict(is_premium=False, plan="free", plan_expire_on=None),
            ban_status=dict(
                is_banned=False,
                ban_duration=0,
                banned_on=datetime.date.max.isoformat(),
                ban_reason="",
            ),
        )

    async def add_user(self, b, m):
        u = m.from_user
        if not await self.is_user_exist(u.id):
            if u.id in Config.ADMIN:
                user = self.admin_user(u.id)
            else:
                user = self.new_user(u.id)
            await self.col.insert_one(user)
            await send_log(b, u)

            config = dict(
                _id=int(u.id),  # Add this line for the user id
                file_id=None,  # Add this line for the file id
                caption=None,  # Add this line for the caption
                autorename=None,  # Add this line for the autorename
                media_type="video",  # Add this line for the media type
                prefix=None,  # Add this line for the prefix
                suffix=None,  # Add this line for the suffix
                metadata=False,  # Add this line for the metadata
                rename_template={},  # Add this line for the rename template
                metadata_code=""" -map 0 -c:s copy -c:a copy -c:v copy -metadata title="Powered By:- @Kdramaland" -metadata author="@Snowball_Official" -metadata:s:s title="Subtitled By :- @Kdramaland" -metadata:s:a title="By :- @Kdramaland" -metadata:s:v title="By:- @Snowball_Official" """,  # Add this line for the metadata code
            )

            await self.config.insert_one(config)

    async def is_user_exist(self, id):
        user = await self.col.find_one({"_id": int(id)})
        return bool(user)
    
    async def get_permit_user(self, id):
        admin = await self.col.find_one({"_id": int(Config.ADMIN[0])})
        permit_user = admin.get("permit_user", [])
        return permit_user if permit_user else []
    
    async def add_permit_user(self, id):
        # Retrieve the current permit_user list for the admin
        admin_user = await self.col.find_one({"_id": int(Config.ADMIN[0])})
        permit_users = admin_user.get("permit_user", [])  # Ensure permit_user is a list
        
        # Check if the ID is already in the list
        if id not in permit_users:
            permit_users.append(id)  # Add the ID if it doesn't exist

            # Update the database with the new list
            await self.col.update_one(
                {"_id": int(Config.ADMIN[0])}, {"$set": {"permit_user": permit_users}}
            )
            return True
        return False

    async def remove_permit_user(self, id):
        # Retrieve the current permit_user list for the admin
        admin_user = await self.col.find_one({"_id": int(Config.ADMIN[0])})
        permit_users = admin_user.get("permit_user", [])  # Ensure permit_user is a list
        
        # Check if the ID exists in the list
        if id in permit_users:
            permit_users.remove(id)  # Remove the ID if it exists

            # Update the database with the new list
            await self.col.update_one(
                {"_id": int(Config.ADMIN[0])}, {"$set": {"permit_user": permit_users}}
            )
            return True
        return False

    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        all_users = self.col.find({})
        return all_users

    async def delete_user(self, user_id):
        await self.col.delete_many({"_id": int(user_id)})

    async def add_user_bot(self, user_datas):
        if not await self.is_user_bot_exist(user_datas["user_id"]):
            await self.bot.insert_one(user_datas)

    async def remove_user_bot(self, user_id):
        await self.bot.delete_many({"user_id": int(user_id), "is_bot": False})

    async def is_user_bot_exist(self, user_id):
        user = await self.bot.find_one({"user_id": user_id, "is_bot": False})
        return bool(user)

    async def get_user_bot(self, user_id: int):
        user = await self.bot.find_one({"user_id": user_id, "is_bot": False})
        return user if user else None

    async def remove_user_bot(self, user_id):
        await self.bot.delete_many({"user_id": int(user_id), "is_bot": False})

    async def set_thumbnail(self, id, file_id):
        await self.config.update_one({"_id": int(id)}, {"$set": {"file_id": file_id}})

    async def get_thumbnail(self, id):
        user = await self.config.find_one({"_id": int(id)})
        return user.get("file_id", None)

    async def set_caption(self, id, caption):
        await self.config.update_one({"_id": int(id)}, {"$set": {"caption": caption}})

    async def get_caption(self, id):
        user = await self.config.find_one({"_id": int(id)})
        return user.get("caption", None)

    async def set_autorename(self, id, autorename):
        await self.config.update_one(
            {"_id": int(id)}, {"$set": {"autorename": autorename}}
        )

    async def get_autorename(self, id):
        user = await self.config.find_one({"_id": int(id)})
        return user.get("autorename", None)

    async def set_media_preference(self, id, media_type):
        await self.config.update_one(
            {"_id": int(id)}, {"$set": {"media_type": media_type}}
        )

    async def get_media_preference(self, id):
        user = await self.config.find_one({"_id": int(id)})
        return user.get("media_type", None)

    async def set_metadata(self, id, bool_meta):
        await self.config.update_one(
            {"_id": int(id)}, {"$set": {"metadata": bool_meta}}
        )

    async def get_metadata(self, id):
        user = await self.config.find_one({"_id": int(id)})
        return user.get("metadata", None)

    async def set_metadata_code(self, id, metadata_code):
        await self.config.update_one(
            {"_id": int(id)}, {"$set": {"metadata_code": metadata_code}}
        )

    async def get_metadata_code(self, id):
        user = await self.config.find_one({"_id": int(id)})
        return user.get("metadata_code", None)

    async def set_prefix(self, id, prefix):
        await self.config.update_one({"_id": int(id)}, {"$set": {"prefix": prefix}})

    async def get_prefix(self, id):
        user = await self.config.find_one({"_id": int(id)})
        return user.get("prefix", None)

    async def set_suffix(self, id, suffix):
        await self.config.update_one({"_id": int(id)}, {"$set": {"suffix": suffix}})

    async def get_suffix(self, id):
        user = await self.config.find_one({"_id": int(id)})
        return user.get("suffix", None)

    async def remove_ban(self, id):
        ban_status = dict(
            is_banned=False,
            ban_duration=0,
            banned_on=datetime.date.max.isoformat(),
            ban_reason="",
        )
        await self.col.update_one({"_id": id}, {"$set": {"ban_status": ban_status}})

    async def ban_user(self, user_id, ban_duration, ban_reason):
        ban_status = dict(
            is_banned=True,
            ban_duration=ban_duration,
            banned_on=datetime.date.today().isoformat(),
            ban_reason=ban_reason,
        )
        await self.col.update_one(
            {"_id": user_id}, {"$set": {"ban_status": ban_status}}
        )

    async def get_ban_status(self, id):
        default = dict(
            is_banned=False,
            ban_duration=0,
            banned_on=datetime.date.max.isoformat(),
            ban_reason="",
        )
        user = await self.col.find_one({"_id": int(id)})
        return user.get("ban_status", default)

    async def get_all_banned_users(self):
        banned_users = self.col.find({"ban_status.is_banned": True})
        return banned_users

    async def add_premium(self, user_id, plan):
        # Get today's date
        today = datetime.date.today()

        # Calculate the date after one month
        next_month = today + relativedelta(months=1)

        user_type = dict(
            is_premium=True,
            plan=plan,
            plan_expire_on=str(next_month),
        )
        await self.col.update_one(
            {"_id": int(user_id)}, {"$set": {"user_type": user_type}}
        )

    async def remove_premium(self, id):
        user_type = dict(
            is_premium=False,
            plan="free",
            plan_expire_on=None,
        )
        await self.col.update_one({"_id": int(id)}, {"$set": {"user_type": user_type}})

    async def get_user_status(self, id):
        default = dict(
            is_premium=False,
            plan="free",
            plan_expire_on=None,
        )
        user = await self.col.find_one({"_id": int(id)})
        return user.get("user_type", default)

    async def get_all_premium_users(self):
        all_premium_users = self.col.find({"user_type.is_premium": True})
        return all_premium_users

    async def set_rename_template(self, id, rename_format, trigger_word, channel_id_array):
    
        user = await self.config.find_one({"_id": int(id)})
        defaultformat = dict(user.get("rename_template", {}))

        if trigger_word.lower() in [key.lower() for key in defaultformat.keys()]:
            return False

        defaultformat.update({trigger_word: [rename_format, channel_id_array]})

        await self.config.update_one(
            {"_id": int(id)}, {"$set": {"rename_template": defaultformat}}
        )
        return True


    async def get_rename_templates(self, id):
        user = await self.config.find_one({"_id": int(id)})
        return user.get("rename_template", None)

    async def remove_rename_template(self, id, trigger_word=None):
    
        if trigger_word:
            user = await self.config.find_one({"_id": int(id)})
            defaultformat = dict(user.get("rename_template", {}))

            for key in defaultformat.keys():
                if key.lower() == trigger_word.lower():
                    defaultformat.pop(key)
                    await self.config.update_one(
                        {"_id": int(id)}, {"$set": {"rename_template": defaultformat}}
                    )
                    break

        else:
            await self.config.update_one(
                {"_id": int(id)}, {"$set": {"rename_template": {}}}
            )
        
db = Database(Config.DB_URL, Config.DB_NAME)