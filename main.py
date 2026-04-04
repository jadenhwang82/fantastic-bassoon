import os
import google.generativeai as genai
import telebot

# 환경변수 로드
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# Gemini 초기화
genai.configure(api_key=GEMINI_API_KEY)

def get_market_briefing():
    # 최신이면서 가장 안정적인 모델 명칭 사용
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    prompt = "오늘 아침 8시 기준, 미국 증시 종가와 한국 증시 주요 뉴스를 요약해줘."
    
    try:
        # 혹시 모를 안전장치: 응답 생성
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # 오류 발생 시 구체적인 메시지를 텔레그램으로 보냄
        return f"❌ AI 생성 실패: {str(e)}"

def send_telegram():
    content = get_market_briefing()
    bot = telebot.TeleBot(TELEGRAM_TOKEN)
    bot.send_message(CHAT_ID, content)

if __name__ == "__main__":
    send_telegram()
