from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
import asyncio
from modules.analyzer import *
from modules.summarizer import *
from modules.integrator import *
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()


class InfoRequest(BaseModel):
    user_id: str
    room_id: str


class RecommendationResponse(BaseModel):
    message: str


def get_messages(user_id, room_id):
    integrator = Integrator(db="", collection="", room_id=room_id)
    chatlog = integrator.get_chatlog(user_id)
    cleanlog = integrator.clean_chatlog(chatlog)

    return cleanlog


async def summarize(chatlog):
    summarizer = Summarizer()
    summary = await summarizer.get_summary(chatlog)

    return summary


async def analyze(chatlog):
    analyzer = Analyzer()
    analysis = await analyzer.get_analysis(chatlog)

    return analysis


@app.post("/chatlog", response_model=RecommendationResponse)
async def return_info(request: InfoRequest):
    try:
        user_id = request.user_id
        room_id = request.room_id

        chatlog = get_messages(user_id, room_id)
        summary, analysis = await asyncio.gather(summarize(chatlog), analyze(chatlog))

        message = summary + analysis

        return RecommendationResponse(message=message)
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
