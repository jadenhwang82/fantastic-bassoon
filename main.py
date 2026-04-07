import os
import google.generativeai as genai
import telebot
from datetime import datetime
import pytz

# 환경 변수 로드
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# Gemini 설정
genai.configure(api_key=GEMINI_API_KEY)

def get_briefing():
    kst = pytz.timezone('Asia/Seoul')
    now_kst = datetime.now(kst)
    current_date = now_kst.strftime('%Y년 %m월 %d일')
    
    model_name = 'models/gemini-2.5-flash'
    
    # 🌟 핵심 수정: google_search 도구를 모델에 장착합니다.
    model = genai.GenerativeModel(
        model_name=model_name,
        tools=[{'google_search': {}}] 
    )
    
    # 프롬프트: '검색'을 강조하고 출처 링크를 포함하라고 지시합니다.
    prompt = f"""
    오늘은 {current_date}입니다. 반드시 '구글 검색' 기능을 사용하여 
    실제 {current_date} 및 직전 영업일의 실시간 시장 데이터를 확인하고 아래 내용을 요약해줘.
    
    1. 미국 증시 마감 상황: 나스닥, S&P500 등 주요 지수와 하락/상승의 실제 이유
    2. 국내 반도체: 삼성전자(현재가 포함) 및 HBM/DRAM 업황 최신 뉴스
    3. 미래 산업: 로봇 및 AI 자동화 관련 실제 보도된 테크 뉴스
    4. 환율: USD/KRW, AUD/KRW 현재 환율
    
    [주의] 
    - 2024년이나 2025년의 과거 데이터를 절대 사용하지 마. 
    - 반드시 오늘 뉴스만 다루고, 가능하다면 정보의 출처(URL)를 짧게 포함해줘.
    """
    
    try:
        # 검색 도구가 포함된 모델로 콘텐츠 생성
        response = model.generate_content(prompt)
        return f"📅 {current_date} 실시간 시장 브리핑\n\n" + response.text
    except Exception as e:
        return f"❌ 브리핑 생성 오류: {str(e)}"

def send_telegram():
    content = get_briefing()
    bot = telebot.TeleBot(TELEGRAM_TOKEN)
    
    # 메시지 길이 제한 처리
    if len(content) > 4000:
        for i in range(0, len(content), 4000):
            bot.send_message(CHAT_ID, content[i:i+4000])
    else:
        bot.send_message(CHAT_ID, content)

if __name__ == "__main__":
    send_telegram()
