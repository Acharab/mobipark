from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class Coordinates(BaseModel):
    lat: float
    lng: float

class UpdateCoordinates(BaseModel):
    lat: Optional[float] = None
    lng: Optional[float] = None

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
    name: Optional[str] = None
    location: Optional[str] = None
    address: Optional[str] = None
    capacity: Optional[int] = None
    reserved: Optional[int] = None
    tariff: Optional[float] = None
    daytariff: Optional[float] = None
    created_at: Optional[str] = None
    coordinates: Optional[Coordinates] = None

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