from typing import Annotated, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select

from .db import get_session, init_db
from .models import (
    Order,
    OrderCreate,
    OrderRead,
    ProductListing,
    ProductListingCreate,
    ProductListingRead,
    User,
    UserCreate,
    UserRead,
)

app = FastAPI(title="Handcrafted Marketplace PoC")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


SessionDep = Annotated[Session, Depends(get_session)]


@app.get("/", response_class=HTMLResponse)
def read_root() -> HTMLResponse:
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.post("/users", response_model=UserRead, status_code=201)
def create_user(user: UserCreate, session: SessionDep) -> User:
    existing_user = session.exec(select(User).where(User.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = User.model_validate(user, update={})
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@app.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, session: SessionDep) -> User:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/listings", response_model=ProductListingRead, status_code=201)
def create_listing(
    listing: ProductListingCreate, session: SessionDep
) -> ProductListing:
    seller = session.get(User, listing.seller_id)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")

    db_listing = ProductListing.model_validate(listing, update={})
    session.add(db_listing)
    session.commit()
    session.refresh(db_listing)
    return db_listing


@app.get("/listings", response_model=List[ProductListingRead])
def list_listings(
    session: SessionDep,
    search: Optional[str] = Query(default=None, description="Filter by title substring"),
    seller_id: Optional[int] = Query(default=None, description="Filter by seller"),
) -> List[ProductListing]:
    query = select(ProductListing)
    if search:
        query = query.where(ProductListing.title.contains(search))
    if seller_id:
        query = query.where(ProductListing.seller_id == seller_id)
    query = query.order_by(ProductListing.created_at.desc())
    listings = session.exec(query).all()
    return listings


@app.get("/listings/{listing_id}", response_model=ProductListingRead)
def get_listing(listing_id: int, session: SessionDep) -> ProductListing:
    listing = session.get(ProductListing, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


@app.post("/orders", response_model=OrderRead, status_code=201)
def create_order(order: OrderCreate, session: SessionDep) -> Order:
    buyer = session.get(User, order.buyer_id)
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")

    product = session.get(ProductListing, order.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.quantity < order.quantity:
        raise HTTPException(status_code=400, detail="Not enough quantity available")

    product.quantity -= order.quantity
    db_order = Order(
        buyer_id=order.buyer_id,
        product_id=order.product_id,
        quantity=order.quantity,
        total_price=product.price * order.quantity,
    )

    session.add(db_order)
    session.add(product)
    session.commit()
    session.refresh(db_order)
    return db_order


@app.get("/orders/{order_id}", response_model=OrderRead)
def get_order(order_id: int, session: SessionDep) -> Order:
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
