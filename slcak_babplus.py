def run_babplus(message_text=None, mode="today", check_holidays=True):
    import os
    import time
    from datetime import datetime
    import holidays
    from bs4 import BeautifulSoup
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
    from dotenv import load_dotenv

    # ✅ 주말 및 공휴일 검사
    if check_holidays:
        kr_holidays = holidays.KR()
        today_date = datetime.now()

        if today_date.weekday() >= 5 or today_date in kr_holidays:
            print("🚫 주말 또는 공휴일 - 실행 안함")
            return

    # ✅ 슬랙 설정
    load_dotenv()
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    chrome_path = os.getenv("CHROMEDRIVER_PATH")
    client = WebClient(token=slack_token)

    # ✅ Selenium 설정
    service = Service(chrome_path)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=service, options=options)

    url = "https://pf.kakao.com/_DRCIn/posts"
    driver.get(url)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    image_url = None
    if mode == "week":
        # ✅ '주간메뉴'가 포함된 tit_card를 찾아 해당 카드의 wrap_fit_thumb 이미지 추출
        cards = soup.select("div.area_card")
        for card in cards:
            tit = card.select_one("strong.tit_card")
            if tit and "주간메뉴" in tit.get_text():
                thumb = card.select_one("div.wrap_fit_thumb")
                if thumb and "style" in thumb.attrs:
                    try:
                        style = thumb["style"]
                        image_url = style.split('url("')[1].split('")')[0]
                        print("✅ 주간메뉴 이미지 URL:", image_url)
                        break
                    except Exception as e:
                        print("❌ 주간메뉴 이미지 파싱 실패:", e)
        if not image_url:
            print("❌ '주간메뉴' 카드 이미지 없음")
    else:
        # ✅ 그냥 첫 wrap_fit_thumb 이미지
        first_thumb = soup.select_one("div.wrap_fit_thumb")
        if first_thumb and "style" in first_thumb.attrs:
            try:
                style = first_thumb["style"]
                image_url = style.split('url("')[1].split('")')[0]
                print("✅ 오늘의 이미지 URL:", image_url)
            except Exception as e:
                print("❌ 오늘의 이미지 파싱 실패:", e)
        else:
            print("❌ wrap_fit_thumb 요소 없음")

    # ✅ 슬랙 전송
    if image_url:
        try:
            if not message_text:
                message_text = f"🍱 오늘의 밥플러스 메뉴입니다:\n{image_url}"
            else:
                message_text = f"{message_text}\n{image_url}"
            client.chat_postMessage(
                channel="밥플러스",
                text=message_text
            )
            print("✅ 슬랙 전송 완료")
        except SlackApiError as e:
            print("❌ 슬랙 오류:", e.response['error'])
    else:
        print("❌ 이미지 추출 실패")
