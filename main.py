import os
import requests
import re
import google.generativeai as genai
import telebot
from datetime import datetime
import pytz

# 1. 환경 변수 로드 (GitHub Secrets)
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
NAVER_CLIENT_ID = os.environ.get('NAVER_CLIENT_ID')
NAVER_CLIENT_SECRET = os.environ.get('NAVER_CLIENT_SECRET')

# Gemini 설정
genai.configure(api_key=GEMINI_API_KEY)

def clean_html(text):
    """네이버 뉴스 결과의 HTML 태그를 깔끔하게 제거하는 함수"""
    text = re.sub('<[^<]+>', '', text)
    return text.replace('&quot;', '"').replace('&apos;', "'").replace('&amp;', '&')

def fetch_naver_news(query, display=3):
    """네이버 API를 통해 특정 키워드의 최신 뉴스를 긁어오는 '센서' 역할"""
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {"query": query, "display": display, "sort": "sim"} # sim: 정확도순, date: 최신순
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        items = response.json().get('items', [])
        
        news_data = ""
        for item in items:
            title = clean_html(item['title'])
            desc = clean_html(item['description'])
            link = item['originallink'] if item.get('originallink') else item['link']
            news_data += f"- 제목: {title}\n  내용: {desc}\n  링크: {link}\n\n"
        return news_data
    except Exception as e:
        return f"뉴스 수집 실패 ({query}): {str(e)}\n"

def get_briefing():
    kst = pytz.timezone('Asia/Seoul')
    now_kst = datetime.now(kst)
    current_date = now_kst.strftime('%Y년 %m월 %d일')
    
    # 2. 국내외 핵심 키워드로 뉴스 원문 수집 (Decoupling 1단계)
    raw_news = f"[{current_date} 수집된 최신 원문 데이터]\n\n"
    raw_news += "■ 미국 증시 (나스닥, S&P500)\n" + fetch_naver_news("미국 증시 나스닥 마감")
    raw_news += "■ 국내 주식 (삼성전자 우선주, KODEX, HBM)\n" + fetch_naver_news("삼성전자 우선주 KODEX HBM")
    raw_news += "■ 로봇 및 AI 테크 (ETF)\n" + fetch_naver_news("로봇 AI ETF")
    raw_news += "■ 주요 환율 (USD/KRW, AUD/KRW)\n" + fetch_naver_news("원달러 호주달러 환율")

    # 3. Gemini에게 요약만 지시 (Decoupling 2단계)
    try:
        # Temperature를 0.0으로 설정하여 상상(할루시네이션)을 100% 차단
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            generation_config=genai.types.GenerationConfig(temperature=0.0)
        )

        prompt = f"""
        너는 전문 금융 애널리스트야. 아래 제공된 [수집된 최신 원문 데이터]만을 읽고, 
        보고서 형식으로 가독성 좋게 브리핑을 작성해줘.
        
        [지시사항]
        1. 내가 제공한 데이터 외에 너의 사전 지식이나 상상을 절대 추가하지 마.
        2. 제공된 텍스트에 환율이나 주가 숫자가 있다면 정확히 기재해.
        3. 각 섹션의 끝에는 반드시 제공된 기사의 '링크'를 달아줘.
        4. 내용이 없거나 부족하면 '수집된 관련 뉴스가 없습니다'라고 솔직하게 적어.

        {raw_news}
        """
        
        response = model.generate_content(prompt)
        return f"📊 {current_date} 팩트 기반 시장 브리핑\n\n" + response.text
        
    except Exception as e:
        return f"❌ 브리핑 생성 실패: {str(e)}"

def send_telegram():
    content = get_briefing()
    bot = telebot.TeleBot(TELEGRAM_TOKEN)
    if len(content) > 4000:
        for i in range(0, len(content), 4000):
            bot.send_message(CHAT_ID, content[i:i+4000])
    else:
        bot.send_message(CHAT_ID, content)

if __name__ == "__main__":
    send_telegram()
