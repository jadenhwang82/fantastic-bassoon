import os
import google.generativeai as genai
import telebot
from datetime import datetime
import pytz # 시간대 처리를 위해 필요

# 1. 환경 변수 읽기
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# 2. Gemini 설정
genai.configure(api_key=GEMINI_API_KEY)

def get_briefing():
    # 한국 시간대(KST) 및 브리즈번 시간대 설정
    kst = pytz.timezone('Asia/Seoul')
    now_kst = datetime.now(kst)
    current_date = now_kst.strftime('%Y년 %m월 %d일')
    
    # 확실히 사용 가능한 모델명 (지난 로그에서 확인된 2.5-flash)
    model_name = 'models/gemini-2.5-flash'
    model = genai.GenerativeModel(model_name)
    tools=[{'google_search': {}}] 
    )
    
    # 프롬프트에 현재 날짜를 명시적으로 주입
    prompt = f"""
    오늘은 {current_date}입니다. 전문 경제 분석가로서 아래 항목들을 요약해서 보고해줘.
    
    1. 미국 시장 마감: 나스닥, S&P500 등 주요 지수 변동과 핵심 원인 (현재 날짜 기준 최신 정보)
    2. 국내 핵심 관심사: 삼성전자 및 반도체 업황, KODEX 지수 펀드 관련 주요 소식
    3. 미래 산업: 로봇 및 AI 자동화 관련 테크 뉴스
    4. 지표: 현재 환율 (USD/KRW, AUD/KRW) 및 DRAM 현물가 동향
    5. 발견: 투자자가 참고할 만한 오늘만의 새로운 글로벌 매크로 인사이트 한 가지
    
    주의: 반드시 {current_date} 시점의 데이터를 바탕으로 한국어로 작성하고, 읽기 편하게 이모지를 사용해줘.
    """
    
    try:
        response = model.generate_content(prompt)
        return f"📅 {current_date} 시장 브리핑\n\n" + response.text
    except Exception as e:
        return f"❌ 브리핑 생성 오류 ({current_date}): {str(e)}"

def send_to_telegram():
    content = get_briefing()
    bot = telebot.TeleBot(TELEGRAM_TOKEN)
    if len(content) > 4000:
        for i in range(0, len(content), 4000):
            bot.send_message(CHAT_ID, content[i:i+4000])
    else:
        bot.send_message(CHAT_ID, content)

if __name__ == "__main__":
    send_to_telegram()
