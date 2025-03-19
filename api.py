from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
import uvicorn
import asyncio
from modules.analyzer import *
from modules.summarizer import *
from modules.recommender import *
from modules.integrator import *
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()


class InfoRequest(BaseModel):
    room_id: str
    my_id: str
    your_id: str


class RecommendationResponse(BaseModel):
    summary: list[str]
    analysis: list[str]
    recommendation: list[str]


def get_messages(user_id, room_id):
    integrator = Integrator(
            mongo_address="mongodb://mongo-container:27017",
            db="pairing", 
            collection="Chatting", 
            room_id=room_id
            ) # MongoDB
    chatlog = integrator.get_chatlog(user_id)
    cleanlog = integrator.clean_chatlog(chatlog)

    return cleanlog


def get_our_info(my_id, your_id, room_id):
    integrator = Integrator(
        Integrator(db="pairing", collection="Chatting", room_id=room_id)
    )
    # MySQL:
    # integrator의 get_user_info 함수에서
    # conn 변수에 사전에 알맞게 정보 입력하면 됨으로
    # Integrator() 초기화 필요 X
    my_info = integrator.get_user_info(my_id)
    your_info = integrator.get_user_info(your_id)

    return my_info, your_info


async def summarize(chatlog):
    summarizer = Summarizer()
    summary = await summarizer.get_summary(chatlog)

    return summary


async def analyze(chatlog):
    analyzer = Analyzer()
    analysis = await analyzer.get_analysis(chatlog)

    return analysis


def recommend(summary, analysis, my_info, your_info):
    recommender = Recommender()
    recommendation = recommender.get_recommendation(
        summary, analysis, my_info, your_info
    )

    return recommendation


@app.post("/chatrooms/chatting_recommender", response_model=RecommendationResponse)
async def return_recommendation(request: InfoRequest):
    try:
        room_id = request.room_id
        my_id = request.my_id
        your_id = request.your_id

        chatlog = get_messages(my_id, room_id)
        summary, analysis = await asyncio.gather(summarize(chatlog), analyze(chatlog))

        my_info, your_info = get_our_info(my_id, your_id)
        recommendation = recommend(summary, analysis, my_info, your_info)

        return RecommendationResponse(
            summary=summary, 
            analysis=analysis, 
            recommendation=recommendation
        )
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("api:app", reload=True, host="0.0.0.0", port=8086)
