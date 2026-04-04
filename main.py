import os
import google.generativeai as genai
import telebot

# 환경변수 로드
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# 1. Gemini 초기화
genai.configure(api_key=GEMINI_API_KEY)

def get_diagnostic_info():
    try:
        # 내 API 키가 접근 가능한 모델 리스트를 가져옵니다.
        model_list = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                model_list.append(m.name)
        
        if not model_list:
            return "❌ 접근 가능한 모델이 하나도 없습니다. API 키 설정을 확인하세요."
        
        # 목록 중 가장 첫 번째 모델로 테스트를 시도합니다.
        test_model_name = model_list[0]
        model = genai.GenerativeModel(test_model_name)
        response = model.generate_content("안녕? 너는 누구니?")
        
        result = f"✅ 성공! 사용 가능한 모델 목록:\n" + "\n".join(model_list)
        result += f"\n\n🤖 테스트 응답 ({test_model_name}): {response.text[:20]}..."
        return result

    except Exception as e:
        return f"❌ 진단 중 오류 발생: {str(e)}"

def send_telegram():
    content = get_diagnostic_info()
    bot = telebot.TeleBot(TELEGRAM_TOKEN)
    bot.send_message(CHAT_ID, content)

if __name__ == "__main__":
    send_telegram()
