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
    kst = pytz.timezone('Asia/Seoul')
    now_kst = datetime.now(kst)
    current_date = now_kst.strftime('%Y년 %m월 %d일')
    
    # [전략] 구글 서버의 변덕에 대비해 여러 가지 설정을 순차적으로 시도합니다.
    tools_options = [
        ['google_search'], # 최근 통합된 명칭
        [{'google_search_retrieval': {'dynamic_retrieval_config': {'mode': 'unspecified', 'dynamic_threshold': 0.06}}}] # 이전 명칭
    ]
    
    last_error = ""
    for tool in tools_options:
        try:
            model = genai.GenerativeModel(model_name='gemini-2.5-flash', tools=tool)
            prompt = f"오늘은 {current_date}입니다. 반드시 구글 검색으로 {current_date}의 실시간 한국/미국 증시와 환율 정보를 요약해줘."
            response = model.generate_content(prompt)
            return f"📅 {current_date} 시장 브리핑 (실시간)\n\n" + response.text
        except Exception as e:
            last_error = str(e)
            continue # 실패하면 다음 이름으로 재시도

    # 모든 검색 도구가 실패할 경우: 검색 없이 지식 기반으로라도 답변 (최후의 보루)
    try:
        model = genai.GenerativeModel(model_name='gemini-2.5-flash')
        prompt = f"오늘은 {current_date}입니다. 현재 시점의 시장 동향을 아는 대로 알려줘. (검색 기능 일시 오류)"
        response = model.generate_content(prompt)
        return f"⚠️ {current_date} 브리핑 (검색 오류 포함)\n\n" + response.text + f"\n\n(참고: {last_error})"
    except Exception as e:
        return f"❌ 최종 생성 실패: {str(e)}"

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
