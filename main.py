import os
import requests
import re
import google.generativeai as genai
import telebot
from datetime import datetime, timedelta
import pytz
import yfinance as yf # 실시간 금융 데이터 센서 추가

# 1. 환경 변수 로드
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
NAVER_CLIENT_ID = os.environ.get('NAVER_CLIENT_ID')
NAVER_CLIENT_SECRET = os.environ.get('NAVER_CLIENT_SECRET')

genai.configure(api_key=GEMINI_API_KEY)

def get_exchange_rate(ticker):
    """주말/공휴일에도 멈추지 않는 정밀 센서 (최근 5일치 조회)"""
    try:
        data = yf.Ticker(ticker)
        # 1d 대신 5d로 조회하여 가장 최근 거래일 데이터를 가져옵니다.
        hist = data.history(period='5d')
        if not hist.empty:
            price = hist['Close'].iloc[-1]
            return f"{price:,.2f}"
        return "데이터 없음"
    except Exception as e:
        return f"센서 오류: {str(e)}"
        
def clean_html(text):
    text = re.sub('<[^<]+>', '', text)
    return text.replace('&quot;', '"').replace('&apos;', "'").replace('&amp;', '&')

def fetch_naver_news(query, display=3):
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    # 전일 17시 이후 흐름을 보기 위해 'date(최신순)' 정렬 유지
    params = {"query": query, "display": display, "sort": "date"}
    
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
    except:
        return f"뉴스 수집 불가 ({query})\n"

def get_briefing():
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst)
    # 아침 7시 실행 시점 기준으로 '어제' 날짜 계산
    target_date = (now - timedelta(days=1)).strftime('%Y년 %m월 %d일')
    
    # 2. 정밀 수치 데이터 수집 (Hallucination 방지용 하드데이터)
    usd_krw = get_exchange_rate("USDKRW=X")
    aud_krw = get_exchange_rate("AUDKRW=X")
    
    # 3. 뉴스 데이터 수집
    raw_news = f"■ [참고기사] 미국 증시\n" + fetch_naver_news("미국 증시 나스닥 마감")
    raw_news += f"■ [참고기사] 국내 증시\n" + fetch_naver_news("삼성전자 우선주 KODEX HBM")
    raw_news += f"■ [참고기사] 로봇/AI\n" + fetch_naver_news("로봇 AI ETF")

    # 4. Gemini 요약 지시 (정밀 수치 데이터 우선 적용)
    try:
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            generation_config=genai.types.GenerationConfig(temperature=0.0)
        )

        prompt = f"""
        너는 전문 금융 애널리스트야. {target_date} 시장 마감 데이터를 바탕으로 
        다음날 아침에 읽을 브리핑을 작성해.
        
        [절대 준수 수치 데이터]
        - 원/달러 환율: {usd_krw}원
        - 호주달러/원 환율: {aud_krw}원
        
        [지시사항]
        1. 환율 정보는 반드시 위의 [절대 준수 수치 데이터]에 적힌 숫자를 사용해. 
           뉴스 기사에 적힌 옛날 숫자와 다르다면 내 데이터를 우선해.
        2. 미국 증시는 오늘 새벽 마감된 최신 상황을 반영해줘.
        3. 각 섹션마다 수집된 뉴스 링크를 포함하되, 가독성 있게 정리해.
        4. 어조는 현대적이고 신뢰감 있는 전문가 톤으로 작성해.

        [수집된 뉴스 원문]
        {raw_news}
        """
        
        response = model.generate_content(prompt)
        header = f"📊 {now.strftime('%Y-%m-%d')} Morning Briefing\n(기준: {target_date} 시장 마감 및 밤사이 주요 소식)\n\n"
        return header + response.text
        
    except Exception as e:
        return f"❌ 브리핑 생성 실패: {str(e)}"

def send_telegram():
    content = get_briefing()
    bot = telebot.TeleBot(TELEGRAM_TOKEN)
    if len(content) > 4000:
        for i in range(0, len(content), 4000):
            bot.send_message(CHAT_ID, content[i:i+4000])
    else:
        bot.send_message(CHAT_ID, content, parse_mode=None)

if __name__ == "__main__":
    send_telegram()
