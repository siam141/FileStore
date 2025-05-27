import os
import sys
import asyncio
import logging
from aiohttp import web
from datetime import datetime
from pyrogram import Client
from pyrogram.enums import ParseMode
import pyromod.listen

from config import (
    API_ID,
    API_HASH,
    BOT_TOKEN,
    CHANNEL_ID,
    OWNER_ID,
    TG_BOT_WORKERS,
    PORT,
    FORCE_SUB_CHANNEL1,
    FORCE_SUB_CHANNEL2,
    FORCE_SUB_CHANNEL3,
    FORCE_SUB_CHANNEL4,
)
from plugins import web_server

# Logger Setup
logging.basicConfig(
    format="%(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
)

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS
        )
        self.LOGGER = logging.getLogger

    async def start(self):
        await super().start()
        self.uptime = datetime.now()
        bot_user = await self.get_me()
        self.username = bot_user.username

        # Handle Force Sub Channels
        for idx, ch in enumerate([FORCE_SUB_CHANNEL1, FORCE_SUB_CHANNEL2, FORCE_SUB_CHANNEL3, FORCE_SUB_CHANNEL4], start=1):
            if ch:
                try:
                    chat = await self.get_chat(ch)
                    link = chat.invite_link or await self.export_chat_invite_link(ch)
                    setattr(self, f"invitelink{idx}", link)
                except Exception as e:
                    self.LOGGER(__name__).warning(e)
                    self.LOGGER(__name__).error(f"Check FORCE_SUB_CHANNEL{idx}. Make sure bot is admin with invite link rights.")
                    sys.exit()

        # Validate DB Channel
        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            test_msg = await self.send_message(db_channel.id, "Bot started test message.")
            await test_msg.delete()
            self.db_channel = db_channel
        except Exception as e:
            self.LOGGER(__name__).warning(e)
            self.LOGGER(__name__).error(f"Check CHANNEL_ID ({CHANNEL_ID}) and bot's admin permissions.")
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)

        # Start Web Server
        app = web.AppRunner(await web_server())
        await app.setup()
        await web.TCPSite(app, "0.0.0.0", PORT).start()

        self.LOGGER(__name__).info("Bot is running!")
        self.LOGGER(__name__).info(f"https://t.me/{self.username}")
        self.LOGGER(__name__).info("Developed by @your_bot_link")

        try:
            await self.send_message(OWNER_ID, text="<b><blockquote>- Bot Restarted</blockquote></b>")
        except:
            pass

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")

    def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.start())
        self.LOGGER(__name__).info("Bot is now running. Use CTRL+C to stop.")
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            self.LOGGER(__name__).info("Shutting down...")
        finally:
            loop.run_until_complete(self.stop())