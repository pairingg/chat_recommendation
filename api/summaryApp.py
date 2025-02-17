from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from bots.summarizer import *

app = FastAPI()


@app.get("/summarize")
async def summarize():
    bot = SummaryBot()
    result = model_inference()
    return {"result": result}
