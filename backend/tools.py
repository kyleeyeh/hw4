"""Tools the Campus Customs agent can call.

Every tool reads live data through db.py, so the agent's answers about price and
stock come from the database rather than the model's memory. Tools return typed
models (models.py) so pydantic-ai validates their shape.
"""

from __future__ import annotations

import db
from models import ProductHit, ProductInfo, SizeStock


def search_products(
    query: str = "",
    garment_type: str | None = None,
    color: str | None = None,
    max_price: float | None = None,
    in_stock_only: bool = False,
) -> list[ProductHit]:
    """Search the catalogue for products matching a shopper's request.

    Args:
        query: free-text keywords, e.g. "navy hoodie" or "davenport crewneck".
        garment_type: optional category filter — one of T-Shirt, Crewneck, Hoodie,
            Quarter-Zip, Jacket, Full-Zip Hoodie, Performance Shirt, Mockneck.
        color: optional color filter, e.g. "navy", "white", "red".
        max_price: optional maximum price in dollars.
        in_stock_only: if true, only return products with at least one size in stock.

    Returns compact product hits (id, name, type, price, colors, availability).
    Use the product_id from a hit when you want full details or to display it.
    """
    hits = db.search_catalogue(
        query=query,
        garment_type=garment_type,
        color=color,
        max_price=max_price,
        in_stock_only=in_stock_only,
    )
    return [ProductHit(**h) for h in hits]


def get_product_details(product_id: str) -> ProductInfo:
    """Look up the full details of one product by its product_id: its description,
    price, and live per-size stock.

    Call this before quoting a price, describing a product, or telling a shopper
    whether their size is available — every number and the description come straight
    from the database, never from memory. If found is False, the id does not exist.
    """
    detail = db.get_product(product_id)
    if detail is None:
        return ProductInfo(product_id=product_id, name="", found=False)
    inventory = [SizeStock(**s) for s in detail["inventory"]]
    return ProductInfo(
        product_id=detail["product_id"],
        name=detail["name"],
        garment_type=detail["garment_type"],
        description=detail["description"],
        colors=detail["colors"],
        price=detail["price"],
        inventory=inventory,
        available_sizes=[s.size for s in inventory if s.quantity > 0],
        total_stock=detail["total_stock"],
        found=True,
    )


def check_size_stock(product_id: str, size: str) -> str:
    """Check whether a specific size of a product is in stock.

    `size` should be one of XS, S, M, L, XL, XXL. Returns a short honest statement
    of how many are available (or that the size/product isn't found).
    """
    detail = db.get_product(product_id)
    if detail is None:
        return f"No product with id '{product_id}' exists."
    size = size.upper().strip()
    for s in detail["inventory"]:
        if s["size"] == size:
            if s["quantity"] == 0:
                return f"{detail['name']} in size {size} is sold out."
            return f"{detail['name']} in size {size}: {s['quantity']} in stock."
    return f"{detail['name']} is not offered in size {size}."
