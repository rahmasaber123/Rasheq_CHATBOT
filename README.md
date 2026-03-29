# 🚀 Rasheqa Chatbot API

<p align="center">
  <img src=https://github.com/rahmasaber123/Rasheq_CHATBOT/blob/main/assets/image.png?raw=true width="900"/>
</p>
AI-powered chatbot backend built with FastAPI and OpenAI, featuring session-based conversations and scalable API design.

---

## 📌 Overview

Rasheqa Chatbot API is a backend service that enables real-time conversational AI using OpenAI models.
It supports session management, structured API endpoints, and is designed to be easily extendable for production use.

---

## ⚙️ Tech Stack

* **Backend:** FastAPI
* **AI Engine:** OpenAI API (GPT models)
* **Server:** Uvicorn
* **Environment Management:** Python Dotenv
* **Language:** Python 3.x

---

## ✨ Features

* 💬 AI Chat endpoint powered by OpenAI
* 🧠 Session-based conversation handling
* 🔄 Reset conversation state
* ⚡ FastAPI async performance
* 📄 Swagger UI for easy testing (`/docs`)
* 🔐 Environment-based API key handling

---

## 📁 Project Structure

```
rasheqa-chatbot/
│
├── app/                # Main backend logic
├── static/             # Static files (if any)
├── templates/          # HTML templates
├── .env.example        # Environment variables template
├── requirements.txt    # Dependencies
└── main.py / app.py    # Entry point
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/rasheqa-chatbot.git
cd rasheqa-chatbot
```

---

### 2. Create virtual environment

```bash
python -m venv venv
```

### Activate:

```bash
venv\Scripts\activate   # Windows
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Setup environment variables

Create `.env` file:

```env
OPENAI_API_KEY=your_api_key_here
```

---

### 5. Run the server

```bash
uvicorn app.main:app --reload
```

---

### 6. Open API Docs

```
http://127.0.0.1:8000/docs
```

---

## 🔌 API Endpoints

### `GET /`

* Health check / index

### `GET /test-openai`

* Test OpenAI connection

### `POST /api/new-session`

* Create new chat session

### `POST /api/chat`

* Send message to chatbot

### `POST /api/reset`

* Reset session

---

## 🧪 Example Request

```json
{
  "session_id": "your_session_id",
  "message": "Hello, how are you?"
}
```

---

## 🔐 Security Considerations

* API key stored in environment variables
* `.env` excluded via `.gitignore`
* No secrets exposed in source code

⚠️ Recommended improvements:

* Add authentication (JWT / API keys)
* Implement rate limiting
* Add request validation & logging

---

## 📈 Future Improvements

* 🔑 Authentication system
* 📊 Logging & monitoring
* 🌐 Frontend integration
* 🧠 Memory persistence (database)
* 🚀 Deployment (Docker / Cloud)

---

##  Author
ENG Rahma Saber
AI ENGINEER



---

## ⭐ Why This Project Matters

This project demonstrates:

* Real-world API integration (OpenAI)
* Backend architecture design
* Secure handling of sensitive data
* Understanding of AI-powered systems

---

## 📜 License

This project is for educational and portfolio purposes.
