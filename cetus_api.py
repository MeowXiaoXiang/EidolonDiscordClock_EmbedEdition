import re
import json
import requests
import datetime as dt

def get_time_string():
    url = 'https://api.warframestat.us/pc/cetusCycle'
    r = json.loads(requests.get(url).content)

    # Match Time Format
    m = re.search(r'(\d)h (\d+)m (\d+)s', r['timeLeft'])
    hh, mm, ss = map(int, m.groups())
    mm = hh * 60 + mm

    # Match State
    state = '入夜' if r['isDay'] else '日出'

    # Calculate Next Night
    d = dt.timedelta(minutes=mm, seconds=ss)
    d = dt.datetime.utcnow() + dt.timedelta(hours=+8) + d
    d = d.replace(second=0, microsecond=0)
    d = d.strftime('%Y-%m-%d %H:%M:%S')

    return f'希圖斯還有 {mm} 分鐘{state}，下個夜晚：{d}'

def get_time():
    url = 'https://api.warframestat.us/pc/cetusCycle'
    r = json.loads(requests.get(url).content)

    # Match Time Format
    m = re.search(r'((\d)h )?((\d+)m )?(\d+)s', r['timeLeft'])
    _, hh, _, mm, ss = m.groups()
    to_int = lambda x: 0 if x is None else int(x)
    hh, mm, ss = map(to_int, (hh, mm, ss))
    mm = hh * 60 + mm
    if not r['isDay']: mm += 100

    # Calculate Last Day Night
    d = dt.timedelta(minutes=mm, seconds=ss)
    d = dt.datetime.utcnow() + dt.timedelta(hours=+8) + d - dt.timedelta(minutes=150 * 10)
    d = d.replace(second=0, microsecond=0)

    return d

if __name__ == "__main__":
    print(get_time())
