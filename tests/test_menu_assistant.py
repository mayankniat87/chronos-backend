"""Tests for the grounded 'Ask AI' menu assistant.

Runs entirely offline (LLM_PROVIDER defaults to 'mock', so the assistant
uses its deterministic grounded fallback path).
"""

import os
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models.restaurant import InventoryItem, MenuItem, Restaurant  # noqa: E402
from app.services.menu_ai.assistant import (  # noqa: E402
    NOT_ON_MENU_REPLY,
    _validate_answer,
    ask_menu_assistant,
)
from app.services.menu_ai.context_builder import invalidate_menu_context  # noqa: E402
from app.services.menu_ai.retrieval import retrieve_relevant_items  # noqa: E402


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)
    session = TestingSession()

    restaurant = Restaurant(id=1, name="Trattoria Roma", cuisine_type="Italian")
    session.add(restaurant)
    session.add_all(
        [
            MenuItem(id=1, restaurant_id=1, name="Margherita Pizza", category="Pizza", cost_price=4, sell_price=12.5),
            MenuItem(id=2, restaurant_id=1, name="Pepperoni Pizza", category="Pizza", cost_price=5, sell_price=14.0),
            MenuItem(id=3, restaurant_id=1, name="Tiramisu", category="Dessert", cost_price=2, sell_price=7.0),
            MenuItem(id=4, restaurant_id=1, name="Spaghetti Carbonara", category="Pasta", cost_price=3, sell_price=13.0),
        ]
    )
    # Tiramisu out of stock
    session.add(InventoryItem(restaurant_id=1, menu_item_id=3, stock_qty=0.0))
    session.commit()

    invalidate_menu_context()
    yield session
    session.close()


@pytest.fixture()
def client(db_session):
    app.dependency_overrides[get_db] = lambda: iter([db_session])
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()


# --- Retrieval ---------------------------------------------------------------

def test_retrieval_finds_named_dish(db_session):
    items = [
        {"id": 1, "name": "Margherita Pizza", "category": "Pizza", "price": 12.5, "available": True},
        {"id": 3, "name": "Tiramisu", "category": "Dessert", "price": 7.0, "available": True},
    ]
    found, had_match = retrieve_relevant_items("do you have margherita pizza?", items)
    assert had_match
    assert found[0]["id"] == 1


def test_retrieval_no_match_returns_full_menu(db_session):
    items = [{"id": 1, "name": "Margherita Pizza", "category": "Pizza", "price": 12.5, "available": True}]
    found, had_match = retrieve_relevant_items("what do you have?", items)
    assert not had_match
    assert found == items


# --- Assistant behavior ------------------------------------------------------

def test_existing_dish_answer_uses_real_price(db_session):
    result = ask_menu_assistant(db_session, 1, "Do you have Margherita Pizza?")
    assert "Margherita Pizza" in result["answer"]
    assert "$12.50" in result["answer"]
    assert result["out_of_menu"] is False


def test_nonexistent_dish_gets_polite_refusal(db_session):
    result = ask_menu_assistant(db_session, 1, "Can I get a sushi platter?")
    assert result["answer"].startswith(NOT_ON_MENU_REPLY)
    assert result["out_of_menu"] is True


def test_unavailable_item_flagged(db_session):
    result = ask_menu_assistant(db_session, 1, "One tiramisu please")
    assert "unavailable" in result["answer"].lower()


def test_browse_question_lists_only_real_items(db_session):
    result = ask_menu_assistant(db_session, 1, "What's on the menu?")
    assert "Margherita Pizza" in result["answer"]
    # Unavailable item is not offered
    assert "Tiramisu" not in result["answer"]


def test_repeated_question_not_identical(db_session):
    a1 = ask_menu_assistant(db_session, 1, "Do you have Margherita Pizza?", session_id="s1")
    a2 = ask_menu_assistant(db_session, 1, "Do you have Margherita Pizza?", session_id="s1")
    assert a1["answer"] != a2["answer"]


def test_empty_menu_graceful(db_session):
    db_session.add(Restaurant(id=2, name="Empty Diner"))
    db_session.commit()
    invalidate_menu_context()
    result = ask_menu_assistant(db_session, 2, "Do you have pizza?")
    assert "menu is being updated" in result["answer"]


def test_unknown_restaurant_raises(db_session):
    with pytest.raises(ValueError):
        ask_menu_assistant(db_session, 999, "Do you have pizza?")


# --- Answer validation (anti-hallucination guardrail) ------------------------

MENU = [{"id": 1, "name": "Margherita Pizza", "category": "Pizza", "price": 12.5, "available": True}]


def test_validator_rejects_unknown_item_ids():
    raw = {"answer": "Try our Truffle Burger!", "matched_item_ids": [99], "out_of_menu": False}
    assert _validate_answer(raw, MENU) is None


def test_validator_rejects_fabricated_price():
    raw = {"answer": "Margherita Pizza is $9.99.", "matched_item_ids": [1], "out_of_menu": False}
    assert _validate_answer(raw, MENU) is None


def test_validator_accepts_real_price():
    raw = {"answer": "Margherita Pizza is $12.50.", "matched_item_ids": [1], "out_of_menu": False}
    assert _validate_answer(raw, MENU) is not None


def test_validator_rejects_empty_answer():
    assert _validate_answer({"answer": "", "matched_item_ids": []}, MENU) is None
    assert _validate_answer("not a dict", MENU) is None


# --- API endpoint ------------------------------------------------------------

def test_ask_endpoint_success(client):
    resp = client.post("/api/ask", json={"restaurant_id": 1, "question": "Do you have pepperoni pizza?"})
    assert resp.status_code == 200
    body = resp.json()
    assert "Pepperoni Pizza" in body["answer"]
    assert body["grounded"] is True


def test_ask_endpoint_404_for_unknown_restaurant(client):
    resp = client.post("/api/ask", json={"restaurant_id": 999, "question": "pizza?"})
    assert resp.status_code == 404


def test_ask_endpoint_validates_empty_question(client):
    resp = client.post("/api/ask", json={"restaurant_id": 1, "question": ""})
    assert resp.status_code == 422
