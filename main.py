from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

class Message(BaseModel):
    message: str

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8081", # For React Native development server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Hello, AuraMeet!"}

@app.post("/message")
async def create_message(message: Message):
    print(f"Received message from mobile: {message.message}")
    return {"message": f"Echo: {message.message}"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}
