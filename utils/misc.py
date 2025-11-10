import json

def find_parking_session_id_by_plate(parking_lot_id: str, licenseplate="TEST-PLATE"):
    filename = f"./data/pdata/p{parking_lot_id}-sessions.json"
    with open(filename, "r") as f:
        parking_lots = json.load(f)

    for k, v in parking_lots.items():
        if v.get("licenseplate") == licenseplate:
            return k