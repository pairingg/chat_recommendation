from fastapi import FastAPI  # 웹 프레임워크
import uvicorn  # FastAPI 앱 실행 위함

from pydantic import BaseModel  # 데이터 유효성 검증
from typing import List  # 사용할 타입 힌드: 리스트

from dotenv import load_dotenv  # .env 파일 접근해 환경 변수 로드
import os  # OS와 상호작용
import yaml  # YAML 읽어오기 위함

# OpenAI 관련 라이브러리
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

# 환경 변수 로드
load_dotenv()  # .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# FastAPI 앱 인스턴스 생성
app = FastAPI()

# LangChain으로 메서드로 OpenAI 모델 초기화
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.3,
    openai_api_key=OPENAI_API_KEY,
)

# YAML 파일로 작성한 프롬프트 설정 로드
def load_prompts():
    """
    interest_analysis 폴더 내의 prompt_config.yaml 파일에서
    프롬프트 설정을 읽어와 딕셔너리 형태로 반환하는 함수.
    """
    # 현재 파일과 같은 디렉터리(interest_analysis/application/) 내에 있으므로 경로를 수정함.
    with open("prompt_config.yaml", "r", encoding="utf-8") as file:
        prompt_data = yaml.safe_load(file)
    return prompt_data["prompts"]  # 작성한 System & User Prompt

# YAML 파일에 있는 더미 채팅 로그 데이터 로드 (테스트 시 사용)
def load_dummy_chat_logs():
    """
    interest_analysis 폴더 내의 dummy_chat_logs.yaml 파일에서
    더미 채팅 로그 데이터 읽어와 딕셔너리 형태로 반환하는 함수.
    """
    # 현재 파일과 같은 디렉터리(interest_analysis/application/) 내에 있으므로 경로를 수정함.
    with open("dummy_chat_logs.yaml", "r", encoding="utf-8") as file:
        dummy_data = yaml.safe_load(file)
    return dummy_data["dummy_chat_logs"]  # 더미 채팅 로그 데이터 반환

# 개별 채팅 메시지 표현: 모델에게 보다 세밀한 정보를 제공해 분석의 정밀도 높이기 위함
class ChatMessage(BaseModel):
    senderId: str  # 메시지를 보낸 사용자 ID (ex: "user1", "user2")
    message: str  # 메시지 내용

# 구조화된 데이터로 채팅 로그 요청
class ChatroomLogsRequest(BaseModel):
    chatroomId: str  # 채팅방 ID
    my_userId: str  # 버튼 누른 사용자 ID (본인)
    messages: List[ChatMessage]  # 채팅방의 메시지 리스트

# 채팅 로그 분석을 통한 호감도 평가
def interest_analysis_model_function(data: ChatroomLogsRequest) -> dict:
    """
    DB에서 가져와 구조화한 채팅 로그 데이터를 사용하여,
    상대방의 호감도 평가 및 이유 분석

    - 버튼을 누른 사용자의 아이디(data.my_userId)를 통해 내 메시지와 상대방 메시지를 구분
    - 각 메시지는 ChatMessage 모델로 발화자 구분 가능
    """

    # 발화자와 대화 순서에 따라 전체 대화를 저장할 리스트
    chat_history = []

    # 모든 메시지를 순회하며 발화자에 따라 구분하여 chat_history에 추가합니다.
    for msg in data.messages:
        if msg.senderId == data.my_userId:  # 내가 보낸 메시자
            chat_history.append(f"나 : {msg.message}")
        else:  # 상대방이 보낸 메시지
            chat_history.append(f"상대방 : {msg.message}")

    # chat_history 리스트의 메시지를 줄바꿈 문자로 결합하여 하나의 문자열로 만들기
    combined_chat_history = "\n".join(chat_history)

    # 프롬프트 설정 불러오기
    prompts = load_prompts()

    system_prompt_text = prompts["system_prompt"]
    system_prompt = SystemMessage(content=system_prompt_text)

    user_prompt_text = prompts["user_prompt"].format(
        chat_history=combined_chat_history
    )  # user_prompt의 {chat_history} 자리에 전체 대화 저장 리스트 삽입
    user_prompt = HumanMessage(content=user_prompt_text)

    # 모델 호출해 프롬프트 전달해 응답받기
    response = llm.invoke([system_prompt, user_prompt])
    # 응답 텍스트 추출 및 공백 제거
    result_text = response.content.strip()

    # 응답 텍스트에서 평가 부분("호감 있음" or "호감 없음") 찾아 호감도 결정
    if "호감 있음" in result_text:
        sentiment = "호감 있음"
    elif "호감 없음" in result_text:
        sentiment = "호감 없음"
    else:
        sentiment = "분석 불가"
    # 응답 텍스트에서 호감도 평가 부분 제거 및 분석 이유 추출
    explanation = result_text.replace(sentiment, "").strip()

    # 최종 분석 결과를 딕셔너리 형태로 반환
    return {"호감도": sentiment, "이유": explanation}

# 채팅 로그 데이터를 받아 분석 결과 반환하는 API 엔드포인트
@app.post("/interest_analysis/")
async def interest_analysis_endpoint(request: ChatroomLogsRequest):
    """
    DB에서 가져온 구조화한 채팅 로그 데이터를 받아
    상대방의 호감도 평가와 이유 결과를 반환
    """
    # 더미 채팅 로그 데이터로 테스트 시 주석 해제 
    # dummy_logs = load_dummy_chat_logs()
    # result = interest_analysis_model_function(dummy_logs)

    result = interest_analysis_model_function(request)
    return result


# FastAPI 애플리케이션 실행 (Uvicorn 사용)
if __name__ == "__main__":
    uvicorn.run(
        "initial_application:app",  # 파일 이름이 initial_application.py라 가정
        reload=True,  # 코드 변경 시 자동 재시작 (개발 모드)
        host="0.0.0.0",  # 모든 네트워크 인터페이스에서 접근 가능하도록 설정합니다.
        port=8085,   # 포트 8085에서 서버 실행
    )
