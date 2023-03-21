from datetime import datetime, timedelta

def get_time():
    '''
    取得前一天時間
    '''
    loop_time = timedelta(seconds=8998.874)
    night_time = timedelta(seconds=3000)
    start_time = datetime(2021, 2, 5, 12, 27, 54)
    current_time = datetime.utcnow()
    time_elapsed = current_time - start_time
    loop_left = loop_time - time_elapsed % loop_time

    time_left = (loop_left - night_time) if loop_left > night_time else loop_left
    hours, remaining_seconds = divmod(time_left.seconds, 3600)
    minutes, seconds = divmod(remaining_seconds, 60)
    # print("夜靈平野還有{}時{}分{}秒{}".format(hours, minutes, seconds, "入夜" if loop_left > night_time else "日出"))

    minutes = hours * 60 + minutes
    if loop_left < night_time:
        minutes += 100

    # Calculate Last Day Night
    time_left = timedelta(minutes=minutes, seconds=seconds)
    current_time = datetime.utcnow() + timedelta(hours=+8)
    last_day_night = current_time + time_left - timedelta(minutes=150 * 10)
    last_day_night = last_day_night.replace(second=0, microsecond=0)

    return last_day_night

if __name__ == "__main__":
    print(get_time())