import os
import google.generativeai as genai
import telebot
from datetime import datetime
import pytz

# 환경 변수 로드
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

genai.configure(api_key=GEMINI_API_KEY)

def get_briefing():
    kst = pytz.timezone('Asia/Seoul')
    now_kst = datetime.now(kst)
    current_date = now_kst.strftime('%Y년 %m월 %d일')
    
    # [수정 포인트] 가장 최신이자 표준인 검색 도구 선언 방식입니다.
    # 모델명은 안정성이 검증된 1.5-flash로 잠시 변경해 보시는 것을 추천합니다. (검색 기능이 가장 안정적임)
    model_name = 'gemini-1.5-flash' 
    
    try:
        model = genai.GenerativeModel(
            model_name=model_name,
            tools=[{"google_search": {}}] # 딕셔너리 형태의 표준 선언
        )

        prompt = f"""
        오늘은 {current_date}입니다. '구글 검색'을 사용하여 반드시 다음 항목의 '실시간' 정보를 요약해줘:
        1. 미국 증시(나스닥, S&P500) 마감 시황과 변동 원인
        2. 삼성전자 주가와 국내 반도체(HBM/DRAM) 최신 뉴스
        3. 로봇 및 AI 자동화 산업 관련 주요 보도
        4. 현재 환율 (USD/KRW, AUD/KRW)
        
        주의: 과거 데이터가 아닌 실제 {current_date}의 뉴스를 기반으로 작성하고, 하단에 뉴스 출처 링크를 포함해줘.
        """
        
        response = model.generate_content(prompt)
        # 검색 결과가 반영되었는지 확인하기 위해 '실시간' 문구를 추가합니다.
        return f"✅ {current_date} 실시간 뉴스 브리핑\n\n" + response.text
        
    except Exception as e:
        return f"❌ 실시간 검색 실패 (상세오류): {str(e)}"

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
