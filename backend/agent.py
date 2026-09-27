"""Campus Customs chat agent — wiring only.

Loads the model (OpenAI via Portkey), the system prompt from prompts/prompt.md, and
the tools from tools.py, and exposes `run_chat()` for the FastAPI layer to call.
The API app lives in main.py; this file is just the agent.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

from pydantic_ai import Agent, RunContext, UsageLimits
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, TextPart, UserPromptPart
from pydantic_ai.models.openai import OpenAIChatModel, OpenAIChatModelSettings
from pydantic_ai.providers.openai import OpenAIProvider

import audit
from models import ChatReply, ChatTurn
from tools import check_size_stock, get_product_details, search_products

BACKEND_DIR = Path(__file__).resolve().parent
PROMPT_PATH = BACKEND_DIR / "prompts" / "prompt.md"

DEFAULT_BASE_URL = "https://api.portkey.ai/v1"
DEFAULT_MODEL = "gpt-5.6-terra"

# Keep a runaway conversation from burning tokens: read, call a tool or two, answer.
MAX_REQUESTS = 6

# gpt-5.6-terra is a reasoning model; at default effort it spends seconds "thinking"
# before every answer, which caused ~27s replies. A shop assistant answering price/stock
# questions from tools doesn't need that. The gateway also requires reasoning_effort
# "none" when function tools are used on the chat-completions endpoint, so this both
# satisfies that constraint and is the single biggest chat-latency win (Problem 9).
MODEL_SETTINGS = OpenAIChatModelSettings(openai_reasoning_effort="none")


def _load_env(path: Path) -> None:
    """Minimal .env loader — avoids a python-dotenv dependency."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


# Load .env from backend/ or the repo root (either location works). setdefault means
# the first file found wins and real environment variables always take precedence.
_load_env(BACKEND_DIR / ".env")
_load_env(BACKEND_DIR.parent / ".env")


@dataclass
class ViewingProduct:
    """The product the shopper is currently looking at on the site (page context)."""
    product_id: str
    name: str
    garment_type: str
    colors: list[str]
    price: float


@dataclass
class ChatDeps:
    """Per-conversation context handed to the agent.

    Identity fields let the agent know *who* is chatting; `viewing` carries page
    context so deictic references ("this", "it") resolve to the product on screen.
    """
    user_id: int | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    viewing: ViewingProduct | None = None


def build_model() -> OpenAIChatModel:
    api_key = os.getenv("PORTKEY_API_KEY")
    if not api_key:
        sys.exit("PORTKEY_API_KEY is not set. Copy backend/.env.example to backend/.env.")
    provider = OpenAIProvider(
        api_key=api_key,
        base_url=os.getenv("PORTKEY_BASE_URL", DEFAULT_BASE_URL),
    )
    return OpenAIChatModel(os.getenv("PORTKEY_MODEL", DEFAULT_MODEL), provider=provider)


def build_agent() -> Agent[ChatDeps, ChatReply]:
    agent = Agent(
        build_model(),
        deps_type=ChatDeps,
        output_type=ChatReply,
        model_settings=MODEL_SETTINGS,
        system_prompt=PROMPT_PATH.read_text(encoding="utf-8"),
        tools=[search_products, get_product_details, check_size_stock],
    )

    @agent.system_prompt
    def who_is_here(ctx: RunContext[ChatDeps]) -> str:
        d = ctx.deps
        if d and d.user_id is not None:
            name = " ".join(p for p in [d.first_name, d.last_name] if p) or "unknown"
            return (
                f"The shopper is logged in. Name: {name}. Email: {d.email or 'unknown'}. "
                f"You may greet them by first name. This is their own account, so it's fine "
                f"to reference their name/email if relevant — never anyone else's."
            )
        return "The shopper is a guest (not logged in); you don't know their name."

    @agent.system_prompt
    def page_context(ctx: RunContext[ChatDeps]) -> str:
        v = ctx.deps.viewing if ctx.deps else None
        if v is None:
            return "The shopper is not on a specific product page right now."
        colors = ", ".join(v.colors) if v.colors else "unspecified"
        return (
            f"PAGE CONTEXT: the shopper is currently viewing this product — "
            f"{v.name} (product_id: {v.product_id}, {v.garment_type}, ${v.price:.0f}, "
            f"colors: {colors}). If they say \"this\", \"it\", or \"this one\" without "
            f"naming a product, they mean this one — use its product_id with your tools."
        )

    return agent


# Built once at import; the system prompt is read a single time.
_AGENT = build_agent()


def _to_message_history(history: list[ChatTurn]) -> list[ModelMessage]:
    """Turn stored user/assistant turns into pydantic-ai message history."""
    messages: list[ModelMessage] = []
    for turn in history:
        if turn.role == "user":
            messages.append(ModelRequest(parts=[UserPromptPart(content=turn.content)]))
        elif turn.role == "assistant":
            messages.append(ModelResponse(parts=[TextPart(content=turn.content)]))
    return messages


async def run_chat(
    message: str,
    deps: ChatDeps | None = None,
    history: list[ChatTurn] | None = None,
) -> ChatReply:
    """Run one shopper turn and return the structured reply."""
    try:
        result = await _AGENT.run(
            message,
            deps=deps or ChatDeps(),
            message_history=_to_message_history(history or []),
            usage_limits=UsageLimits(request_limit=MAX_REQUESTS),
        )
    except Exception as exc:  # noqa: BLE001
        audit.record_error(message, "chat", f"{type(exc).__name__}: {exc}")
        raise
    audit.record_run(result, subject=message, mode="chat")
    return result.output


async def run_chat_stream(
    message: str,
    deps: ChatDeps | None = None,
    history: list[ChatTurn] | None = None,
):
    """Stream one shopper turn.

    Yields ("delta", text) as the reply is generated, then ("final", ChatReply) once
    the run completes. Tool round-trips happen before the final answer streams, so the
    shopper sees the answer appear as it's written instead of waiting for the whole thing.
    """
    try:
        async with _AGENT.run_stream(
            message,
            deps=deps or ChatDeps(),
            message_history=_to_message_history(history or []),
            usage_limits=UsageLimits(request_limit=MAX_REQUESTS),
        ) as result:
            emitted = ""
            async for partial in result.stream_output(debounce_by=0.05):
                reply = getattr(partial, "reply", "") or ""
                if len(reply) > len(emitted):
                    yield "delta", reply[len(emitted):]
                    emitted = reply
            final = await result.get_output()
            # If nothing streamed (short/edge cases), emit the full reply now.
            if not emitted and final.reply:
                yield "delta", final.reply
            audit.record_run(result, subject=message, mode="stream")
            yield "final", final
    except Exception as exc:  # noqa: BLE001
        audit.record_error(message, "stream", f"{type(exc).__name__}: {exc}")
        raise
