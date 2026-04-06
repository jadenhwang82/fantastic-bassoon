import os
import google.generativeai as genai
import telebot

# 환경 변수 로드
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# Gemini 설정
genai.configure(api_key=GEMINI_API_KEY)

def get_briefing():
    # ⚠️ 여기를 반드시 확인하세요! 2.5-flash로 강제 고정합니다.
    model_name = 'models/gemini-2.5-flash'
    
    try:
        model = genai.GenerativeModel(model_name)
        # 테스트용 아주 짧은 프롬프트
        prompt = """
        당신은 전문 경제 분석가입니다. 오늘 아침 8시 기준 다음 정보를 요약해줘:
        1. 미국 증시 마감 상황 (나스닥, S&P500 지수 및 주요 변동 원인)
        2. 반도체 업황 및 DRAM 현물 가격 동향
        3. 한국 증시 개장 전 주요 뉴스 3가지
        4. 주요 환율 정보 (USD/KRW, AUD/KRW 현황)
        
        가독성 좋게 이모지를 사용해 보고서 형식으로 작성해줘.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # 에러 메시지에 어떤 모델명을 썼는지 강제로 출력하게 함
        return f"❌ [시도모델:{model_name}] 생성 오류: {str(e)}"

def send_telegram():
    content = get_briefing()
    bot = telebot.TeleBot(TELEGRAM_TOKEN)
    bot.send_message(CHAT_ID, content)

if __name__ == "__main__":
    send_telegram()
