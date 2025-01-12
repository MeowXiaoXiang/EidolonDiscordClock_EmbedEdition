from datetime import datetime, timedelta, timezone

TOTAL_CYCLE_DURATION = timedelta(seconds=8998.874) # 完整循環時間
NIGHT_DURATION = timedelta(seconds=3000)           # 夜晚持續時間
BASELINE_START = datetime(2021, 2, 5, 12, 27, 54, tzinfo=timezone.utc)  # 循環基準時間
CYCLES_IN_A_DAY = 10                               # 平原日夜循環數
CYCLE_TOTAL_MINUTES = 150                          # 每個循環的總分鐘數

def get_previous_night_time():
    """
    計算前一天的夜晚開始時間。

    基於基準時間 (BASELINE_START) 和日夜循環邏輯，計算夜靈平原的上一次夜晚開始時間。
    結果以 UTC+8 時區表示，並去除秒與微秒。

    Returns:
        datetime: 上一次夜晚開始時間（UTC+8）。
    """
    # 目前時間（UTC）
    utc_now = datetime.now(timezone.utc)
    elapsed_since_start = utc_now - BASELINE_START

    # 計算當前循環內的剩餘時間
    time_until_cycle_end = TOTAL_CYCLE_DURATION - (elapsed_since_start % TOTAL_CYCLE_DURATION)

    # 判斷是否為夜晚或白天，計算剩餘時間
    if time_until_cycle_end > NIGHT_DURATION:
        time_left_for_state = time_until_cycle_end - NIGHT_DURATION
    else:
        time_left_for_state = time_until_cycle_end

    # 將剩餘時間轉為分鐘，處理夜晚邏輯
    state_minutes = time_left_for_state.seconds // 60
    if time_until_cycle_end <= NIGHT_DURATION:
        state_minutes += 100  # 夜晚邏輯加 100 分鐘

    # 計算前一天的夜晚開始時間
    utc8_now = utc_now + timedelta(hours=8)
    previous_night_start = utc8_now + timedelta(minutes=state_minutes) - timedelta(minutes=CYCLE_TOTAL_MINUTES * CYCLES_IN_A_DAY)

    return previous_night_start.replace(second=0, microsecond=0)


if __name__ == "__main__":
    print(get_previous_night_time())