# api.py

from fastapi import FastAPI
import uvicorn
from module.schemas import ChatroomLogsRequest, ChatroomRequest
from module.inference import interest_analysis_model_function
from module.db_getter import load_chat_logs_from_db
from module.dummy import load_dummy_chat_logs

app = FastAPI()


@app.post("/interest_analysis/")
async def interest_analysis(request: ChatroomRequest):
    """
    DB에 저장된 채팅 로그를 조회하여 호감도 평가 수행 API 엔드포인트 정의
    매개변수: ChatroomRequest 객체, 반환: 분석 결과 딕셔너리 반환
    """

    chat_logs_request = load_chat_logs_from_db(request.chatroomId, request.my_userId)
    result = interest_analysis_model_function(chat_logs_request)

    return result

@app.post("/interest_analysis/test")
async def interest_analysis_dummy(dialogue_key: str, my_userId: str):
    """
    더미 데이터를 활용하여 호감도 평가 수행 API 엔드포인트 정의
    매개변수: dialogue_key, my_userId, 반환: 분석 결과 딕셔너리 반환
    """

    chat_logs_request = load_dummy_chat_logs(dialogue_key, my_userId)
    result = interest_analysis_model_function(chat_logs_request)
    return result

if __name__ == "__main__":
    uvicorn.run("api:app", reload=True, host="0.0.0.0", port=8085)
