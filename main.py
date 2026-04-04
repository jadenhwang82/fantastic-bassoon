import os
import google.generativeai as genai
import telebot

# 1. 환경 변수 읽기
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# 2. Gemini 설정 (최신 안정화 버전 v1을 사용하도록 설정됨)
genai.configure(api_key=GEMINI_API_KEY)

def get_briefing():
    # 'models/' 접두사 없이 모델명만 입력하는 것이 현재 가장 표준입니다.
    # 1.5-flash가 안되면 1.5-flash-latest를 시도합니다.
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = """
    금융 분석가로서 오늘 아침 8시 기준 다음을 요약해줘:
    1. 미국 증시 마감 상황
    2. 한국 증시 주요 뉴스 3가지
    3. DRAM 가격 및 환율(USD, AUD) 정보
    가독성 좋게 이모지를 섞어서 보고서 형태로 작성해줘.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # 여기서 발생하는 상세 에러를 로그에 찍어서 나중에 확인할 수 있게 합니다.
        print(f"상세 에러 로그: {e}")
        return f"❌ AI 요약 생성 실패: {str(e)}"

def send_to_telegram():
    content = get_briefing()
    bot = telebot.TeleBot(TELEGRAM_TOKEN)
    bot.send_message(CHAT_ID, content)

if __name__ == "__main__":
    send_to_telegram()
