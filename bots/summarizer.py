from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from konlpy.tag import Okt
import re

load_dotenv()


class SummaryBot:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            max_tokens=None,
            timeout=None,
            streaming=False,
        )
        self.okt = Okt()

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

    def get_summary(self, chatlog):
        processed_chatlog = self.clean_chatlog(chatlog)
        prompt = f"""
        당신은 호감도 분석을 위해 대화 내용을 요약하는 챗봇입니다.
        대화의 주체는 A 와 B 두 사람입니다. 각 사람의 취미, 관심사, 취향 등 상대의 호감도를 높이기 위한 주제에 집중해 대화 내용을 요약하세요.
        내가 명시한 내용과 요약 내용 이외의 수식어는 제외해줘.
        출력 결과는 bullet point 를 이용해 정리해줘.
        대화 내용: {processed_chatlog}
        """
        response = self.llm(prompt)

        return response.content


if __name__ == "__main__":
    bot = SummaryBot()

    chat = """A: 안녕하세요! 반갑습니다.  
    B: 안녕하세요!ㅎㅎ 만나서 반가워요.  
    A: 취미가 어떻게 되세요?  
    B: 저는 여행 다니는 걸 좋아해요. 새로운 곳을 가는 게 재미있더라고요.  
    A: 저도 여행 좋아해요! 최근에 어디 다녀오셨어요?  
    B: 얼마 전에 제주도를 다녀왔어요. 바다가 정말 예쁘더라고요.  
    A: 와, 저도 제주도 좋아해요. 특히 성산일출봉에서 보는 일출이 멋지죠.  
    A: 혹시 좋아하는 음식 있으세요?  
    B: 저는 파스타랑 한식을 좋아해요. 특히 불고기를 자주 먹어요.  
    A: 저도 불고기 좋아해요! 고기류 좋아하시나 보네요.  
    B: 네ㅋㅋㅋㅋㅋ 맞아요. 그런데 매운 음식은 잘 못 먹어요. A 님은요?  
    A: 저는 매운 음식 좋아하는 편이에요. 매운 라면 같은 거 자주 먹어요.  
    A: 주말에는 주로 뭐 하세요?  
    B: 보통 운동하러 가요. 헬스장 다니고 있는데, 가끔 등산도 해요.  
    A: 저도 등산 좋아하는데! 최근에 어디 다녀오셨어요?  
    B: 얼마 전에 북한산에 갔어요. 경치가 정말 좋았어요.  
    A: 혹시 강아지나 고양이 좋아하세요?  
    B: 네! 저는 강아지를 정말 좋아해요. 나중에 반려견 키우고 싶어요.  
    A: 저도요! 강아지 키우면 같이 산책 다니는 게 즐거울 것 같아요."""

    # +++++++++++++++++++++debug llm+++++++++++++++++++++
    summary = bot.get_summary(chat)

    print(summary)

    # +++++++++++++++++++++debug tokenizer+++++++++++++++++++++
    # print(bot.clean_chatlog(chat))
