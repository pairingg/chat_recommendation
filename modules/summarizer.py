from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from konlpy.tag import Okt
from modules.integrator import *

load_dotenv()


class Summarizer:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            max_tokens=None,
            timeout=None,
            streaming=False,
        )
        self.okt = Okt()

    def get_summary(self, chatlog):
        prompt = f"""
        당신은 호감도 분석을 위해 대화 내용을 요약하는 챗봇입니다.
        대화의 주체는 A 와 B 두 사람입니다. 각 사람의 취미, 관심사, 취향 등 상대의 호감도를 높이기 위한 주제에 집중해 대화 내용을 요약하세요.
        취미, 관심사, 취향 이외의 내용은 제외해줘.
        일관된 내용들을 bullet point 를 이용해 정리해줘.
        대화 내용: {chatlog}
        """
        response = self.llm(prompt)

        return response.content


if __name__ == "__main__":
    bot = Summarizer()

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


""" 사용자가 보는거
대화 요약:
- A와 B 모두 불고기를 좋아함
- A는 매운 음식을 좋아하고, B는 매운 음식을 못 먹음
- B는 주말에 운동과 등산을 즐김, A도 등산을 좋아함
- B는 강아지를 정말 좋아하고, A도 강아지와 함께 산책하는 것을 즐거워함

호감도 분석:
상대가 나의 말에 적극적으로 반응하고, 썸을 탄다는 뉘앙스를 풍기네요! 호감도가 있어보여요.

다음 대화:
둘의 공통 관심사는 강아지네요. 강아지에 대한 얘기를 더 하는 걸 추천드려요
아직 취미에 대한 이야기가 부족해보여요. 상대의 취미 중에 "영화 감상" 이 있네요!
"""
