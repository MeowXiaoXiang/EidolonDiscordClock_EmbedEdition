import discord
import datetime as dt
from cetus_api import get_time


class AlarmMan:
    def __init__(self):
        self.first_night = get_time()
        self.night_gap = dt.timedelta(minutes=150)

    def refresh(self):
        self.first_night = get_time()
        return f'First night refresh to {self.first_night}'

    def alarm(self):
        left_min = int((self.next_night() - now()).total_seconds() // 60)
        state = '入夜' if left_min <= 100 else '日出'
        left_min -= 100 if left_min > 100 else 0
        nextnight = str(self.next_night())
        msg = f'夜靈平野還有 {left_min} 分鐘{state}\n下個夜晚：{nextnight[11:16]}'

        return msg

    def next_night(self):
        today = dt.datetime.utcnow() + dt.timedelta(hours=+8)
        gap = today - self.first_night
        night_len = dt.timedelta(minutes=50)
        time = self.first_night + (gap // self.night_gap + 1) * self.night_gap

        return time

    def recent_night(self):
        raw = []
        alarm = self.alarm()
        timetoday = dt.datetime.utcnow() + dt.timedelta(hours=+8)
        today = timetoday.replace(hour=0, minute=0)
        gap = today - self.first_night
        night_len = dt.timedelta(minutes=50)
        time = self.first_night + (gap // self.night_gap + 1) * self.night_gap
        tomorrow = today + dt.timedelta(days=1, hours=23, minutes=59)
        pre = time
        embed = discord.Embed(color=0x00b3ff)
        raw.append('近期入夜時間')
        raw.append(f"**\n今天 - {time.strftime('%m/%d')}**\n```")
        while time <= tomorrow:
            t2 = time + night_len
            a = time.strftime('%H:%M')
            b = t2.strftime('%H:%M')
            raw.append(f'{a} ～ {b}')
            pre = time
            time += self.night_gap
            if pre.day != time.day and time <= tomorrow:
                raw.append(f"```**\n明天 - {tomorrow.strftime('%m/%d')}**```")
        raw.append('```')
        result = '\n'.join(raw)
        embed.add_field(name=f"{alarm}\n", value=f'{result}', inline=False)
        embed.set_footer(text=f'現在時間：{UTC_8_NOW()}')
        return embed

    def full_message(self):
        return self.recent_night()


def now():
    return dt.datetime.utcnow() + dt.timedelta(hours=+8)

def UTC_8_NOW():
    f = '%Y-%m-%d %H:%M'
    time_delta = dt.timedelta(hours=+8)
    utc_8_date_str = (dt.datetime.utcnow()+time_delta).strftime(f) #時間戳記UTC+8
    return utc_8_date_str

'''
def UTC_8_CH():
    time_delta = dt.timedelta(hours=+8)
    str_time = (dt.datetime.utcnow()+time_delta).strftime('%H:%M')
    hours, minutes = map(int, str_time.split(':'))
    am_or_pm = ['a.m.', 'p.m.'][hours >= 12]
    return f"{(dt.datetime.utcnow()+time_delta).strftime('%Y-%m-%d')} {(hours-1) % 12+1}:{minutes:02}{am_or_pm}"
'''
if __name__ == "__main__":
    am = AlarmMan()
    print(am.full_message())
    am.refresh()
