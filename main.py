import os
import google.generativeai as genai
import telebot
from datetime import datetime
import pytz

# 1. 환경 변수 로드
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# 2. Gemini 설정
genai.configure(api_key=GEMINI_API_KEY)

def get_briefing():
    try:
        # 시간대 설정
        kst = pytz.timezone('Asia/Seoul')
        now_kst = datetime.now(kst)
        current_date = now_kst.strftime('%Y년 %m월 %d일')
        
        # 모델 설정 (정확한 툴 명칭: google_search_retrieval)
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            tools=[{'google_search_retrieval': {}}]
        )

        prompt = f"""
        오늘은 {current_date}입니다. '구글 검색' 기능을 사용하여 다음 정보를 반드시 '실시간'으로 확인하고 요약해줘:
        
        1. 미국 증시(나스닥, S&P500) 마감 상황과 주요 변동 원인
        2. 삼성전자 주가 현황 및 국내 반도체(HBM 등) 최신 뉴스
        3. 로봇 및 AI 테크 관련 주요 소식
        4. 현재 환율 (USD/KRW, AUD/KRW)
        
        주의: 반드시 {current_date}의 실제 최신 정보를 반영하고, 가능한 경우 정보의 출처 링크를 포함해줘.
        """
        
        response = model.generate_content(prompt)
        return f"📅 {current_date} 실시간 시장 브리핑\n\n" + response.text
    except Exception as e:
        # 에러 발생 시 상세 내용을 텔레그램으로 보냄
        return f"❌ 브리핑 생성 중 오류 발생: {str(e)}"

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
