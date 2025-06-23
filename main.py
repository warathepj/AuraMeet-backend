from fastapi import FastAPI, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import os
import shutil
import httpx # Import httpx for making HTTP requests

# Global dictionary to store loaded Excel DataFrames
excel_data = {}

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

@app.on_event("startup")
async def load_excel_data():
    excel_dir = "backend/excel"
    if not os.path.exists(excel_dir):
        print(f"Directory '{excel_dir}' does not exist. No Excel files to load.")
        return

    for filename in os.listdir(excel_dir):
        if filename.endswith(".xlsx"):
            file_path = os.path.join(excel_dir, filename)
            try:
                df = pd.read_excel(file_path)
                excel_data[os.path.splitext(filename)[0]] = df
                print(f"Loaded '{filename}' into pandas DataFrame.")
            except Exception as e:
                print(f"Error loading '{filename}': {e}")
    print(f"All Excel files loaded. Available DataFrames: {list(excel_data.keys())}")

@app.get("/")
async def read_root():
    return {"message": "Hello, AuraMeet!"}

@app.post("/message")
async def create_message(message: Message):
    print(f"Received message from mobile: {message.message}")

    webhook_url = "http://localhost:5678/webhook-test/1d1a9fa9-7f57-44b4-835d-d79ed8a4ec25"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, json={"message": message.message})
            response.raise_for_status() # Raise an exception for 4xx or 5xx responses
        print(f"Message successfully forwarded to webhook. Status: {response.status_code}")
        return {"message": f"Message '{message.message}' forwarded to webhook."}
    except httpx.RequestError as exc:
        print(f"An error occurred while requesting {exc.request.url!r}: {exc}")
        return {"message": f"Failed to forward message: Connection error to webhook."}
    except httpx.HTTPStatusError as exc:
        print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}: {exc}")
        return {"message": f"Failed to forward message: Webhook returned error status {exc.response.status_code}."}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {"message": f"Failed to forward message: An unexpected error occurred."}

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
