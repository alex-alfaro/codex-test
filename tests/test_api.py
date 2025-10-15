from fastapi.testclient import TestClient

from app.main import app
from app.db import init_db, session_scope
from app.models import Order, ProductListing, User


client = TestClient(app)


def setup_module(module):
    # Reset database between test runs
    init_db()
    with session_scope() as session:
        session.query(Order).delete()
        session.query(ProductListing).delete()
        session.query(User).delete()


def test_create_user_listing_and_order():
    user_response = client.post(
        "/users",
        json={"name": "Alice", "email": "alice@example.com", "role": "seller"},
    )
    assert user_response.status_code == 201
    seller = user_response.json()

    buyer_response = client.post(
        "/users",
        json={"name": "Bob", "email": "bob@example.com", "role": "buyer"},
    )
    assert buyer_response.status_code == 201
    buyer = buyer_response.json()

    listing_response = client.post(
        "/listings",
        json={
            "title": "Soy Candle",
            "description": "Lavender scented handmade candle",
            "price": 25.0,
            "quantity": 3,
            "seller_id": seller["id"],
        },
    )
    assert listing_response.status_code == 201
    listing = listing_response.json()

    order_response = client.post(
        "/orders",
        json={
            "buyer_id": buyer["id"],
            "product_id": listing["id"],
            "quantity": 2,
        },
    )
    assert order_response.status_code == 201
    order = order_response.json()

    assert order["total_price"] == 50.0

    updated_listing = client.get(f"/listings/{listing['id']}").json()
    assert updated_listing["quantity"] == 1


def test_duplicate_user_email_fails():
    client.post(
        "/users",
        json={"name": "Charlie", "email": "charlie@example.com", "role": "seller"},
    )
    duplicate_response = client.post(
        "/users",
        json={"name": "Charles", "email": "charlie@example.com", "role": "buyer"},
    )
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Email already registered"


def test_order_with_insufficient_quantity():
    seller = client.post(
        "/users",
        json={"name": "Dana", "email": "dana@example.com", "role": "seller"},
    ).json()
    buyer = client.post(
        "/users",
        json={"name": "Eli", "email": "eli@example.com", "role": "buyer"},
    ).json()
    listing = client.post(
        "/listings",
        json={
            "title": "Wool Scarf",
            "description": "Handwoven scarf",
            "price": 40.0,
            "quantity": 1,
            "seller_id": seller["id"],
        },
    ).json()

    order_response = client.post(
        "/orders",
        json={
            "buyer_id": buyer["id"],
            "product_id": listing["id"],
            "quantity": 2,
        },
    )
    assert order_response.status_code == 400
    assert order_response.json()["detail"] == "Not enough quantity available"
