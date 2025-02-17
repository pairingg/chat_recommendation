from pymongo import MongoClient
from datetime import datetime

mongodb_address = ""
database_name = ""
collection_name = ""

# MongoDB 연결
client = MongoClient(mongodb_address)
db = client[database_name]
collection = db[collection_name]

# 예시: 'roomId'와 'createdAt'을 기준으로 메시지 가져오기
room_id = "room_123"
start_time = datetime(2023, 1, 1)
end_time = datetime(2023, 12, 31)

# 'roomId'가 "room_123"이고, 'createdAt'이 2023년 1월 1일부터 12월 31일 사이인 메시지 가져오기
query = {"roomId": room_id, "createdAt": {"$gte": start_time, "$lte": end_time}}

# 데이터 가져오기
messages = collection.find(query)

# 메시지 출력
for message in messages:
    print(message)
