import os
import sys

import discord
from discord.ext import tasks
from dotenv import load_dotenv
from loguru import logger
from cetus_alarm import CetusAlarm

class EidolonClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ca = CetusAlarm()
        self.channels = []  # 儲存需要推播的頻道
        self.channel_last_message = {}  # 追蹤每個頻道的最後一條訊息 ID

    async def on_ready(self):
        logger.info(f"{self.user} | Ready！")

        # 收集需要推播的頻道 ID
        alarm_channel_ids = set()
        try:
            alarm_channel_ids = set(map(int, os.getenv("ALARM_CHANNEL", "").split(",")))
        except ValueError:
            logger.critical("環境變數 ALARM_CHANNEL 設定有誤，應該是以逗號分隔的有效頻道 ID")
            sys.exit("請檢查 ALARM_CHANNEL 設定！")

        # 查找符合條件的頻道
        for channel in self.get_all_channels():
            if isinstance(channel, discord.TextChannel) and channel.id in alarm_channel_ids:
                self.channels.append(channel)

        if not self.channels:
            logger.critical("未找到有效的推播頻道，請檢查 ALARM_CHANNEL 是否正確設定並確保機器人有訪問權限！")
            sys.exit("無有效頻道，無法啟動機器人")

        logger.info(f"監控的頻道: {[channel.id for channel in self.channels]}")

        # 啟動後回頭查找之前是否已經發送過訊息
        await self.initialize_last_messages()

        # 啟動定時任務，必須在機器人準備好後啟動
        self.update_channels_task.start()
        self.refresh_first_night_task.start()

    async def initialize_last_messages(self):
        """檢查每個頻道是否已有機器人發送的相關訊息，並更新記錄"""
        for channel in self.channels:
            async for message in channel.history(limit=50):  # 往回檢查最近 50 條訊息
                if message.author == self.user and message.embeds:
                    embed = message.embeds[0]
                    if embed.fields and embed.fields[0].name.startswith("夜靈平野還有"):
                        self.channel_last_message[channel.id] = message.id
                        logger.info(f"已找到頻道 {channel.id} 的最後嵌入訊息，ID: {message.id}")
                        break

    @tasks.loop(seconds=60)
    async def update_channels_task(self):
        """每 60 秒更新頻道的推播訊息"""
        for channel in self.channels:
            try:
                await self.update_channel_message(channel)
            except Exception as e:
                logger.error(f"更新頻道 {channel.id} 時發生錯誤: {str(e)}")

    @tasks.loop(seconds=300)
    async def refresh_first_night_task(self):
        """每 300 秒刷新夜晚起始時間"""
        try:
            self.ca.refresh_first_night()
            logger.info("夜晚起始時間已刷新")
        except Exception as e:
            logger.error(f"刷新夜晚起始時間時發生錯誤: {str(e)}")

    async def update_channel_message(self, channel: discord.TextChannel):
        """更新單個頻道的推播訊息"""
        embed = self.ca.get_embed()

        # 獲取頻道最後一條訊息 ID（若不存在，則初始化為 None）
        last_message_id = self.channel_last_message.get(channel.id, None)

        if last_message_id is None:
            # 若無記錄，直接發送新訊息並保存訊息 ID
            msg = await channel.send(embed=embed)
            self.channel_last_message[channel.id] = msg.id
            logger.info(f"向頻道 {channel.id} 發送了新的嵌入訊息")
            return

        # 嘗試抓取已發送的最後一條訊息
        try:
            last_msg = await channel.fetch_message(last_message_id)
        except discord.NotFound:
            # 若無法找到記錄的訊息，重新發送
            msg = await channel.send(embed=embed)
            self.channel_last_message[channel.id] = msg.id
            logger.warning(f"未找到頻道 {channel.id} 的最後訊息，已重新發送")
            return

        # 如果最後一條訊息是機器人發送的，檢查是否需要更新
        if last_msg.author == self.user:
            if not self._compare_embeds(last_msg.embeds[0], embed):
                await last_msg.edit(embed=embed)
                logger.info(f"更新了頻道 {channel.id} 的嵌入訊息")
        else:
            # 若最後訊息不是機器人發送的，發送新的嵌入訊息
            msg = await channel.send(embed=embed)
            self.channel_last_message[channel.id] = msg.id
            logger.info(f"向頻道 {channel.id} 發送了新的嵌入訊息")

    @staticmethod
    def _compare_embeds(existing_embed: discord.Embed, new_embed: discord.Embed) -> bool:
        """比較兩個 Embed 是否一致"""
        return (
            existing_embed.title == new_embed.title and
            existing_embed.description == new_embed.description and
            existing_embed.fields == new_embed.fields
        )


def set_logger():
    """配置 loguru 的輸出"""
    logger.remove()  # 移除所有預設的 Sink，避免重複輸出

    # 配置終端輸出
    logger.add(
        sys.stdout,
        level="INFO",  # 根據 DEBUG 模式調整
        colorize=True  # 保留彩色輸出
    )

    # 配置檔案輸出
    logger.add(
        './logs/system.log',
        rotation='7 days',  # 每 7 天輪轉日誌
        retention='30 days',  # 保存最近 30 天的日誌
        level="INFO",  # 檔案中僅記錄 INFO 級別及以上的日誌
        encoding='UTF-8',
        compression="gz",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}"
    )

if __name__ == "__main__":
    set_logger()
    load_dotenv()
    # 檢查 TOKEN 是否有效
    token = os.getenv("TOKEN")
    if not token or not isinstance(token, str):
        logger.critical("環境變數 TOKEN 設定錯誤，請確認已設置正確的 Discord Bot Token！")
        sys.exit("未提供有效的 TOKEN，請檢查一下你的環境變數")

    intents = discord.Intents.default()
    client = EidolonClient(intents=intents)
    try:
        client.run(token)
    except discord.LoginFailure as e:
        logger.critical("機器人無法登入，請確認 TOKEN 是否正確！\n" + str(e))
        sys.exit("TOKEN 無效，請檢查並重新啟動機器人")
