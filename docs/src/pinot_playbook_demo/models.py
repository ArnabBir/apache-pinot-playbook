from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, ConfigDict


class City(str, Enum):
    bengaluru = "bengaluru"
    mumbai = "mumbai"
    delhi = "delhi"
    hyderabad = "hyderabad"
    pune = "pune"
    chennai = "chennai"


class ServiceTier(str, Enum):
    economy = "economy"
    premium = "premium"
    xl = "xl"


class EventType(str, Enum):
    created = "created"
    accepted = "accepted"
    en_route = "en_route"
    picked_up = "picked_up"
    completed = "completed"
    cancelled = "cancelled"
    deleted = "deleted"


class PaymentMethod(str, Enum):
    card = "card"
    wallet = "wallet"
    cash = "cash"
    upi = "upi"


class Vertical(str, Enum):
    restaurant = "restaurant"
    grocery = "grocery"
    pharmacy = "pharmacy"
    electronics = "electronics"
    fashion = "fashion"


class ContractTier(str, Enum):
    platinum = "platinum"
    gold = "gold"
    silver = "silver"
    launchpad = "launchpad"


class TripEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trip_id: str = Field(..., description="Primary entity identifier for a delivery trip")
    merchant_id: str
    merchant_name: str
    driver_id: str
    rider_id: str
    city: City
    service_tier: ServiceTier
    event_type: EventType
    status: str
    payment_method: PaymentMethod
    event_time_ms: int = Field(..., description="Event time in epoch milliseconds")
    event_day: str = Field(..., description="yyyy-mm-dd, pre-computed for low-latency filtering")
    event_hour: int = Field(..., ge=0, le=23)
    event_minute_bucket_ms: int = Field(..., description="Epoch milliseconds truncated to a 5-minute bucket")
    trip_partition: int = Field(..., ge=0, le=15)
    pickup_zone: str
    dropoff_zone: str
    pickup_h3: str
    dropoff_h3: str
    fare_amount: float
    distance_km: float
    eta_seconds: int
    surge_multiplier: float
    event_version: int = Field(..., ge=1)
    is_deleted: bool = False
    attributes: Dict[str, Any] = Field(default_factory=dict)


class TripState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trip_id: str
    merchant_id: str
    merchant_name: str
    driver_id: str
    rider_id: str
    city: City
    service_tier: ServiceTier
    status: str
    payment_method: PaymentMethod
    last_event_type: EventType
    last_event_time_ms: int
    last_event_day: str
    last_event_hour: int = Field(..., ge=0, le=23)
    last_event_minute_bucket_ms: int
    trip_partition: int = Field(..., ge=0, le=15)
    fare_amount: float
    distance_km: float
    eta_seconds: int
    surge_multiplier: float
    event_version: int = Field(..., ge=1)
    is_deleted: bool = False
    attributes: Dict[str, Any] = Field(default_factory=dict)


class Merchant(BaseModel):
    model_config = ConfigDict(extra="forbid")

    merchant_id: str
    merchant_name: str
    city: City
    vertical: Vertical
    contract_tier: ContractTier
    rating: float = Field(..., ge=0, le=5)
    is_active: bool = True
    monthly_orders: int = Field(..., ge=0)
    onboarding_date: str


class KPIResponse(BaseModel):
    city: Optional[City] = None
    window_minutes: int = 60
    completed_trips: int
    cancelled_trips: int
    gross_merchandise_value: float
    average_fare: float
    average_distance_km: float
    average_eta_seconds: float


class MerchantStats(BaseModel):
    merchant_id: str
    merchant_name: str
    city: City
    completed_trips: int
    revenue: float


class SQLRequest(BaseModel):
    query: str = Field(..., description="SQL text to run against Pinot or the in-memory demo provider")
    query_type: Literal["v1", "multistage"] = "v1"
    query_options: Optional[str] = Field(
        default=None,
        description="Semicolon separated Pinot queryOptions string, e.g. useMultistageEngine=true;timeoutMs=15000")


class TimeSeriesRequest(BaseModel):
    metric: Literal["gross_merchandise_value", "completed_trips", "avg_eta_seconds"] = "gross_merchandise_value"
    bucket_minutes: int = Field(default=60, ge=1, le=1440)
    city: Optional[City] = None
    window_hours: int = Field(default=24, ge=1, le=24 * 30)


class TimeSeriesPoint(BaseModel):
    bucket_start_ms: int
    value: float


class HealthResponse(BaseModel):
    mode: str
    pinot_available: bool
    generated_rows: int


class SQLResponse(BaseModel):
    mode: str
    query_type: str
    query: str
    result: Dict[str, Any]


class TimeSeriesResponse(BaseModel):
    mode: str
    metric: str
    points: List[TimeSeriesPoint]
