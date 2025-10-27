from pydantic import BaseModel
from datetime import date

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
    created_at: date
    coordinates: Coordinates