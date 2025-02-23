from pymongo import MongoClient
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
