import os
import google.generativeai as genai
from google.generativeai import protos # 프로토콜 직접 제어를 위해 추가
import telebot
from datetime import datetime
import pytz

# 환경 변수 로드
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

genai.configure(api_key=GEMINI_API_KEY)

def get_briefing():
    kst = pytz.timezone('Asia/Seoul')
    now_kst = datetime.now(kst)
    current_date = now_kst.strftime('%Y년 %m월 %d일')
    
    # 🌟 [검증된 모델] 1.5-flash가 현재 검색 기능이 가장 안정적입니다.
    model_name = 'gemini-1.5-flash' 
    
    try:
        # 🌟 [에러 원천 차단] 딕셔너리가 아닌 'Tool' 프로토타입을 직접 생성합니다.
        # 이렇게 하면 'Unknown field' 에러를 물리적으로 피할 수 있습니다.
        search_tool = protos.Tool(
            google_search_retrieval=protos.GoogleSearchRetrieval(
                dynamic_retrieval_config=protos.DynamicRetrievalConfig(
                    mode=protos.DynamicRetrievalConfig.Mode.MODE_UNSPECIFIED,
                    dynamic_threshold=0.06
                )
            )
        )

        model = genai.GenerativeModel(
            model_name=model_name,
            tools=[search_tool]
        )

        prompt = f"""
        오늘은 {current_date}입니다. 반드시 '구글 검색'을 실행해서 다음 정보를 알려줘:
        1. 미국 증시(나스닥, S&P500) 마감 결과와 등락 원인
        2. 삼성전자 현재가 및 국내 반도체(HBM/DRAM) 최신 뉴스
        3. 로봇 및 AI 테크 관련 주요 뉴스
        4. 현재 환율 (USD/KRW, AUD/KRW)
        
        [주의] 가상의 시나리오를 쓰지 말고, 오늘 자 실시간 뉴스만 다뤄줘. 출처 링크도 꼭 포함해줘.
        """
        
        response = model.generate_content(prompt)
        return f"✅ {current_date} 실시간 뉴스 브리핑\n\n" + response.text
        
    except Exception as e:
        return f"❌ 최종 디버깅 실패: {str(e)}"

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
