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
        
        # 모델 설정 (서버가 요청한 정확한 이름 'google_search' 사용)
        # ⚠️ 딕셔너리가 아닌 리스트 내 문자열 형식이 가장 호환성이 높습니다.
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            tools=['google_search']
        )

        # 사용자님의 투자 관심사를 반영한 정교한 프롬프트
        prompt = f"""
        오늘은 {current_date}입니다. '구글 검색' 기능을 사용하여 다음의 최신 정보를 확인하고 요약해줘:
        
        1. 미국 증시 상황: 나스닥, S&P500 지수와 주요 기술주 변동 원인
        2. 국내 반도체 핵심: 삼성전자(우선주 포함) 주가 현황 및 HBM/DRAM 관련 뉴스
        3. 투자 섹터: KODEX 인덱스 관련 동향 및 로봇/AI 자동화 산업의 새로운 소식
        4. 환율 및 지표: USD/KRW, AUD/KRW 현재 환율과 주요 원자재 가격
        
        주의: 반드시 '실시간 검색 결과'를 바탕으로 작성하고, 정보 하단에 출처 링크를 포함해줘.
        """
        
        response = model.generate_content(prompt)
        return f"📅 {current_date} 실시간 시장 브리핑\n\n" + response.text
    except Exception as e:
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
