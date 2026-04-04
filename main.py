import os
import google.generativeai as genai
import telebot

# 1. 환경 변수에서 비밀 키 가져오기 (GitHub Secrets에 등록한 값들)
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# 2. Gemini AI 설정
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

def get_market_briefing():
    # Gemini에게 전달할 명령문 (프롬프트)
    # 2026년 실시간 정보를 반영하도록 지시합니다.
    prompt = """
    당신은 전문 금융 분석가입니다. 오늘 아침 8시 기준 다음 정보를 한국어로 요약해줘:
    1. 미국 증시(나스닥, S&P500) 마감 지수와 주요 하락/상승 원인
    2. 반도체 업황(DRAM 현물가 동향) 및 관련 주요 소식
    3. 한국 증시 개장 전 체크해야 할 핵심 뉴스 3가지
    4. 현재 환율(USD/KRW, AUD/KRW) 정보
    
    친절하고 가독성 좋게(이모지 활용) 보고서 형식으로 작성해줘.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ 브리핑 생성 중 오류 발생: {str(e)}"

def send_telegram_message(content):
    bot = telebot.TeleBot(TELEGRAM_TOKEN)
    # 긴 메시지의 경우 잘릴 수 있어 4000자 단위로 끊어 보냅니다.
    if len(content) > 4000:
        for i in range(0, len(content), 4000):
            bot.send_message(CHAT_ID, content[i:i+4000])
    else:
        bot.send_message(CHAT_ID, content)

# 실행부
if __name__ == "__main__":
    print("브리핑 생성 중...")
    briefing_content = get_market_briefing()
    print("텔레그램 전송 중...")
    send_telegram_message(briefing_content)
    print("완료!")
