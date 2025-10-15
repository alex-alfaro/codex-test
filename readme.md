# Handcrafted Marketplace PoC

A minimalistic business-to-consumer marketplace inspired by Etsy. Built with FastAPI and SQLModel, it allows you to create users, publish listings, browse inventory, and place orders.

## Architecture Overview

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) with [SQLModel](https://sqlmodel.tiangolo.com/) on top of SQLite for quick persistence.
- **Frontend**: Lightweight static HTML page served by FastAPI, styled with Milligram CSS and vanilla JavaScript for API interactions.
- **Testing**: [Pytest](https://docs.pytest.org/) with FastAPI's `TestClient` to validate marketplace flows.

This stack is intentionally simple to keep the proof-of-concept fast to iterate on while remaining production-friendly.

## Getting Started

### 1. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the application

```bash
uvicorn app.main:app --reload
```

The site will be available at http://127.0.0.1:8000/. The REST API lives under the same host.

### 3. Run the test suite

```bash
pytest
```

## Key API Endpoints

| Method | Endpoint         | Description                             |
| ------ | ---------------- | --------------------------------------- |
| POST   | `/users`         | Register a buyer/seller account         |
| GET    | `/users/{id}`    | Retrieve a user profile                 |
| POST   | `/listings`      | Publish a product listing               |
| GET    | `/listings`      | Browse listings with optional filters   |
| POST   | `/orders`        | Place an order and decrement inventory  |
| GET    | `/orders/{id}`   | Retrieve order details                  |

## Data Model

- **User** – stores name, email, and role (buyer, seller, or both).
- **ProductListing** – seller-owned item with price, description, and quantity.
- **Order** – links a buyer to a product listing and tracks the quantity purchased and total price.

## Next Steps

Potential follow-up enhancements:

- Authentication and session management
- Payment integrations and order status workflow
- Richer listing metadata (images, categories, tags)
- Seller dashboards and analytics
- Search and discovery improvements

This PoC lays the groundwork for experimentation and user testing while keeping the codebase approachable.
