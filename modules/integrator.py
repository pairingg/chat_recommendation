from pymongo import MongoClient
import mysql.connector
from konlpy.tag import Okt
import re


class Integrator:

    def __init__(self, mongo_address, db, collection, room_id):
        self.address = mongo_address
        self.db = db
        self.collection = collection
        self.room_id = room_id
        self.okt = Okt()

    def get_chatlog(self, user_id):
        client = MongoClient(self.address)
        db = client[self.db]
        collection = db[self.collection]

        query = {"chatroomId": self.room_id}
        messages = collection.find(query).sort("createdAt", 1)

        chatlog = "\n".join(
            f"{'나' if msg['sender'] == user_id else '상대'}: {msg['message']}"
            for msg in messages
        )
        return chatlog

    def clean_chatlog(self, chatlog):
        messages = [chat.strip() for chat in chatlog.split("\n")]
        result = []
        for message in messages:
            speaker = message[0]
            message = message[3:]
            singles_removed = re.sub(r"([ㄱ-ㅎㅏ-ㅣ])\1{2,}", r"\1\1", message)
            emoji_removed = re.sub("[^\w\s\n]", "", singles_removed)

            words = self.okt.pos(emoji_removed)
            nouns_and_adjectives = [
                word for word, tag in words if tag in ["Noun", "Adjective"]
            ]
            processed = " ".join(nouns_and_adjectives)
            processed = re.sub(r"님은요|에요|네요|그런데|그래서", "", processed)
            result.append(f"{speaker}: {processed}")

        return "\n".join(result)

def get_user_info(self, user_id):

    conn = mysql.connector.connect(
        host="mysql-container",
        user="chat-recommendation",     
        password="limitedPass",         
        database="pairing"      
    )
    cursor = conn.cursor(dictionary=True)

    query_member = """
        SELECT age, birth, city, district, drink, gender, mbti, smoking
        FROM member 
        WHERE user_id = %s
    """

    cursor.execute(query_member, (user_id,))
    member_info = cursor.fetchone()
    # member_info = {
    # "birth": "1995-03-25",
    # "mbti": "ENFP",
    # "drink": "Y",
    # "smoking": "N",
    # "residence": "서울특별시",
    # "region": "마포구"
    # }

    if member_info:
        gender_map = {0: "남자", 1: "여자"}
        drink_map = {0: "전혀 안마심", 1: "피할 수 없을 때만", 2: "가끔 마심", 3: "자주 마심", 4: "금주중"}
        smoking_map = {0: "비흡연", 1: "가끔 피움", 2: "매일 피움", 3: "전자 담배", 4: "금연중"}

        member_info["gender"] = gender_map.get(member_info["gender"], member_info["gender"])
        member_info["drink"] = drink_map.get(member_info["drink"], member_info["drink"])
        member_info["smoking"] = smoking_map.get(member_info["smoking"], member_info["smoking"])

    query_hobby = """
        SELECT hobby 
        FROM hobby 
        WHERE member_user_id = %s
    """
    cursor.execute(query_hobby, (user_id,))
    hobby_rows = cursor.fetchall()
    # 예시
    # hobby_rows = [
    # {"hobby": "독서"},
    # {"hobby": "영화 감상"},
    # {"hobby": "운동"}
    # ]
    hobbies = [row["hobby"] for row in hobby_rows] if hobby_rows else []
    # 예시
    # hobbies = ["독서", "영화 감상", "운동"]

    cursor.close()
    conn.close()

    return {
        "사용자 기본 정보": member_info,
        "사용자의 취미 목록": hobbies,
    }