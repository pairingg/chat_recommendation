# dummy.py

import os
import yaml
from module.schemas import ChatMessage, ChatroomLogsRequest

def load_dummy_chat_logs(dialogue_key: str, my_userId: str) -> ChatroomLogsRequest:
    """
    더미 채팅 로그 파일(dummy_chat_logs.yaml)에서 지정 대화(dialogue_key)의 채팅 로그 로드
    매개변수: dialogue_key - 대화 키, my_userId - 분석 요청한 사용자 ID
    반환: ChatroomLogsRequest 객체 반환
    """

    file_path = os.path.join(os.path.dirname(__file__), "..", "dummy_chat_logs.yaml")

    with open(file_path, "r", encoding="utf-8") as file:
        dummy_data = yaml.safe_load(file)

    dummy_logs = dummy_data["dummy_chat_logs"]

    if dialogue_key not in dummy_logs:
        raise ValueError(f"{dialogue_key} 대화 데이터가 존재하지 않음")

    conversation = dummy_logs[dialogue_key]["conversation"]

    messages = []
    for msg in conversation:
        parts = msg.split(":", 1)
        sender, message = parts[0].strip(), parts[1].strip()
        messages.append(ChatMessage(senderId=sender, message=message))

    return ChatroomLogsRequest(chatroomId="dummy_chatroom", my_userId=my_userId, messages=messages)
