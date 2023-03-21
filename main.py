import os
import sys

import discord
from discord.ext import commands, tasks
from loguru import logger

from cetus_alarm import CetusAlarm


class EidolonBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        logger.info(f"{self.user} | Ready!")

        alarm_channel_id = os.getenv("ALARM_CHANNEL").split(",")
        alarm_channel_id = set(list(map(int, alarm_channel_id)))

        channels = list()
        for channel in self.get_all_channels():
            if channel.id in alarm_channel_id:
                channels.append(channel)
        self.add_cog(MasterCog(self, channels))


class MasterCog(commands.Cog):
    def __init__(self, bot: EidolonBot, channels):
        self.bot = bot
        self.ca = CetusAlarm()
        for channel in channels:
            ChannelAlarm(channel, self.bot.user, self.ca)
        self.do_task.start()

    def cog_unload(self):
        self.do_task.cancel()

    @tasks.loop(seconds=300)
    async def do_task(self):
        logger.info("Refresh")
        self.ca.refresh()


class ChannelAlarm(commands.Cog):
    def __init__(self, channel: discord.TextChannel, user: discord.ClientUser, ca: CetusAlarm):
        self.channel = channel
        self.user = user
        self.ca = ca
        self.do_task.start()

    def cog_unload(self):
        self.do_task.cancel()

    @tasks.loop(seconds=60)
    async def do_task(self):
        if self.channel.last_message_id is None:
            await self.channel.send(embed = self.ca.full_message())

        msg = await self.channel.fetch_message(self.channel.last_message_id)
        if msg.author == self.user:
            try:
                full_msg = self.ca.full_message()
                if msg.content != full_msg:
                    await msg.edit(embed=full_msg)
                    logger.info(f"Edit {self.channel}")
            except Exception as e:
                logger.error(f"Error: {str(e)}")

    def __repr__(self) -> str:
        return f"ChannelAlarm({self.user}, {self.channel})"


def set_logger():
    log_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSSSSS} | <lvl>{level: ^9}</lvl> | {message}"
    )
    logger.add(sys.stderr, level="INFO", format=log_format)
    logger.add(
        f"logs/bot.log",
        rotation="1 day",
        retention="7 days",
        level="INFO",
        encoding="UTF-8",
        compression="gz",
        format=log_format,
    )

if __name__ == "__main__":
    set_logger()
    token = os.getenv("TOKEN")
    intents = discord.Intents.default()
    EidolonBot(command_prefix="!", intents=intents).run(token)