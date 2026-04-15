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
        
        # 모델 설정 - 에러 메시지가 요청한 'google_search_retrieval' 객체 형식입니다.
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            tools=[
                {
                    "google_search_retrieval": {
                        "dynamic_retrieval_config": {
                            "mode": "unspecified", # 기본 모드 설정
                            "dynamic_threshold": 0.06 # 검색 필요성 문턱값
                        }
                    }
                }
            ]
        )

        prompt = f"""
        오늘은 {current_date}입니다. '구글 검색'을 통해 다음 실시간 정보를 분석해줘:
        
        1. 미국 증시 마감 상황 (나스닥, S&P500) 및 변동 이유
        2. 삼성전자 주가 및 국내 반도체(HBM/DRAM) 최신 뉴스
        3. 로봇 및 AI 자동화 산업 관련 주요 소식
        4. 환율 (USD/KRW, AUD/KRW) 정보
        
        반드시 오늘({current_date})의 실제 데이터를 바탕으로 작성하고 정보 출처를 포함해줘.
        """
        
        response = model.generate_content(prompt)
        return f"📅 {current_date} 실시간 시장 브리핑\n\n" + response.text
    except Exception as e:
        return f"❌ 브리핑 생성 중 상세 오류: {str(e)}"

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
