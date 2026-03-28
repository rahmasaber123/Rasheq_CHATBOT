from __future__ import annotations
import json
import asyncio
from typing import AsyncGenerator

import httpx

from app.config import (
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    MODEL_ID,
    MAX_TOKENS,
    TEMPERATURE,
    TOP_P,
)


class LLMError(Exception):
    """Custom error for LLM issues."""
    pass


def _check_api_key() -> None:
    """Ensure API key exists."""
    if not OPENAI_API_KEY or not OPENAI_API_KEY.startswith("sk-"):
        raise LLMError(
            "🔑 OpenAI API key غير مُعيَّن!\n\n"
            "أضف في ملف .env:\n"
            "OPENAI_API_KEY=sk-proj-xxxxxxxx"
        )


async def stream_chat(
    messages: list[dict[str, str]],
) -> AsyncGenerator[str, None]:
    """
    OpenAI streaming endpoint with robust error handling.
    """

    _check_api_key()

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL_ID,
        "messages": messages,
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
        "top_p": TOP_P,
        "stream": True,
    }

    retries = 3
    base_delay = 2

    # Use proper timeout — connect fast, but allow long reads for streaming
    timeout = httpx.Timeout(connect=15.0, read=120.0, write=15.0, pool=15.0)

    for attempt in range(retries):
        client = None
        try:
            client = httpx.AsyncClient(
                timeout=timeout,
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
            )

            async with client.stream(
                "POST",
                OPENAI_BASE_URL,
                headers=headers,
                json=payload,
            ) as resp:

                # ── Handle error status codes ──
                if resp.status_code == 401:
                    raise LLMError("🔑 مفتاح OpenAI غير صالح. تأكد من صحة المفتاح في ملف .env")

                if resp.status_code == 402:
                    raise LLMError("💳 لا يوجد رصيد كافٍ في حساب OpenAI.")

                if resp.status_code == 429:
                    if attempt < retries - 1:
                        delay = base_delay * (2 ** attempt)  # exponential backoff
                        await asyncio.sleep(delay)
                        await client.aclose()
                        client = None
                        continue
                    raise LLMError("⏳ تم تجاوز حد الطلبات. حاول بعد قليل.")

                if resp.status_code == 404:
                    raise LLMError(f"❌ النموذج '{MODEL_ID}' غير موجود أو لا يمكنك الوصول إليه.")

                if resp.status_code == 500:
                    if attempt < retries - 1:
                        await asyncio.sleep(base_delay)
                        await client.aclose()
                        client = None
                        continue
                    raise LLMError("⚠️ خطأ داخلي من OpenAI. حاول مرة أخرى.")

                if resp.status_code != 200:
                    # Try to read error body
                    error_body = ""
                    try:
                        raw = await resp.aread()
                        error_body = raw.decode("utf-8", errors="replace")[:500]
                    except Exception:
                        pass
                    raise LLMError(
                        f"⚠️ خطأ من OpenAI (HTTP {resp.status_code}): {error_body}"
                    )

                # ── Stream successful response ──
                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue

                    data = line[6:].strip()

                    if data == "[DONE]":
                        return

                    try:
                        chunk = json.loads(data)
                        choices = chunk.get("choices", [])
                        if not choices:
                            continue
                        delta = choices[0].get("delta", {})
                        content = delta.get("content")
                        if content:
                            yield content
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue

                return  # stream completed normally

        except LLMError:
            raise

        except httpx.TimeoutException:
            if attempt < retries - 1:
                await asyncio.sleep(base_delay * (attempt + 1))
                continue
            raise LLMError("⏱️ انتهت مهلة الاتصال بـ OpenAI. حاول مرة أخرى.")

        except httpx.ConnectError:
            if attempt < retries - 1:
                await asyncio.sleep(base_delay * (attempt + 1))
                continue
            raise LLMError("🌐 فشل الاتصال بـ OpenAI. تحقق من اتصال الإنترنت.")

        except httpx.RemoteProtocolError:
            if attempt < retries - 1:
                await asyncio.sleep(base_delay * (attempt + 1))
                continue
            raise LLMError("🌐 انقطع الاتصال أثناء الاستجابة. حاول مرة أخرى.")

        except Exception as e:
            if isinstance(e, (StopAsyncIteration, GeneratorExit)):
                return
            if attempt < retries - 1:
                await asyncio.sleep(base_delay)
                continue
            raise LLMError(f"⚠️ خطأ غير متوقع: {type(e).__name__}: {e}")

        finally:
            if client is not None:
                try:
                    await client.aclose()
                except Exception:
                    pass
