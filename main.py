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
        prompt = "안녕? 반가워. 오늘 증시 요약해줄 준비 됐니?"
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
