import discord
from datetime import datetime, timedelta, timezone
from cetus_cycle import get_previous_night_time


class CetusAlarm:
    """
    用於產生夜靈平野入夜時間表的類別
    """

    def __init__(self):
        """
        初始化 CetusAlarm，包含第一個夜晚時間與循環的間隔
        """
        self._first_night = get_previous_night_time()
        self._night_gap = timedelta(minutes=150)

    def refresh_first_night(self):
        """
        重新更新第一晚的時間

        Returns:
            str: 新的第一晚時間資訊
        """
        self._first_night = get_previous_night_time()
        return f"重新更新第一晚的時間: {self._first_night}"

    def get_embed(self):
        """
        產生並返回完整的 Embed 結果，包含現在的狀態與時間表

        Returns:
            discord.Embed: 包含現在狀態與時間表的 Discord Embed 對象
        """
        # 動態判斷目前是否為夜晚，並設定顏色
        embed_color = 0xf1c40f if self._is_night() else 0x3498db

        # 建立 Embed 並添加資料
        embed = discord.Embed(color=embed_color)
        embed.add_field(name=self._generate_status(), value="近期入夜時間", inline=False)
        embed.add_field(name=self._generate_today_name(), value=self._generate_schedule(today=True), inline=False)
        embed.add_field(name=self._generate_tomorrow_name(), value=self._generate_schedule(today=False), inline=False)
        return embed

    def _is_night(self):
        """
        判斷目前時間是否處於夜晚

        Returns:
            bool: 如果處於夜晚，回傳 True；否則回傳 False
        """
        return (self._next_night() - self._current_time()).total_seconds() // 60 <= 100

    def _generate_status(self):
        """
        產生狀態資訊，作為 Field 0

        Returns:
            str: 頂部的狀態的文字描述
        """
        is_night = self._is_night()  # 直接調用 _is_night 判斷是否為夜晚
        state = "入夜" if is_night else "日出"
        minutes_left = int((self._next_night() - self._current_time()).total_seconds() // 60)
        minutes_left -= 100 if not is_night else 0
        next_night_time = self._next_night().strftime('%H:%M')
        current_time_str = self._current_time().strftime('%H:%M')
        return f"夜靈平野還有 {minutes_left} 分鐘{state}\n現在時間：{current_time_str}\n下個夜晚：{next_night_time}"

    def _generate_today_name(self):
        """
        動態產生今天的 embed_name，作為 Field 1 的 name

        Returns:
            str: 今天的日期 embed_name，格式為「今天 - 月/日」
        """
        today = self._current_time().strftime('%m/%d')
        return f"今天 - {today}"

    def _generate_tomorrow_name(self):
        """
        動態產生明天的 embed_name，作為 Field 2 的 name

        Returns:
            str: 明天的日期 embed_name，格式為「明天 - 月/日」
        """
        tomorrow = (self._current_time() + timedelta(days=1)).strftime('%m/%d')
        return f"明天 - {tomorrow}"

    def _generate_schedule(self, today=True):
        """
        產生今天或明天的入夜時間表

        Args:
            today (bool): 靠 today 值確認目前要產生今天還是明天的時間表，若值為 False 就產生明天的時間表

        Returns:
            str: 入夜時間表，以 ```diff 包覆的多行文字
        """
        start_time = self._current_time().replace(hour=0, minute=0) if today else \
            self._current_time().replace(hour=0, minute=0) + timedelta(days=1)
        end_time = start_time + timedelta(hours=23, minutes=59)
        night_duration = timedelta(minutes=50)

        schedule = ["```diff"]
        next_night = self._next_night(start_time)
        current_time = self._current_time()

        while next_night <= end_time:
            start = next_night.strftime('%H:%M')
            end = (next_night + night_duration).strftime('%H:%M')
            minutes_left = int((next_night - current_time).total_seconds() // 60)

            if minutes_left > 100:
                schedule.append(f"--- {start} ～ {end}")
            elif minutes_left > -50:
                if next_night == self._next_night():
                    schedule.append(f"+ {start} ～ {end} 下一晚")
                else:
                    schedule.append(f"+ {start} ～ {end} 進行中")
            else:
                schedule.append(f"- {start} ～ {end} 已結束")

            next_night += self._night_gap

        schedule.append("```")
        return "\n".join(schedule)

    def _next_night(self, reference_time=None):
        """
        計算下一次夜晚的時間

        Args:
            reference_time (datetime, optional): 參考的時間點如果為 None，則使用現在時間

        Returns:
            datetime: 下一晚的開始時間
        """
        if reference_time is None:
            reference_time = self._current_time()
        gap = reference_time - self._first_night
        return self._first_night + (gap // self._night_gap + 1) * self._night_gap

    @staticmethod
    def _current_time():
        """
        取得目前的時間，時區是（UTC+8）

        Returns:
            datetime: 目前的時區（UTC+8）時間
        """
        return datetime.now(timezone.utc) + timedelta(hours=8)


if __name__ == "__main__":
    ca = CetusAlarm()
    embed = ca.get_embed()
    print("color: ", embed.color)
    for i, field in enumerate(embed.fields):
        print(f"field {i}: \n\nfield_name: \n{field.name}\n\nfield_value: \n{field.value}\n")
