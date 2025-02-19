# db_getter.py

import os
from pymongo import MongoClient
from dotenv import load_dotenv
from module.schemas import ChatMessage, ChatroomLogsRequest

# 환경 변수 로드
load_dotenv()

def load_chat_logs_from_db(chatroom_id: str, my_userId: str) -> ChatroomLogsRequest:
    """
    MongoDB에서 지정된 채팅방의 채팅 로그를 조회하여 ChatroomLogsRequest 객체 생성
    매개변수: chatroom_id - 채팅방 ID, my_userId - 분석 요청한 사용자 ID
    반환: ChatroomLogsRequest 객체 반환
    """

    mongodb_uri = os.getenv("MONGODB_URI")
    if not mongodb_uri:
        raise ValueError("MongoDB URI가 .env 파일에 설정되어 있지 않음")

    client = MongoClient(mongodb_uri)
    db = client['chatbot_db']        # 데이터베이스 이름 수정 필요
    collection = db['chat_logs']       # 컬렉션 이름 수정 필요

    chatroom_doc = collection.find_one({"chatroomId": chatroom_id})
    if not chatroom_doc:
        raise ValueError(f"채팅방 ID '{chatroom_id}'에 해당하는 채팅 로그를 찾을 수 없음")

    messages_data = chatroom_doc.get("messages", [])
    messages_data = sorted(messages_data, key=lambda x: x.get("timestamp", 0))

    messages = []
    for msg in messages_data:
        sender = msg.get("senderId", "")
        message_text = msg.get("message", "")
        messages.append(ChatMessage(senderId=sender, message=message_text))
    
    return ChatroomLogsRequest(chatroomId=chatroom_id, my_userId=my_userId, messages=messages)
