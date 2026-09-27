"""Structured types for Campus Customs — shared by the agent, its tools, and the API.

Two layers:
  * Tool-facing types the agent reads (SearchResult, ProductInfo, StockAnswer).
  * Agent output (ChatReply) and the HTTP request/response shapes for /api/chat.
"""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


# --------------------------------------------------------------------------
# Product shapes (also what the front end renders on the page)
# --------------------------------------------------------------------------

class SizeStock(BaseModel):
    size: str
    quantity: int


class ProductCard(BaseModel):
    """A product as shown on the page and returned to the chat widget."""
    product_id: str
    name: str
    garment_type: str
    description: str
    colors: list[str] = Field(default_factory=list)
    price: float
    image_url: str
    inventory: list[SizeStock] = Field(default_factory=list)
    total_stock: int = 0


class ProductHit(BaseModel):
    """Compact shape a search tool hands back to the model — enough to decide
    relevance without flooding the context with every field."""
    product_id: str
    name: str
    garment_type: str
    price: float
    colors: list[str] = Field(default_factory=list)
    short_description: str
    total_stock: int
    available_sizes: list[str] = Field(default_factory=list)


class ProductInfo(BaseModel):
    """A full single-product lookup for the agent: the real description, price, and
    per-size stock straight from the database. This is what the agent reads to answer
    "tell me about X", "how much is X", and "do you have X in <size>"."""
    product_id: str
    name: str
    garment_type: str = ""
    description: str = ""
    colors: list[str] = Field(default_factory=list)
    price: float = 0.0
    inventory: list[SizeStock] = Field(default_factory=list)
    available_sizes: list[str] = Field(default_factory=list)
    total_stock: int = 0
    found: bool = True


# --------------------------------------------------------------------------
# Agent output
# --------------------------------------------------------------------------

class ChatReply(BaseModel):
    """What the agent produces on every turn.

    `product_ids` are the catalogue ids the agent chose to surface. The backend
    re-hydrates them from the database into full ProductCards, so the price, stock,
    and image shown on the page are always the real values — never the model's memory.
    """
    reply: str = Field(description="The assistant's message to the shopper.")
    product_ids: list[str] = Field(
        default_factory=list,
        description="Catalogue product_ids to display alongside the reply (may be empty).",
    )


# --------------------------------------------------------------------------
# HTTP shapes for /api/chat
# --------------------------------------------------------------------------

class ChatTurn(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    history: list[ChatTurn] = Field(default_factory=list)
    # Page context: the product_id the shopper is currently viewing, if any, so
    # "do you have this in pink?" resolves to the right item.
    page_product_id: str | None = None
    # NOTE: identity is NOT taken from the request body — it comes only from the signed
    # Authorization bearer token (see main._authed_user_id), so a client can't impersonate
    # another customer by supplying their user id.


class ChatResponse(BaseModel):
    reply: str
    products: list[ProductCard] = Field(default_factory=list)


# --------------------------------------------------------------------------
# Auth request shapes (kept here so main.py imports one module)
# --------------------------------------------------------------------------

class SignupRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=200)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=200)
