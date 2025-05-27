from aiohttp import web
from plugins import web_server
import asyncio
import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
import sys
from datetime import datetime
from config import *


class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()

        for i, channel in enumerate(
            [FORCE_SUB_CHANNEL1, FORCE_SUB_CHANNEL2, FORCE_SUB_CHANNEL3, FORCE_SUB_CHANNEL4],
            start=1
        ):
            if channel:
                try:
                    link = (await self.get_chat(channel)).invite_link
                    if not link:
                        await self.export_chat_invite_link(channel)
                        link = (await self.get_chat(channel)).invite_link
                    setattr(self, f"invitelink{i}", link)
                except Exception as e:
                    self.LOGGER(__name__).warning(e)
                    self.LOGGER(__name__).warning("Bot can't export invite link from Force Sub Channel!")
                    self.LOGGER(__name__).warning(
                        f"Please check FORCE_SUB_CHANNEL{i} and ensure the bot is admin with invite permissions. Current value: {channel}"
                    )
                    self.LOGGER(__name__).info("Bot Stopped. https://t.me/your_bot_link for support")
                    sys.exit()

        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            test = await self.send_message(chat_id=db_channel.id, text="Test Message")
            await test.delete()
        except Exception as e:
            self.LOGGER(__name__).warning(e)
            self.LOGGER(__name__).warning(f"Make sure bot is admin in DB channel and check CHANNEL_ID. Current value: {CHANNEL_ID}")
            self.LOGGER(__name__).info("Bot Stopped. Join https://t.me/your_bot_link for support")
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)
        self.username = usr_bot_me.username

        self.LOGGER(__name__).info(r"""
  ___ ___  ___  ___ ___ _    _____  _____  ___ _____ ___ 
 / __/ _ \\|   \\| __| __| |  |_ _\\ \\/ / _ )/ _ \\_   _/ __|
| (_| (_) | |) | _|| _|| |__ | | >  <| _ \\ (_) || | \__ \\
 \___\___/|___/|___|_| |____|___/_/\\_\\___/\\___/ |_| |___/
        """)

        self.LOGGER(__name__).info("Bot Running..! Made by @your_bot_link")

        # Start Web Server
        app = web.AppRunner(await web_server())
        await app.setup()
        await web.TCPSite(app, "0.0.0.0", PORT).start()

        try:
            await self.send_message(OWNER_ID, text="<b><blockquote>- Bᴏᴛ Rᴇsᴛᴀʀᴛᴇᴅ by @your_bot_link</blockquote></b>")
        except:
            pass

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")

    def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.start())
        self.LOGGER(__name__).info("Bot is now running. Thanks to @your_bot_link")
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            self.LOGGER(__name__).info("Shutting down...")
        finally:
            loop.run_until_complete(self.stop())