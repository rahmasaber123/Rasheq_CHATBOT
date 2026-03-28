"""
Rasheqa Chatbot — FastAPI Server
Streaming responses via Server-Sent Events (SSE).
"""

from __future__ import annotations

import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.config import HOST, PORT
from app.session import Session, get_session, delete_session
from app.prompt import build_system_prompt
from app.llm import stream_chat, LLMError

# ── App ─────────────────────────────────────────────────────

app = FastAPI(title="Rasheqa Chatbot API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directory (create it if missing so the server doesn't crash)
import os
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ── Schemas ─────────────────────────────────────────────────


class ChatRequest(BaseModel):
    session_id: str = ""
    message: str


class NewSessionResponse(BaseModel):
    session_id: str
    greeting: str


# ── Greeting ────────────────────────────────────────────────

GREETING_AR = (
    "مرحباً بك في رشيقة! 👋\n\n"
    "أنا مساعدك المتخصص في التغذية والبرامج الغذائية.\n\n"
    "⚠️ **تنبيه طبي مهم:**\n"
    "إذا كنت تعاني من أي حالة طبية مزمنة، يُرجى استشارة طبيب مختص قبل البدء بأي برنامج.\n\n"
    "كيف يمكنني مساعدتك اليوم؟"
)


# ── Routes ──────────────────────────────────────────────────


@app.get("/", response_class=HTMLResponse)
async def index():
    with open("templates/index.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.post("/api/new-session", response_model=NewSessionResponse)
async def new_session():
    sid = uuid.uuid4().hex
    session = get_session(sid)
    session.greeted = True
    session.add("assistant", GREETING_AR)
    return NewSessionResponse(session_id=sid, greeting=GREETING_AR)


@app.post("/api/chat")
async def chat(req: ChatRequest):
    """
    Streaming chat endpoint.
    Returns text/event-stream with word-by-word chunks.
    """
    # Validate session_id — create one if empty
    if not req.session_id:
        req.session_id = uuid.uuid4().hex

    # Validate message
    if not req.message or not req.message.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "الرسالة فارغة"},
        )

    session = get_session(req.session_id)

    # extract metrics if possible
    session.try_extract_metrics(req.message)

    # record user message
    session.add("user", req.message)

    # build messages payload
    system_prompt = build_system_prompt(session.user_profile)
    api_messages = [{"role": "system", "content": system_prompt}]
    api_messages.extend(session.history_for_api(last_n=16))

    # stream response
    async def event_generator():
        full_response = []
        try:
            async for chunk in stream_chat(api_messages):
                full_response.append(chunk)
                # SSE format
                yield f"data: {chunk}\n\n"
        except LLMError as e:
            error_msg = str(e)
            yield f"data: {error_msg}\n\n"
            full_response.append(error_msg)
        except Exception as e:
            error_msg = f"⚠️ خطأ: {type(e).__name__}: {e}"
            yield f"data: {error_msg}\n\n"
            full_response.append(error_msg)
        finally:
            # save complete response to session
            complete = "".join(full_response)
            if complete:
                session.add("assistant", complete)
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/reset")
async def reset(req: ChatRequest):
    delete_session(req.session_id)
    return await new_session()


# ── Health check ────────────────────────────────────────────

@app.get("/api/health")
async def health():
    from app.config import OPENAI_API_KEY
    has_key = bool(OPENAI_API_KEY and OPENAI_API_KEY.startswith("sk-"))
    return {"status": "ok", "api_key_configured": has_key}


# ── Run ─────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    from app.config import OPENAI_API_KEY

    print("\n" + "=" * 60)
    print("🏥  Rasheqa Chatbot Server")
    print("=" * 60)

    if not OPENAI_API_KEY or not OPENAI_API_KEY.startswith("sk-"):
        print("⚠️  WARNING: OPENAI_API_KEY is not set!")
        print("   Create a .env file with:")
        print("   OPENAI_API_KEY=sk-your-actual-key")
        print("   Get a key at: https://platform.openai.com/api-keys")
    else:
        key_preview = OPENAI_API_KEY[:12] + "..." + OPENAI_API_KEY[-4:]
        print(f"✅  API Key: {key_preview}")

    print(f"🌐  Open http://localhost:{PORT}")
    print("=" * 60 + "\n")

    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
