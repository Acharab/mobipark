from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class Coordinates(BaseModel):
    lat: float
    lng: float

class ParkingLot(BaseModel):
    name: str
    location: str
    address: str
    capacity: int
    reserved: int
    tariff: float
    daytariff: float
    created_at: str
    coordinates: Coordinates

class UpdateParkingLot(BaseModel):
    name: Optional[str]
    location: Optional[str]
    address: Optional[str]
    capacity: Optional[int]
    reserved: Optional[int]
    tariff: Optional[float]
    daytariff: Optional[float]
    created_at: Optional[str]
    coordinates: Optional[Coordinates]

class ParkingSessionCreate(BaseModel):
    licenseplate: str

class OngoingParkingSession(BaseModel):
    licenseplate: str
    started: str
    stopped: str
    user: str

class FinishedParkingSession(BaseModel):
    licenseplate: str
    started: str
    stopped: str
    user: str
    duration_minutes: int
    cost: float
    payment_status: str