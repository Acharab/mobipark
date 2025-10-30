from datetime import datetime
from typing import Dict

from fastapi import HTTPException, status, Depends
from fastapi.encoders import jsonable_encoder

from models.parking_lots_model import ParkingLot, ParkingSessionCreate
from services import auth_services
from utils import storage_utils

def create_parking_lot(parking_lot: ParkingLot, session_user: Dict[str, str] = Depends(auth_services.require_auth)):
    # TODO: Validate parking lots
    parking_lots = storage_utils.load_parking_lot_data()

    new_id = None
    if parking_lots:
        new_id = str(max(int(k) for k in parking_lots.keys()) + 1)
    else: new_id = "1"

    parking_lot_entry = {
        "name": parking_lot.name,
        "location": parking_lot.location,
        "address": parking_lot.address,
        "capacity": parking_lot.capacity,
        "reserved": parking_lot.reserved,
        "tariff": parking_lot.tariff,
        "daytariff": parking_lot.daytariff,
        "created_at": parking_lot.created_at,
        "coordinates": {
            parking_lot.coordinates.lat,
            parking_lot.coordinates.lng
        }
    }

    try:
        parking_lots[new_id] = parking_lot_entry
        storage_utils.save_parking_lot_data(parking_lots)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save parking lot"
        )
    
    return parking_lots[new_id]

def update_parking_lot(parking_lot_id: str, parking_lot_data: ParkingLot):
    parking_lots = storage_utils.load_parking_lot_data()
    if parking_lot_id not in parking_lots:
        raise HTTPException(404, "Parking lot not found")
    
    updated_lot_encoded = jsonable_encoder(parking_lot_data)
    parking_lots[parking_lot_id].update(updated_lot_encoded)
    
    try:
        storage_utils.save_parking_lot_data(parking_lots)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update parking lot"
        )
    
    return parking_lots[parking_lot_id]

def start_parking_session(
    parking_lot_id: str,
    session_data: ParkingSessionCreate,
    session_user: Dict[str, str] = Depends(auth_services.require_auth)
    ):
    parking_sessions = storage_utils.load_parking_session_data(parking_lot_id)
    new_id = None
    if parking_sessions:
        new_id = str(max(int(k) for k in parking_sessions.keys()) + 1)
    else: new_id = "1"

    parking_session_entry = {
        "licenseplate": session_data.licenseplate,
        "started": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "stopped": None,
        "user": session_user.get("username")
    }

    try:
        parking_sessions[new_id] = parking_session_entry
        storage_utils.save_parking_session_data(parking_sessions, parking_lot_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save parking session"
        )
    
    return parking_sessions[new_id]
