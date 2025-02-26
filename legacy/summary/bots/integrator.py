from pymongo import MongoClient
import re

# 한국어 불용어 사전: https://www.ranks.nl/stopwords/korean
# txt 파일이나 csv 파일로 정리해놓고 이를 불러와서 사용


class Integrator:
    mongodb_address = ""
    database_name = ""
    collection_name = ""

    def __init__(self, room_id):
        self.room_id = room_id

    def get_chatlog(self):
        client = MongoClient(self.mongodb_address)
        db = client[self.database_name]
        collection = db[self.collection_name]

        query = {"roomId": self.room_id}
        messages = collection.find(query).sort("createdAt", 1)

        chatlog = "\n".join(f"{msg['sender']}: {msg['message']}" for msg in messages)

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
