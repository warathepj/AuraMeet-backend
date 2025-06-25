# ซอร์สโค้ดนี้ ใช้สำหรับเป็นตัวอย่างเท่านั้น ถ้านำไปใช้งานจริง ผู้ใช้ต้องจัดการเรื่องความปลอดภัย และ ประสิทธิภาพด้วยตัวเอง

-----

# AuraMeet AI Chatbot

AuraMeet is a comprehensive system consisting of a mobile application, a FastAPI backend, and an n8n workflow. It powers an AI chatbot capable of answering user questions based on dynamically provided Excel data, acting as a knowledge base. The system is designed to process incoming messages from the mobile app, allow users to upload Excel files, utilize an AI agent with a Google Gemini chat model for intelligent responses, and maintain a short-term memory of the conversation.

-----

## Features

  * **Mobile Chat Interface:** A user-friendly mobile application for interacting with the AI chatbot.
  * **Excel File Upload:** Users can upload Excel (.xlsx) files directly from the mobile app to the backend, which then serves as the dynamic knowledge base for the AI.
  * **Dynamic Knowledge Base:** The backend loads uploaded Excel files into pandas DataFrames, which are then included with every message sent to the n8n webhook, providing real-time context to the AI.
  * **Webhook Trigger:** Easily integrates with external applications (like the FastAPI backend) to receive user messages and their associated Excel data.
  * **Dynamic Session Management:** Generates unique session IDs for each conversation using various fallback options (request ID, user ID, chat ID, or a timestamp).
  * **Contextual AI Responses:** Uses an AI Agent (Langchain) to understand user questions and provide relevant answers from the provided Excel data.
  * **Google Gemini Integration:** Leverages the `models/gemini-2.5-flash-preview-05-20` model for powerful and efficient natural language processing.
  * **Short-Term Memory:** Incorporates a simple memory buffer to maintain conversation context for up to 10 interactions.
  * **Thai Language Support:** Configured to answer questions in Thai.
  * **Concise Answers:** Limits answers to a maximum of 5 relevant rows of data when the knowledge base contains extensive information.

-----

## How It Works

The system operates in a series of integrated steps:

1.  **Mobile Application (React Native):**
    *   **Chat Screen:** Users type messages, which are sent to the FastAPI backend's `/message` endpoint.
    *   **Upload Screen:** Users select Excel (.xlsx) files, which are then uploaded to the FastAPI backend's `/upload-excel/` endpoint.

2.  **FastAPI Backend (Python):**
    *   **File Upload:** Receives Excel files from the mobile app, saves them to the `backend/excel` directory, and loads them into pandas DataFrames, making them available in a global `excel_data` dictionary.
    *   **Message Processing:** Receives user messages from the mobile app. For each message, it includes *all currently loaded Excel data* (converted to JSON) as `session_data` in the payload.
    *   **Webhook Forwarding:** Forwards the user's message and the `session_data` to the n8n workflow's webhook.
    *   **Response Handling:** Receives the AI's response from the n8n webhook, extracts the `output` field, and sends it back to the mobile application.

3.  **n8n Workflow:**
    *   **Webhook:** Listens for incoming `POST` requests from the FastAPI backend to a specific path (`your_webhook_path`). The incoming data contains the user's `message` and the `session_data` (Excel data).
    *   **Edit Fields:** Extracts and organizes key information from the incoming webhook data, including `sessionId`, `message`, and `session_data`.
    *   **AI Agent:** This is the core intelligence. It takes the user's `message` and the `session_data` (Excel data) as input. It's configured to:
        *   Answer the user's question based on the provided knowledge.
        *   Respond in Thai language.
        *   Limit responses to a maximum of 5 relevant data points if the knowledge base is large.
    *   **Google Gemini Chat Model:** Provides the AI capabilities for the AI Agent. It uses the specified Gemini model to process natural language and generate responses.

    *   **Simple Memory:** Stores recent conversation turns (up to 10) to help the AI Agent maintain context throughout the dialogue.
    *   **Respond to Webhook:** Sends the AI Agent's generated answer back as a response to the original webhook request (to the FastAPI backend).

