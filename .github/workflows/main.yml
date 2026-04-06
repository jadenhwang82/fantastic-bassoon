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
    # 404 에러 방지를 위해 가장 표준적인 모델명 사용
    # 만약 'gemini-1.5-flash'가 안되면 'models/gemini-1.5-flash'로 시도
    model_name = 'gemini-1.5-flash'
    
    try:
        model = genai.GenerativeModel(model_name)
        prompt = "금융 분석가로서 오늘 아침 8시 기준, 미국 증시와 한국 증시 주요 뉴스를 요약해줘."
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # 에러 발생 시 사용 가능한 모델 목록을 로그에 출력 (디버깅용)
        print("--- 사용 가능한 모델 목록 ---")
        for m in genai.list_models():
            print(m.name)
        return f"❌ 브리핑 생성 오류: {str(e)}"

def send_telegram():
    content = get_briefing()
    bot = telebot.TeleBot(TELEGRAM_TOKEN)
    bot.send_message(CHAT_ID, content)

if __name__ == "__main__":
    send_telegram()
