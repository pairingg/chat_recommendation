import os
import yaml
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class Recommender:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o", 
            temperature=1.0,
            openai_api_key=OPENAI_API_KEY,
            max_tokens=None,
            timeout=None,
            streaming=False,
        )
        self.prompts = self.load_prompts()

    def load_prompts(self):
        file_path = os.path.join(
            os.path.dirname(__file__), "..", "config/recommender_prompt.yaml"
        )
        with open(file_path, "r", encoding="utf-8") as file:
            prompt_data = yaml.safe_load(file)
        return prompt_data["prompts"]

    def get_recommendation(self, summary, analysis, my_info, your_info):
        # system prompt에 세 단계 결과와 DB 정보를 포맷팅해서 전달
        system_text = self.prompts["system_prompt"].format(
            summary=summary, analysis=analysis, my_info=my_info, your_info=your_info
        )
        system_prompt = SystemMessage(content=system_text)
        user_prompt = HumanMessage(content=self.prompts["user_prompt"])

        response = self.llm.invoke([system_prompt, user_prompt])
        result_text = response.content.strip()
        return "다음 대화 추천: \n" + result_text


# +++++++++++++++++++++ debug llm +++++++++++++++++++++
if __name__ == "__main__":
    # 테스트용 코드 (샘플 입력)
    bot = Recommender()

    sample_summary = """
        대화 요약: 
            - 상대와 나 모두 집에서 쉬고 있음
            - 최근 본 영화와 책에 대해 이야기 함
            - 상대가 요즘 날씨에 대해 언급하며 추운 날씨에 공감함
            - 주말 계획에 대해 서로 궁금해함
            - 대화가 자연스럽게 이어지며 서로의 관심사에 대한 탐색이 있음
            """
    sample_analysis = """    
        호감도 분석: 
        상대는 나에게 호감이 있어 보입니다. 상대는 대화를 이어가려는 노력을 보이며, 주말 계획을 물어보는 등 나에게 관심을 보이고 있습니다. 
        또한, 대화 중간에 날씨에 대해 이야기하며 공통된 주제를 찾으려는 모습도 보입니다. 
        이러한 요소들은 상대가 나에게 친밀감을 느끼고 있다는 신호로 해석될 수 있습니다.
        """
    sample_my_info = {
        "member": {
            "birth": "1990-01-01",
            "mbti": "INTJ",
            "drink": "O",
            "smoking": "X",
            "residence": "서울",
            "region": "강남",
        },
        "hobbies": ["영화 감상", "독서"],
    }

    sample_your_info = {
        "member": {
            "birth": "2002-04-15",
            "mbti": "ISTP",
            "drink": "O",
            "smoking": "X",
            "residence": "서울",
            "region": "홍대",
        },
        "hobbies": ["음악 감상", "운동"],
    }

    recommendation = bot.get_recommendation(
        sample_summary,
        sample_analysis,
        sample_my_info,
        sample_your_info,
    )

    print(recommendation)
