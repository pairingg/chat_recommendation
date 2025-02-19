# schemas.py

from pydantic import BaseModel
from typing import List

class ChatMessage(BaseModel):
    """
    채팅 메시지 모델 정의
    """
    senderId : str  #: 메시지 보낸 사용자 ID 정의
    message : str   #: 메시지 내용 정의

class ChatroomLogsRequest(BaseModel):
    """
    채팅 로그 요청 모델 정의
    """
    chatroomId : str               #: 채팅방 ID 정의
    my_userId : str                #: 분석 요청한 사용자 ID 정의
    messages : List[ChatMessage]   #: 채팅 메시지 리스트 정의

class ChatroomRequest(BaseModel):
    """
    DB에서 채팅 로그를 가져오기 위한 요청 모델 정의
    """
    chatroomId : str  #: 채팅방 ID 정의
    my_userId : str   #: 분석 요청한 사용자 ID 정의
