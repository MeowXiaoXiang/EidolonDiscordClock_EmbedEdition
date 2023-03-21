import discord
import datetime as dt
from cetus_cycle import get_time


class CetusAlarm:
    def __init__(self):
        self.first_night = get_time()
        self.night_gap = dt.timedelta(minutes=150)

    def refresh(self):
        self.first_night = get_time()
        return F'重新更新第一晚的時間 {self.first_night}'

    def get_status(self):
        left_min = int((self.next_night() - self.now()).total_seconds() // 60)
        state = '入夜' if left_min <= 100 else '日出'
        left_min -= 100 if left_min > 100 else 0
        nextnight = str(self.next_night())
        time_delta = dt.timedelta(hours=+8)
        utc_8_date_str = (dt.datetime.utcnow()+time_delta).strftime('%H:%M') #時間戳記UTC+8
        msg = F'夜靈平野還有 {left_min} 分鐘{state}\n現在時間：{utc_8_date_str}\n下個夜晚：{nextnight[11:16]}'
        return msg

    def next_night(self, today = None):
        if not today:
            today = dt.datetime.utcnow() + dt.timedelta(hours=+8)
        gap = today - self.first_night
        time = self.first_night + (gap // self.night_gap + 1) * self.night_gap
        return time

    def get_schedule(self):
        raw = []
        alarm = self.get_status()
        timetoday = self.now()
        today = timetoday.replace(hour=0, minute=0)
        night_len = dt.timedelta(minutes=50)
        time = self.next_night(today)
        tomorrow = today + dt.timedelta(days=1, hours=23, minutes=59)
        
        pre = time
        left_min = int((time - self.now()).total_seconds() // 60)
        embed = discord.Embed(color=0xf1c40f if "入夜" in alarm else 0x3498db)
        raw.append('近期入夜時間')
        raw.append(f"**\n今天 - {time.strftime('%m/%d')}**\n```diff")
        while time <= tomorrow:
            t2 = time + night_len
            a = time.strftime('%H:%M')
            b = t2.strftime('%H:%M')
            left_min = int((time - self.now()).total_seconds() // 60)
            if left_min > 100:
                raw.append(F"--- {a} ～ {b}")
            elif left_min > -50:
                # 入夜時顯示進行中
                if time == self.next_night():  # 如果當前時間等於下個夜晚的時間
                    raw.append(F"+ {a} ～ {b} 下一晚")  # 使用+號來表示下一晚的時間
                else:
                    raw.append(F"+ {a} ～ {b} 進行中")  # 不使用+號來表示進行中的時間
            else:
                raw.append(F"- {a} ～ {b} 已結束")
            pre = time
            time += self.night_gap
            if pre.day != time.day and time <= tomorrow:
                raw.append(
                    F"```**\n明天 - {tomorrow.strftime('%m/%d')}**```diff")
        raw.append('```')
        result = '\n'.join(raw)
        # print(result)
        embed.add_field(name=f"{alarm}\n", value=f'{result}', inline=False)
        return embed

    def full_message(self):
        return self.get_schedule()

    def now(self):
        return dt.datetime.utcnow() + dt.timedelta(hours=+8)

if __name__ == "__main__":
    ca = CetusAlarm()
    print(ca.get_status())
    print(ca.full_message())
    ca.refresh()