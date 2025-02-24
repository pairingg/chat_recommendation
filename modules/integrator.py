from pymongo import MongoClient
import mysql.connector
import re


class Integrator:

    def __init__(self, mongo_address, db, collection, room_id):
        self.address = mongo_address
        self.db = db
        self.collection = collection
        self.room_id = room_id

    def get_chatlog(self, user_id):
        client = MongoClient(self.address)
        db = client[self.db]
        collection = db[self.collection]

        query = {"roomId": self.room_id}
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

    def get_our_id(self, user_id):

        # 클라이언트 측에서 상대방 아이디 받을 수 있으면 이 코드 안적어도 될 듯
        # 버튼 누른 사람 아이디(내 아이디)만 전달 받으니까 상대방 아이디를 몰라서
        client = MongoClient(self.address)
        db = client[self.db]
        collection = db[self.collection]

        query = {"roomId": self.room_id}
        messages = collection.find(query)

        my_id = None
        your_id = None
        index = 0

        while index < len(messages):
            msg = messages[index]

            if msg["sender"] == user_id:
                my_id = user_id
            else:
                your_id = msg["sender"]
            if my_id is not None and your_id is not None:
                break

            index += 1  # 다음 메시지로 이동

        return my_id, your_id

    def get_user_info(self, user_id):
        
        conn = mysql.connector.connect(
            host="MYSQL_HOST",  
            user="MYSQL_USER",  
            password="MYSQL_PASSWORD",  
            database="MYSQL_DATABASE",  
        )

        cursor = conn.cursor(dictionary=True)

        query_member = """
            SELECT birth, mbti, drink, smoking, residence, region 
            FROM Member 
            WHERE userId = %s
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

        query_hobby = """
            SELECT hobby 
            FROM Hobby 
            WHERE userId = %s
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
            "사용자 기본 정보": member_info, # 딕셔너리
            "사용자의 취미 목록": hobbies,  # 리스트
        }
