from fastapi import FastAPI, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import shutil

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

@app.post("/upload-excel/")
async def upload_excel_file(request: Request, file: UploadFile = File(...)):
    print(f"Received file upload request.")
    print(f"File filename: {file.filename}")
    print(f"File content type: {file.content_type}")
    print(f"Request headers: {request.headers}")

    upload_dir = "backend/excel"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"message": f"File '{file.filename}' uploaded successfully to {file_path}"}
    except Exception as e:
        return {"message": f"Error uploading file: {e}"}
    finally:
        file.file.close()
