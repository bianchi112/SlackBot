from datetime import datetime, timedelta
import time
import threading
from slcak_babplus import run_babplus

import os
from dotenv import load_dotenv
import holidays

# ✅ 현재 디렉터리 기준으로 .env 명시적으로 로드
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)


# ✅ 밥플러스 실행일 계산 함수 (월~금, 공휴일 건너뜀)
def get_next_babplus_day():
    today = datetime.now().date()
    kr_holidays = holidays.KR()
    # 이번 주 월~금 날짜 리스트
    week = [today]
    # 오늘이 월요일이 아니면 이번 주 월요일로 이동
    if today.weekday() != 0:
        week[0] = today - timedelta(days=today.weekday())
    week = [week[0] + timedelta(days=i) for i in range(5)]
    # 월~금 중 공휴일/주말이 아닌 첫 번째 날 찾기
    for d in week:
        if d.weekday() < 5 and d not in kr_holidays:
            return d
    return None  # 이번 주 평일이 모두 공휴일이면 None


# ✅ 슬랙 알람 봇 실행
already_ran_10 = False
already_ran_1105 = False
already_ran_1750 = False
next_babplus_day = get_next_babplus_day()

while True:
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    today = now.date()

    # 매일 자정에 다음 실행일 및 실행 상태 갱신
    if current_time == "00:00:00":
        already_ran_10 = False
        already_ran_1105 = False
        already_ran_1750 = False
        next_babplus_day = get_next_babplus_day()
        print("🌙 자정 - 실행 상태 및 다음 밥플러스 실행일 갱신:", next_babplus_day)

    # 오늘이 밥플러스 실행일이면 10:00:00에 실행
    if today == next_babplus_day and current_time == "10:00:00" and not already_ran_10:
        print("🕙 10:00:00 - run_babplus 실행 (공휴일/요일 체크 반영)")
        run_babplus("🍱 이번주 밥플러스 메뉴입니다!", mode="week")
        already_ran_10 = True

    # 11:00:00에는 평일(월~금)만 실행 (중식)
    if now.weekday() < 5 and current_time == "11:00:00" and not already_ran_1105:
        print("🕚 11:00:00 - run_babplus 실행 (평일, 중식)")
        run_babplus("🍱 오늘의 밥플러스 중식 메뉴입니다!", mode="today", check_holidays=False)
        already_ran_1105 = True

    # 17:50:00에는 월~목만 실행 (석식)
    if now.weekday() < 4 and current_time == "17:50:00" and not already_ran_1750:
        print("🕔 17:50:00 - run_babplus 실행 (월~목, 석식)")
        run_babplus("🍱 오늘의 밥플러스 석식 메뉴입니다!", mode="today", check_holidays=False)
        already_ran_1750 = True

    time.sleep(1)
