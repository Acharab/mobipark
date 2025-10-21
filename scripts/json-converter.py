import json
from pathlib import Path


OLD_FILE = Path("data/vehicles.json")
BACKUP_FILE = Path("data/vehicles_backup.json")
NEW_FILE = Path("data/vehicles_converted.json")


def convert_vehicle_data():
    if not OLD_FILE.exists():
        print("Error: data/vehicles.json not found")
        return
    print(f"Backup saved as {BACKUP_FILE}")
    with open(OLD_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        print("File already in new format, no conversion needed")
        return
    new_format = {}
    for v in data:
        username = f"user_{v['user_id']}"
        lid = v["license_plate"].replace("-", "")
        if username not in new_format:
            new_format[username] = {}
        new_format[username][lid] = {
            "license_plate": v["license_plate"],
            "name": f"{v.get('make', '')} {v.get('model', '')}".strip(),
            "created_at": v["created_at"],
            "updated_at": v["updated_at"],
        }
    with open(NEW_FILE, "w", encoding="utf-8") as f:
        json.dump(new_format, f, indent=4)
    print(f"converted {len(data)} vehicles into grouped format")
    print(f"new file saves as: {NEW_FILE}")
    print(f"original file backed up as: {BACKUP_FILE}")


if __name__ == "__main__":
    convert_vehicle_data()
