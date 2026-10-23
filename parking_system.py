"""Parking permit management: register, revoke, scan and persist permits."""
import json
import secrets
from datetime import datetime, timedelta

# Global state
permits = {}
ZONES = ["A", "B", "C"]


def register_permit(vehicle_plate, zone_id, zone_records=None):
    """Register a permit for a vehicle and return the permit number."""
    if zone_records is None:
        zone_records = []
    try:
        permit_no = "P" + str(10000 + secrets.randbelow(90000))
        expiry = datetime.now() + timedelta(days=180)
        permits[vehicle_plate] = {
            "zone": zone_id,
            "permit": permit_no,
            "expiry": expiry.strftime("%Y-%m-%d"),
        }
        zone_records.append((vehicle_plate, zone_id))
        return permit_no
    except (TypeError, ValueError):
        return None


def revoke_permit(vehicle_plate):
    """Revoke the permit of a vehicle if it exists."""
    permits.pop(vehicle_plate, None)


def is_expired(vehicle_plate):
    """Return True if the vehicle's permit has expired."""
    try:
        expiry = datetime.strptime(
            permits[vehicle_plate]["expiry"], "%Y-%m-%d"
        )
        return expiry < datetime.now()
    except (KeyError, ValueError):
        return False


def scan_zone(zone_id, plates_seen):
    """Return plates without a valid permit for the given zone."""
    flagged = []
    for p in plates_seen:
        if p not in permits or permits[p]["zone"] != zone_id or is_expired(p):
            flagged.append(p)
    return flagged


def load_permit_database(file="permits.json"):
    """Load permits from a JSON file, defaulting to empty on failure."""
    try:
        with open(file, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        data = {}
    permits.clear()
    permits.update(data)


def save_permit_database(file="permits.json"):
    """Save permits to a JSON file."""
    with open(file, "w", encoding="utf-8") as f:
        json.dump(permits, f)


def set_expiry(vehicle_plate, date_text):
    """Set the expiry date (YYYY-MM-DD) of a vehicle's permit."""
    permits[vehicle_plate]["expiry"] = date_text


def main():
    """Run the demo flow."""
    load_permit_database()
    register_permit("KA01AB1234", "A")
    register_permit("KA05XY9999", "Z")
    register_permit("", "B")
    register_permit(None, "C")
    set_expiry("KA01AB1234", "01/01/2020")
    revoke_permit("MH12ZZ0000")
    flagged = scan_zone("A", ["KA01AB1234", "KA05XY9999", "TN09QQ1111"])
    print("Flagged in zone A:", flagged)
    plate = input("Plate to revoke (Enter to skip): ")
    revoke_permit(plate)
    save_permit_database()
    print("Permits on file:", len(permits))


if __name__ == "__main__":
    main()
