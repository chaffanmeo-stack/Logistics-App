"""Pydantic models for request bodies and API responses."""

from pydantic import BaseModel, Field


class CustomerLoginRequest(BaseModel):
    phone: str = Field(..., min_length=7, max_length=20)
    pin: str = Field(..., min_length=6, max_length=6)


class StaffLoginRequest(BaseModel):
    email: str
    password: str


class RiderLoginRequest(BaseModel):
    phone: str = Field(..., min_length=7, max_length=20)
    pin: str = Field(..., min_length=6, max_length=6)


class PackageCreateRequest(BaseModel):
    sender_name: str = Field(..., min_length=1)
    receiver_name: str = Field(..., min_length=1)
    receiver_phone: str = Field(..., min_length=7, max_length=20)
    origin_hub: str
    destination_hub: str


class PackageCreateResponse(BaseModel):
    tracking_id: str
    status: str
    # Only populated the first time a new Customer profile is auto-created.
    # Phase 3 (email automation) will remove this and email it instead.
    new_customer_pin: str | None = None
