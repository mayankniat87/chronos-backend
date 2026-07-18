"""Builds and caches the grounding context for the menu assistant.

The LLM must only ever see real data pulled from the database. This module
converts DB rows into a compact dict snapshot and caches it per restaurant
with a short TTL so repeated questions don't re-query the whole menu.
"""

import logging
import threading
import time
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.restaurant import InventoryItem, MenuItem, Restaurant

logger = logging.getLogger(__name__)

# --- Simple per-restaurant TTL cache -----------------------------------------
_CACHE_TTL_SECONDS = 60.0
_cache: Dict[int, Dict[str, Any]] = {}
_cache_lock = threading.Lock()


def invalidate_menu_context(restaurant_id: Optional[int] = None) -> None:
    """Drop cached context (call after menu uploads/edits)."""
    with _cache_lock:
        if restaurant_id is None:
            _cache.clear()
        else:
            _cache.pop(restaurant_id, None)


def build_menu_context(db: Session, restaurant_id: int) -> Optional[Dict[str, Any]]:
    """Returns the grounding snapshot for a restaurant, or None if the
    restaurant does not exist. Cached for a short TTL.
    """
    now = time.monotonic()
    with _cache_lock:
        entry = _cache.get(restaurant_id)
        if entry and now - entry["at"] < _CACHE_TTL_SECONDS:
            return entry["context"]

    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        return None

    menu_items: List[MenuItem] = (
        db.query(MenuItem).filter(MenuItem.restaurant_id == restaurant_id).all()
    )

    # Availability: an item is available unless every linked inventory row
    # reports zero stock. Items without inventory rows default to available.
    stock_by_item: Dict[int, float] = {}
    inventory = (
        db.query(InventoryItem)
        .filter(InventoryItem.restaurant_id == restaurant_id)
        .all()
    )
    for inv in inventory:
        stock_by_item[inv.menu_item_id] = (
            stock_by_item.get(inv.menu_item_id, 0.0) + (inv.stock_qty or 0.0)
        )

    items = []
    categories = set()
    for mi in menu_items:
        categories.add(mi.category)
        available = stock_by_item.get(mi.id, 1.0) > 0
        items.append(
            {
                "id": mi.id,
                "name": mi.name,
                "category": mi.category,
                "price": round(mi.sell_price, 2),
                "available": available,
            }
        )

    context = {
        "restaurant": {
            "id": restaurant.id,
            "name": restaurant.name,
            "cuisine_type": restaurant.cuisine_type,
        },
        "categories": sorted(categories),
        "menu_items": items,
    }

    with _cache_lock:
        _cache[restaurant_id] = {"at": now, "context": context}
    logger.info(
        f"Built menu context for restaurant {restaurant_id}: "
        f"{len(items)} items, {len(categories)} categories"
    )
    return context
