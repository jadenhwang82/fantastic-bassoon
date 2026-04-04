import os
import google.generativeai as genai
import telebot

# 환경 변수 설정
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# 1. Gemini 초기화 및 '사용 가능한 모델' 자동 찾기
genai.configure(api_key=GEMINI_API_KEY)

def get_best_model():
    # 사용 가능한 모델 목록 중 'generateContent'를 지원하는 가장 좋은 모델을 찾습니다.
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            # 1.5 flash나 2.0 flash가 포함된 모델을 우선 선택
            if 'flash' in m.name:
                return m.name
    return 'gemini-1.5-flash' # 예외 상황 대비 기본값

def get_market_briefing():
    selected_model_name = get_best_model()
    print(f"선택된 모델: {selected_model_name}") # 로그 확인용
    
    model = genai.GenerativeModel(selected_model_name)
    
    prompt = """
    당신은 전문 금융 분석가입니다. 오늘 아침 8시 기준 다음 정보를 한국어로 요약해줘:
    1. 미국 증시(나스닥, S&P500) 마감 상황과 핵심 원인
    2. 반도체(DRAM 현물가) 및 IT 산업 주요 소식
    3. 한국 증시 개장 전 체크해야 할 뉴스 3가지
    4. 현재 환율(USD/KRW, AUD/KRW)
    
    이모지를 사용해 읽기 편한 보고서 형식으로 작성해줘.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ 내용 생성 중 오류 발생: {str(e)}"

def send_telegram_message(content):
    bot = telebot.TeleBot(TELEGRAM_TOKEN)
    if len(content) > 4000:
        for i in range(0, len(content), 4000):
            bot.send_message(CHAT_ID, content[i:i+4000])
    else:
        bot.send_message(CHAT_ID, content)

if __name__ == "__main__":
    briefing_content = get_market_briefing()
    send_telegram_message(briefing_content)
    print("전송 완료!")
