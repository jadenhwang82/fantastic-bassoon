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

# (앞부분 import 및 함수들은 이전과 동일)

def get_briefing():
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst)
    # 오늘 아침 7시 읽는 시점 기준
    display_date = now.strftime('%Y년 %m월 %d일')
    # 데이터의 기준이 되는 어제 날짜
    target_date = (now - timedelta(days=1)).strftime('%Y년 %m월 %d일')
    
    usd_krw = get_exchange_rate("USDKRW=X")
    aud_krw = get_exchange_rate("AUDKRW=X")
    
    raw_news = f"■ [미국 증시]\n" + fetch_naver_news("미국 증시 나스닥 S&P500 마감", 4)
    raw_news += f"■ [국내 증시]\n" + fetch_naver_news("삼성전자 우선주 KODEX HBM 실적", 4)
    raw_news += f"■ [로봇/AI]\n" + fetch_naver_news("로봇 피지컬AI ETF 신규 상장", 4)

    try:
        # 모델명을 'gemini-1.5-flash'로 설정하되, 
        # 혹시 모를 에러를 대비해 가장 안정적인 식별자를 사용합니다.
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash', # 'models/gemini-1.5-flash' 대신 이 형식을 권장합니다.
            generation_config=genai.types.GenerationConfig(temperature=0.0)
        )
        
        # (이하 생략)

        # 사용자님의 요구사항에 맞춘 정밀 프롬프트
        prompt = f"""
        너는 수석 금융 애널리스트야. 제공된 데이터를 바탕으로 {display_date} 아침에 읽을 전문적인 브리핑을 작성해.
        
        [필수 정보]
        - 보고서 기준일: {target_date} 시장 마감 기준
        - 원/달러 환율: {usd_krw}원
        - 호주달러/원 환율: {aud_krw}원

        [보고서 구조 가이드]
        1. 제목: {display_date} 아침 금융시장 브리핑: (그날의 핵심 키워드를 넣은 멋진 제목)
        2. Ⅰ. 브리핑 요약: 전체 내용을 3~4줄로 통찰력 있게 요약.
        3. Ⅱ. 글로벌 증시 동향: 미국 증시(나스닥, S&P500) 중심 분석 및 뉴스 링크.
        4. Ⅲ. 국내 증시 분석: 코스피/코스닥 흐름, 삼성전자 및 주요 테마 분석 및 뉴스 링크.
        5. Ⅳ. 주요 섹터 포커스: 로봇 및 AI 산업 관련 심층 요약 및 뉴스 링크.
        6. Ⅴ. 환율 시장 업데이트: 제공된 환율 수치를 정확히 명시하고 간단한 코멘트.
        7. Ⅵ. 애널리스트 코멘트 및 전망: 향후 투자 유의점이나 전망 제시.

        [주의사항]
        - 환율은 반드시 내가 제공한 숫자를 사용해. 뉴스 기사 속 숫자가 다르다면 무시해.
        - 링크는 각 섹션 하단에 몰아서 가독성 있게 배치해.
        - 수집된 뉴스 데이터 외의 허구의 숫자를 지어내지 마.

        [수집된 뉴스 데이터]
        {raw_news}
        """
        
        response = model.generate_content(prompt)
        return f"📊 {display_date} Morning Briefing\n(기준: {target_date} 시장 마감 및 밤사이 주요 소식)\n\n" + response.text
        
    except Exception as e:
        return f"❌ 브리핑 생성 실패: {str(e)}"

# (뒷부분 send_telegram 함수는 동일)
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
