from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class UserRole(str, Enum):
    BUYER = "buyer"
    SELLER = "seller"
    BOTH = "both"


class UserBase(SQLModel):
    name: str
    email: str
    role: UserRole = UserRole.BOTH


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    listings: list["ProductListing"] = Relationship(back_populates="seller")
    purchases: list["Order"] = Relationship(back_populates="buyer")


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: int
    created_at: datetime


class ProductListingBase(SQLModel):
    title: str
    description: str
    price: float
    quantity: int = Field(ge=0)


class ProductListing(ProductListingBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    seller_id: int = Field(foreign_key="user.id")

    seller: Optional[User] = Relationship(back_populates="listings")
    orders: list["Order"] = Relationship(back_populates="product")


class ProductListingCreate(ProductListingBase):
    seller_id: int


class ProductListingRead(ProductListingBase):
    id: int
    created_at: datetime
    seller_id: int


class OrderBase(SQLModel):
    quantity: int = Field(gt=0)


class Order(OrderBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    buyer_id: int = Field(foreign_key="user.id")
    product_id: int = Field(foreign_key="productlisting.id")
    total_price: float

    buyer: Optional[User] = Relationship(back_populates="purchases")
    product: Optional[ProductListing] = Relationship(back_populates="orders")


class OrderCreate(OrderBase):
    buyer_id: int
    product_id: int


class OrderRead(OrderBase):
    id: int
    created_at: datetime
    buyer_id: int
    product_id: int
    total_price: float
