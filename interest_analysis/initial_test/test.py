# test.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
import os
import uvicorn

from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = FastAPI()

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.3,
    openai_api_key=OPENAI_API_KEY,
)

# 더미 데이터: 사용자 채팅 로그
dummy_chat_log = """
💬 민수: 오늘 하루 어땠어? 😊
💬 지윤: 그냥 평범했지 뭐 ㅎㅎ 너는?
💬 민수: 나도 뭐~ 근데 왠지 모르게 너랑 톡하면 하루가 좀 더 특별해지는 느낌? 😏
💬 지윤: 오~ 오늘은 또 왜 이렇게 말이 스윗해? ㅎㅎ
💬 민수: 원래도 스윗했는데 너만 몰랐던 거 아냐? 🤭
💬 지윤: 아, 맞다! 너 저번에 추천해준 카페 갔다 왔어! 분위기 진짜 좋더라~
💬 민수: 오! 진짜? 근데 왜 나랑 안 갔어? 섭섭하네 ㅋㅋ
💬 지윤: ㅋㅋㅋ 다음에 같이 가자! 그럼 됐지? 😆
💬 민수: 오케이, 약속했어! 말 바꾸기 없기!
💬 지윤: 네네~ 근데 너 뭐 먹었어? 저녁 안 챙겨 먹은 거 아니지?
💬 민수: 응~ 근데 너 걱정해 주는 거 기분 좋다 😌
💬 지윤: 당연하지~ 친구잖아! ㅎㅎ
💬 민수: …그치, 친구니까 그렇겠지? (뭔가 아쉽네 ㅋㅋ)
💬 지윤: ㅋㅋㅋㅋ 뭔가? 왜 말 흐려~
💬 민수: 아냐아냐~ 그냥… 네가 나한테 하는 말이 썸 같기도 하고, 친구 같기도 하고 헷갈려서 ㅎㅎ
💬 지윤: 음… 그럼 내가 좀 더 헷갈리게 해줄까? 😉
💬 민수: 뭐야ㅋㅋㅋ 궁금한데?
"""

# Pydantic 모델 정의: 여러 개의 채팅 로그 분석 요청
class ChatLogsRequest(BaseModel):
    chat_logs: List[str]  # 여러 개의 채팅 기록을 리스트 형태로 받음

# LangChain을 활용한 호감도 분석 함수 (여러 개의 채팅 로그 지원)
def interest_analysis(chat_logs: List[str]) -> dict:
    """
    여러 개의 채팅 로그를 LangChain을 사용해 분석하고,
    상대방의 호감도를 '호감 있음' 또는 '호감 없음'으로 평가하며,
    분석 이유를 5줄 이내로 요약하여 반환하는 함수.
    """

    # 여러 개의 채팅 로그를 하나의 문자열로 변환
    chat_history = "\n".join(chat_logs)

    # 시스템 프롬프트 설정
    system_prompt = SystemMessage(
        content="""
    당신은 감정 분석 전문가입니다.
    아래 채팅 로그를 분석하고, 상대방의 호감도를 판단하세요.
    결과는 반드시 '호감 있음' 또는 '호감 없음' 중 하나로 답하세요.
    또한 상대방의 태도를 분석하여, 5줄 이내로 요약하여 이유를 설명하세요.
    
    분석 기준:
    - 상대방이 친밀감을 표현하는지
    - 상대방이 관심을 지속적으로 보이는지
    - 농담이나 유머를 활용하여 관계를 유지하려 하는지
    """
    )

    # 사용자 입력 메시지
    user_prompt = HumanMessage(
        content=f"채팅 로그:\n{chat_history}\n\n분석 결과를 알려주세요."
    )

    # LangChain을 사용한 모델 호출
    response = llm.invoke([system_prompt, user_prompt])

    # 결과 추출
    result_text = response.content.strip()

    # 결과에서 호감도와 분석 이유 분리
    if "호감 있음" in result_text:
        sentiment = "호감 있음"
    elif "호감 없음" in result_text:
        sentiment = "호감 없음"
    else:
        sentiment = "분석 불가"

    explanation = result_text.replace(sentiment, "").strip()  # 호감도를 제외한 분석 이유 추출

    return {"호감도": sentiment, "이유": explanation}

# API 엔드포인트: 여러 개의 채팅 로그 분석 요청
@app.post("/analyze/")
async def analyze_chat_logs(request: ChatLogsRequest):
    """
    사용자가 여러 개의 채팅 로그를 보내면 LangChain을 사용하여 분석 후 결과를 반환하는 API
    """
    chat_logs = request.chat_logs  # 여러 개의 채팅 로그 가져오기
    result = interest_analysis(chat_logs)  # LangChain을 사용해 분석
    return result  # JSON 결과 반환

# FastAPI 애플리케이션 실행
if __name__ == "__main__":
    uvicorn.run(
        "test:app",
        reload=True,
        host="0.0.0.0",
        port=8085
    )
