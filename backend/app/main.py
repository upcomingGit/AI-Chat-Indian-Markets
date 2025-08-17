from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from app.llm_router import router as chat_router

load_dotenv(dotenv_path="app/.env")

app = FastAPI()
#app.include_router(chat_router, prefix="/chat")



# Allow frontend access (dev mode)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://saras-ai-assistant-frontend.azurewebsites.net",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/chat")

# Optional: avoid 307 redirect from /chat to /chat/ by handling both.
@app.get("/chat")
async def chat_root_get():
    return {"message": "Chat endpoint is available. POST to /chat/ for queries."}

@app.get("/")
async def root():
    return {"status": "ok"}


#class ChatRequest(BaseModel):
#    query: str

#@app.post("/chat")
#async def chat(req: ChatRequest):
#    query = req.query.lower()
#    print(f"Received query: {query}")
#    # Placeholder: replace this with OpenAI + SQL logic later
#    if "revenue" in query:
#        return {"answer": "The company's revenue for FY2023 was ₹12,345 crore."}
#    elif "profit" in query:
#        return {"answer": "The net profit for FY2023 was ₹2,300 crore."}
#    else:
#        return {"answer": "I'm still learning how to fetch that. Try asking about revenue or profit!"}
