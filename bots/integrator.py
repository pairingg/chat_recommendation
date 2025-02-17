from pymongo import MongoClient
import re


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
        messages = collection.find(query)

    def clean_chatlog(self, chatlog):
        messages = [chat.strip() for chat in chatlog.split("\n")]
        result = []
        for message in messages:
            speaker = message[0]
            message = message[3:]
            singles_removed = re.sub("([ㄱ-ㅎㅏ-ㅣ]+)", "", message)
            emoji_removed = re.sub("[^\w\s\n]", "", singles_removed)

            words = self.okt.pos(emoji_removed)
            nouns_and_adjectives = [
                word for word, tag in words if tag in ["Noun", "Adjective"]
            ]
            processed = " ".join(nouns_and_adjectives)
            processed = re.sub(r"님은요|에요|네요|그런데|그래서", "", processed)
            result.append(f"{speaker}: {processed}")

        return "\n".join(result)
