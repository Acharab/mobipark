from datetime import datetime
from typing import Dict

from fastapi import APIRouter, Request, HTTPException, Depends, status, Header
from fastapi.responses import JSONResponse
from models.parking_lots_model import ParkingLot, Coordinates, ParkingSessionCreate

from services import parking_services, auth_services
from utils.storage_utils import (
    save_parking_lot_data,
    load_parking_lot_data,
    save_parking_session_data,
    load_parking_session_data
)

router = APIRouter(
    tags=["parking-lots"],
    responses={
        401: {"description": "Unauthorized - Invalid or missing token"},
        403: {"description": "Forbidden - Insufficient permissions"},
        404: {"description": "Not Found - Resource does not exist"}
    }
)

@router.get(
    "/parking-lots/{parking_lot_id}",
    summary="Retrieve a single parking lot by ID",
    response_description="Parking lot details"
)
def get_parking_lot_by_id(parking_lot_id: str):
    parking_lots = load_parking_lot_data()
    return parking_lots[parking_lot_id]

@router.get(
    "/parking-lots/",
    summary="Retrieve all current parking lots",
    response_description="Parking lot details"
)
def get_parking_lots():
    parking_lots = load_parking_lot_data()
    return parking_lots

@router.get(
    "/parking-lots/{parking_lot_id}/sessions",
    summary="Retrieve session(s) in a specific parking lot",
    response_description="Parking session details"
)
def get_parking_sessions(parking_lot_id: str, session_user: Dict[str, str] = Depends(auth_services.require_auth)):
    parking_sessions = load_parking_session_data(parking_lot_id)
    sessions_to_display = []

    # TODO: validate parking lots
    if session_user.get("role") != "ADMIN":
        for k, v in parking_sessions.items():
            if v["user"] == session_user.get("username"):
                sessions_to_display.append((k, v))
        return sessions_to_display
    else:
        return parking_sessions
    
@router.post(
    "/parking-lots/",
    summary="Create new parking lot",
    response_description="Parking lot creation"
)
def create_parking_lot(parking_lot: ParkingLot, session_user: Dict[str, str] = Depends(auth_services.require_auth)):
    auth_services.verify_admin(session_user)
    new_lot = parking_services.create_parking_lot(parking_lot, session_user)

    return JSONResponse(
        content=new_lot,
        status_code=status.HTTP_200_OK
    )

@router.post(
    "/parking-lots/sessions/{parking_lot_id}/start"
)
def start_parking_session(
    parking_lot_id: str,
    session_data: ParkingSessionCreate,
    session_user: Dict[str, str] = Depends(auth_services.require_auth)):
    started_session = parking_services.start_parking_session(parking_lot_id, session_data, session_user)

    return JSONResponse(
    content=started_session,
    status_code=status.HTTP_200_OK
    )


@router.put(
    "/parking-lots/sessions/{parking_lot_id}/stop"
)
def stop_parking_session(
    parking_lot_id: str,
    session_data: ParkingSessionCreate,
    session_user: Dict[str, str] = Depends(auth_services.require_auth)):

    # TODO: Add parking lot ID
    # TODO: Check for valid token
    # TODO: Calculate cost of session
    # TODO: Update payment status
    
    updated_parking_session_entry = None
    parking_sessions = load_parking_session_data(parking_lot_id)
    for key, session in parking_sessions.items():
        if session["licenseplate"] == session_data.licenseplate:

            if session["user"] != session_user.get("username") and session_user.get("role") != "ADMIN":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unauthorized - invalid or missing session token"
                )

            start_time = datetime.strptime(session["started"], "%d-%m-%Y %H:%M:%S")
            stop_time = datetime.now()
            duration = stop_time - start_time
            # Check if duration in minutes should be rounded up or down
            duration_minutes = int(duration.total_seconds() / 60)

            updated_parking_session_entry = {
                "licenseplate": session_data.licenseplate,
                "started": session["started"],
                "stopped": stop_time.strftime("%d-%m-%Y %H:%M:%S"),
                "user": session["user"],
                "duration_minutes": duration_minutes,
                # Cost should be calculated using calculate_price from session_calculator.py
                "cost": 0,
                # Payment status should be updated through Payment endpoint (probably)
                "payment_status": "Pending"
            }
            parking_sessions[key] = updated_parking_session_entry
            break
    if updated_parking_session_entry == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Found - Resource does not exist"
        )

    try:
        save_parking_session_data(parking_sessions, parking_lot_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update parking session"
        )
    
    return JSONResponse(
    content=updated_parking_session_entry,
    status_code=status.HTTP_200_OK
    )

@router.put(
    "/parking-lots/{parking_lot_id}",
    summary="Update parking lot entry data",
    response_description="Update parking lot"
)
def update_parking_lot(
    parking_lot_id: str,
    parking_lot_data: ParkingLot,
    session_user: Dict[str, str] = Depends(auth_services.require_auth)
):
    auth_services.verify_admin(session_user)
    updated_lot = parking_services.update_parking_lot(parking_lot_id, parking_lot_data)

    return JSONResponse(
        content=updated_lot,
        status_code=status.HTTP_200_OK
    )