-----

## Setup

To run the AuraMeet system, you'll need to set up the FastAPI backend, the React Native mobile application, and the n8n workflow.

### 1. FastAPI Backend Setup

```sh
https://github.com/warathepj/AuraMeet-backend.git
```
1.  **Navigate to the `backend` directory:**
    ```bash
    cd AuraMeet-backend
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt # Assuming you have a requirements.txt
    ```
    (If `requirements.txt` does not exist, you'll need to install `fastapi`, `uvicorn`, `pandas`, `openpyxl`, `httpx`, `python-multipart` manually: `pip install fastapi uvicorn pandas openpyxl httpx python-multipart`)
3.  **Run the backend server:**
    ```bash
    uvicorn main:app --reload --port 8000
    ```
    The backend will run on `http://localhost:8000`.

### 2. React Native Mobile Application Setup

```sh
https://github.com/warathepj/AuraMeet-mobile.git
```

1.  **Navigate to the `mobile` directory:**
    ```bash
    cd AuraMeet-mobile
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```
3.  **Start the Expo development server:**
    ```bash
    npx expo start
    ```
    This will typically open a browser window with a QR code. You can scan this QR code with the Expo Go app on your mobile device (iOS or Android) or run it in a simulator/emulator. The app will connect to the backend at `http://localhost:8000`.

### 3. n8n Workflow Setup

1.  **n8n Instance:** A running instance of n8n.
2.  **Google Gemini API Key:** You'll need credentials for the Google Gemini (PaLM) API. This workflow uses a credential named "Google Gemini(PaLM) Api account". Ensure this credential is set up correctly in your n8n instance.

#### Deployment Steps:

1.  **Create a New Workflow:** 
2.  **Configure Webhook:** The webhook is pre-configured with a path (`your_webhook_path`). Ensure this matches the `webhook_url` in `backend/main.py`. Note down the full webhook URL provided by n8n after activation.
3.  **Activate Workflow:** Set the workflow to "Active" in n8n.

**Important:** Ensure the FastAPI backend is running *before* you start the mobile application, as the mobile app will attempt to connect to it.

-----

## Usage

1.  **Start the Backend:** Ensure your FastAPI backend is running (`uvicorn main:app --reload --port 8000` in the `backend` directory).
2.  **Start the Mobile App:** Run the Expo development server (`npx expo start` in the `AuraMeet-mobile` directory) and open the app on your device or emulator.
3.  **Upload Excel Files:**
    *   Navigate to the "Upload Page" within the mobile app.
    *   Tap "Upload Excel File" and select an `.xlsx` file from your device.
    *   The file will be uploaded to the backend and loaded as a knowledge base.
4.  **Chat with the AI:**
    *   Go back to the chat screen.
    *   Type your message in the input field and tap "Send".
    *   The mobile app sends your message to the FastAPI backend.
    *   The backend forwards your message along with *all currently loaded Excel data* to the n8n webhook.
    *   The n8n workflow processes the request using the AI Agent and Google Gemini, generating a response based on the Excel data.
    *   The AI's response is sent back through the backend to the mobile app and displayed in the chat.

**Example Interaction:**

*   **User uploads `products.xlsx`** containing:
    ```
    Product,Price,Stock
    Laptop,1200,50
    Mouse,25,200
    Keyboard,75,100
    ```
*   **User message (from mobile app):** "ราคาของ Laptop คือเท่าไหร่?" (What is the price of Laptop?)
*   **AI Response (in mobile app):** "ราคาของ Laptop คือ 1200 บาท" (The price of Laptop is 1200 Baht)

-----

## Customization

  * **AI Agent Prompt:** Modify the `text` parameter in the "AI Agent" node to change how the AI processes questions and generates answers.
  * **Memory Length:** Adjust the `contextWindowLength` in the "Simple Memory" node to control how many past interactions the AI remembers.
  * **Google Gemini Model:** You can switch to a different Google Gemini model if desired by changing the `modelName` in the "Google Gemini Chat Model" node.
  * **Webhook Path:** Change the `path` in the "Webhook" node to customize your endpoint.

-----
