# inference.py

import os
import yaml
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

# 환경 변수 로드
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.3,
    openai_api_key=OPENAI_API_KEY,
)


def load_prompts():
    """
    프롬프트 설정 파일(prompt_config.yaml)에서 프롬프트 정의 로드
    반환: 프롬프트 설정 딕셔너리 반환
    """

    file_path = os.path.join(os.path.dirname(__file__), "..", "prompt_config.yaml")

    with open(file_path, "r", encoding="utf-8") as file:
        prompt_data = yaml.safe_load(file)

    return prompt_data["prompts"]


def interest_analysis_model_function(chat_logs_request):
    """
    채팅 로그 분석을 통한 호감도 평가 수행 함수 정의
    매개변수: chat_logs_request - module.schemas.ChatroomLogsRequest 객체
    반환: {"호감도": sentiment, "이유": explanation} 형태의 딕셔너리 반환
    """

    chat_history = []

    for msg in chat_logs_request.messages:

        if msg.senderId == chat_logs_request.my_userId:
            chat_history.append(f"나 : {msg.message}")
        else:
            chat_history.append(f"상대방 : {msg.message}")

    combined_chat_history = "\n".join(chat_history)

    prompts = load_prompts()
    system_prompt = SystemMessage(content=prompts["system_prompt"])
    user_prompt_text = prompts["user_prompt"].format(chat_history=combined_chat_history)
    user_prompt = HumanMessage(content=user_prompt_text)

    response = llm.invoke([system_prompt, user_prompt])
    result_text = response.content.strip()

    return {"호감도 분석 결과": result_text}
