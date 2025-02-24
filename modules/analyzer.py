import os
import yaml
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class Analyzer:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.3,
            openai_api_key=OPENAI_API_KEY,
            max_tokens=None,
            timeout=None,
            streaming=False,
        )
        self.prompts = self.load_prompts()

    def load_prompts(self):
        """
        프롬프트 설정 파일(prompt_config.yaml)에서 프롬프트 정의 로드
        반환: 프롬프트 설정 딕셔너리 반환
        """
        file_path = os.path.join(
            os.path.dirname(__file__), "..", "config/analyzer_prompt.yaml"
        )
        with open(file_path, "r", encoding="utf-8") as file:
            prompt_data = yaml.safe_load(file)

        return prompt_data["prompts"]

    async def get_analysis(self, chatlog):
        prompts = self.prompts
        system_prompt = SystemMessage(content=prompts["system_prompt"])
        user_prompt_text = prompts["user_prompt"].format(chat_history=chatlog)
        user_prompt = HumanMessage(content=user_prompt_text)

        response = self.llm.invoke([system_prompt, user_prompt])
        result_text = response.content.strip()

        return result_text


# +++++++++++++++++++++debug llm+++++++++++++++++++++
if __name__ == "__main__":
    bot = Analyzer()

    file_path = os.path.join(
        os.path.dirname(__file__), "..", "config/dummy_chat_logs.yaml"
    )

    with open(file_path, "r", encoding="utf-8") as file:
        dummy_data = yaml.safe_load(file)

    dummy_logs = dummy_data["dummy_chat_logs"]
    chat = dummy_logs["6번 대화"]["conversation"]

    # chatlog = """나: 그냥 평범했지 뭐 ㅎㅎ 너는?
    # 나: 나도 뭐~ 근데 왠지 모르게 너랑 톡하면 하루가 좀 더 특별해지는 느낌? 😏
    # 상대: 오~ 오늘은 또 왜 이렇게 말이 스윗해? ㅎㅎ
    # 나: 원래도 스윗했는데 너만 몰랐던 거 아냐? 🤭
    # 상대: 아, 맞다! 너 저번에 추천해준 카페 갔다 왔어! 분위기 진짜 좋더라~
    # 나: 오! 진짜? 근데 왜 나랑 안 갔어? 섭섭하네 ㅋㅋ
    # 상대: ㅋㅋㅋ 다음에 같이 가자! 그럼 됐지? 😆
    # 나: 오케이, 약속했어! 말 바꾸기 없기!
    # 상대: 네네~ 근데 너 뭐 먹었어? 저녁 안 챙겨 먹은 거 아니지?
    # 나: 응~ 근데 너 걱정해 주는 거 기분 좋다 😌
    # 상대: 당연하지~ 친구잖아! ㅎㅎ
    # 나: …그치, 친구니까 그렇겠지? (뭔가 아쉽네 ㅋㅋ)
    # 상대: ㅋㅋㅋㅋ 뭔가? 왜 말 흐려~
    # 나: 아냐아냐~ 그냥… 네가 나한테 하는 말이 썸 같기도 하고, 친구 같기도 하고 헷갈려서 ㅎㅎ
    # 상대: 음… 그럼 내가 좀 더 헷갈리게 해줄까? 😉
    # 나: 뭐야ㅋㅋㅋ 궁금한데?"""

    summary = bot.get_analysis(chat)

    print(summary)
