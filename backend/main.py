"""Campus Customs API — the app you run with uvicorn from the backend/ folder:

    uvicorn main:app --reload --port 8000

Problem 3: storefront (products, images).
Problem 4: account creation + login.
Problem 5: the PydanticAI chat agent, wired to the website's chat widget.
"""

from __future__ import annotations

import json
import sqlite3

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse

from agent import ChatDeps, ViewingProduct, run_chat, run_chat_stream
from auth import hash_password, make_token, verify_password, verify_token
from db import (
    PRODUCTS_DIR,
    create_user,
    ensure_seed_logins,
    get_chat_history,
    get_product,
    get_user_by_email,
    get_user_by_id,
    list_products,
    save_chat_message,
)
from models import (
    ChatRequest,
    ChatResponse,
    LoginRequest,
    ProductCard,
    SignupRequest,
)

app = FastAPI(title="Campus Customs API", version="0.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    ensure_seed_logins()


# ---------------------------------------------------------------- catalogue

@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/products")
def products() -> list[dict]:
    return list_products()


@app.get("/api/products/{product_id}")
def product(product_id: str) -> dict:
    item = get_product(product_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return item


@app.get("/media/products/{filename}")
def product_image(filename: str) -> FileResponse:
    if "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    path = PRODUCTS_DIR / filename
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(path, media_type="image/jpeg")


# ---------------------------------------------------------------- auth

@app.post("/api/signup", status_code=201)
def signup(req: SignupRequest) -> dict:
    try:
        user = create_user(
            first_name=req.first_name,
            last_name=req.last_name,
            email=str(req.email),
            password_hash=hash_password(req.password),
        )
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="An account with that email already exists.")
    # Issue a signed session token so later requests prove who they are.
    return {"user": user, "token": make_token(user["id"])}


@app.post("/api/login")
def login(req: LoginRequest) -> dict:
    row = get_user_by_email(str(req.email))
    if row is None or not verify_password(row["password_hash"], req.password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    return {
        "user": {
            "id": row["id"],
            "email": row["email"],
            "first_name": row["first_name"],
            "last_name": row["last_name"],
            "name": row["name"],
        },
        "token": make_token(row["id"]),
    }


# ---------------------------------------------------------------- chat agent

def _authed_user_id(authorization: str | None) -> int | None:
    """The user id from a verified Bearer token, or None (guest / bad token).

    Identity is taken ONLY from the signed token — never from a client-supplied id —
    so a request cannot impersonate another customer.
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    return verify_token(authorization[7:].strip())


def _build_deps(req: ChatRequest, auth_user_id: int | None):
    """Identity + page context for a chat request. Returns (deps, user_row|None).

    Identity comes from the verified token (auth_user_id), not from the request body.
    """
    deps = ChatDeps()
    row = get_user_by_id(auth_user_id) if auth_user_id is not None else None
    if row is not None:
        deps.user_id = row["id"]
        deps.first_name = row["first_name"]
        deps.last_name = row["last_name"]
        deps.email = row["email"]

    if req.page_product_id:
        p = get_product(req.page_product_id)
        if p is not None:
            deps.viewing = ViewingProduct(
                product_id=p["product_id"],
                name=p["name"],
                garment_type=p["garment_type"],
                colors=p["colors"],
                price=p["price"],
            )
    return deps, row


def _hydrate(product_ids: list[str]) -> list[ProductCard]:
    """Re-hydrate agent product_ids into full cards from the DB (dedup, keep order)."""
    cards: list[ProductCard] = []
    seen: set[str] = set()
    for pid in product_ids:
        if pid in seen:
            continue
        seen.add(pid)
        detail = get_product(pid)
        if detail is not None:
            cards.append(ProductCard(**detail))
    return cards


def _persist_turn(row, message: str, reply: str, cards: list[ProductCard]) -> None:
    if row is None:
        return
    products_json = json.dumps([c.model_dump() for c in cards]) if cards else None
    save_chat_message(row["id"], "user", message)
    save_chat_message(row["id"], "assistant", reply, products_json)


# When the model provider's own guardrails block a prompt, degrade to a polite refusal
# instead of a 502 — this is the safety layer failing safe, not the store being "down".
_BLOCK_MARKERS = ("content_filter", "content management policy", "cyber_policy", "responsible ai")
_REFUSAL = (
    "Woof — I can't help with that one. I'm here to help you shop Campus Customs Yale gear: "
    "want to see hoodies, tees, or something for your college or team?"
)


def _is_blocked(exc: Exception) -> bool:
    return any(m in str(exc).lower() for m in _BLOCK_MARKERS)


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, authorization: str | None = Header(default=None)) -> ChatResponse:
    """One shopper turn -> agent reply plus the products it chose to show (non-streaming).

    The agent returns product_ids; we re-hydrate them from the database so price,
    stock, and images on the page are the real values, not the model's memory.
    """
    deps, row = _build_deps(req, _authed_user_id(authorization))
    try:
        result = await run_chat(message=req.message, deps=deps, history=req.history)
    except Exception as exc:  # noqa: BLE001
        if _is_blocked(exc):
            _persist_turn(row, req.message, _REFUSAL, [])
            return ChatResponse(reply=_REFUSAL, products=[])
        raise HTTPException(status_code=502, detail=f"The assistant is unavailable: {exc}")

    cards = _hydrate(result.product_ids)
    _persist_turn(row, req.message, result.reply, cards)
    return ChatResponse(reply=result.reply, products=cards)


@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest, authorization: str | None = Header(default=None)) -> StreamingResponse:
    """Streaming version of /api/chat (Server-Sent Events).

    Emits `{"type":"delta","text":...}` as the reply is written, then one
    `{"type":"final","reply":...,"products":[...]}` with the hydrated product cards.
    The product cards are still filled from the DB, never the model's memory.
    """
    deps, row = _build_deps(req, _authed_user_id(authorization))

    async def event_stream():
        final_reply = ""
        product_ids: list[str] = []
        try:
            async for kind, payload in run_chat_stream(
                message=req.message, deps=deps, history=req.history
            ):
                if kind == "delta":
                    yield f"data: {json.dumps({'type': 'delta', 'text': payload})}\n\n"
                else:  # final ChatReply
                    final_reply = payload.reply
                    product_ids = payload.product_ids
        except Exception as exc:  # noqa: BLE001
            if _is_blocked(exc):
                # Provider guardrail blocked it — fail safe as a polite refusal.
                _persist_turn(row, req.message, _REFUSAL, [])
                yield f"data: {json.dumps({'type': 'delta', 'text': _REFUSAL})}\n\n"
                yield f"data: {json.dumps({'type': 'final', 'reply': _REFUSAL, 'products': []})}\n\n"
                return
            yield f"data: {json.dumps({'type': 'error', 'detail': str(exc)})}\n\n"
            return

        cards = _hydrate(product_ids)
        _persist_turn(row, req.message, final_reply, cards)
        final_event = {
            "type": "final",
            "reply": final_reply,
            "products": [c.model_dump() for c in cards],
        }
        yield f"data: {json.dumps(final_event)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/api/chat/history")
def chat_history(authorization: str | None = Header(default=None)) -> dict:
    """Reload the authenticated shopper's own saved chat turns.

    The user is taken from the verified token only — you can only ever read your own
    history, never another customer's by passing their id.
    """
    auth_user_id = _authed_user_id(authorization)
    if auth_user_id is None or get_user_by_id(auth_user_id) is None:
        raise HTTPException(status_code=401, detail="Sign in to view your chat history.")
    return {"history": get_chat_history(auth_user_id)}
