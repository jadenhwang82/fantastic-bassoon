import os
import google.generativeai as genai
import telebot

# 1. 환경 변수 읽기
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# 2. Gemini 설정
genai.configure(api_key=GEMINI_API_KEY)

def get_briefing():
    # 로그에서 확인된 '확실히 사용 가능한' 모델 명칭을 사용합니다.
    # 'models/'를 붙여서 명확하게 지정합니다.
    model_name = 'models/gemini-2.5-flash'
    
    try:
        model = genai.GenerativeModel(model_name)
        
        # 사용자님께 꼭 필요한 정보를 담은 맞춤형 프롬프트
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
        return f"❌ AI 생성 중 상세 오류 발생: {str(e)}"

def send_to_telegram():
    content = get_briefing()
    bot = telebot.TeleBot(TELEGRAM_TOKEN)
    
    # 메시지가 너무 길면 나눠서 전송
    if len(content) > 4000:
        for i in range(0, len(content), 4000):
            bot.send_message(CHAT_ID, content[i:i+4000])
    else:
        bot.send_message(CHAT_ID, content)

if __name__ == "__main__":
    send_to_telegram()
