from __future__ import annotations

import json
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

from pinot_playbook_demo.models import (
    HealthResponse,
    KPIResponse,
    MerchantStats,
    SQLRequest,
    SQLResponse,
    TimeSeriesRequest,
    TimeSeriesResponse,
    TripState)
from pinot_playbook_demo.service import AnalyticsProvider, build_provider

app = FastAPI(
    title="Apache Pinot playbook Demo API",
    version="0.1.0",
    description=(
        "A small API that fronts the sample Pinot demo tables. "
        "In auto mode it talks to Pinot when available and falls back to a deterministic in-memory provider otherwise."
    ))


def get_provider() -> AnalyticsProvider:
    return build_provider()


@app.get("/health", response_model=HealthResponse, tags=["meta"])
def health(provider: AnalyticsProvider = Depends(get_provider)) -> HealthResponse:
    return HealthResponse(**provider.health())


@app.get("/api/v1/kpis", response_model=KPIResponse, tags=["analytics"])
def get_kpis(
    city: Optional[str] = Query(default=None),
    window_minutes: int = Query(default=60, ge=1, le=60 * 24 * 7),
    provider: AnalyticsProvider = Depends(get_provider)) -> KPIResponse:
    return provider.get_kpis(city=city, window_minutes=window_minutes)


@app.get("/api/v1/top-merchants", response_model=List[MerchantStats], tags=["analytics"])
def top_merchants(
    city: Optional[str] = Query(default=None),
    limit: int = Query(default=10, ge=1, le=100),
    provider: AnalyticsProvider = Depends(get_provider)) -> List[MerchantStats]:
    return provider.top_merchants(city=city, limit=limit)


@app.get("/api/v1/trips/{trip_id}", response_model=TripState, tags=["analytics"])
def get_trip(trip_id: str, provider: AnalyticsProvider = Depends(get_provider)) -> TripState:
    trip = provider.get_trip(trip_id)
    if not trip or trip.get("is_deleted"):
        raise HTTPException(status_code=404, detail=f"Trip {trip_id} not found")
    # Pinot stores attributes as a JSON string, parse it back to dict
    if isinstance(trip.get("attributes"), str):
        trip["attributes"] = json.loads(trip["attributes"])
    return TripState(**trip)


@app.post("/api/v1/query/sql", response_model=SQLResponse, tags=["query"])
def query_sql(request: SQLRequest, provider: AnalyticsProvider = Depends(get_provider)) -> SQLResponse:
    result = provider.sql(request)
    return SQLResponse(mode=provider.mode, query_type=request.query_type, query=request.query, result=result)


@app.post("/api/v1/query/timeseries", response_model=TimeSeriesResponse, tags=["query"])
def query_timeseries(request: TimeSeriesRequest, provider: AnalyticsProvider = Depends(get_provider)) -> TimeSeriesResponse:
    points = provider.timeseries(request)
    return TimeSeriesResponse(mode=provider.mode, metric=request.metric, points=points)


@app.exception_handler(RuntimeError)
def runtime_error_handler(_: object, exc: RuntimeError) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": str(exc)})
