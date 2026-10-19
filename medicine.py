"""
medicine.py - Medicine management, scheduling, and rule-based AI warnings
Handles add/edit/delete medicines, dose marking, and missed dose tracking.
Data is stored per-user in data/{username}_medicines.json
"""

import json
import os
from datetime import datetime, date, timedelta
from typing import Optional
import uuid

FREQUENCY_MAX_DOSES = {
    "Once daily": 1,
    "Twice daily": 2,
    "Three times daily": 3,
    "Four times daily": 4,
    "Every 6 hours": 4,
    "Every 8 hours": 3,
    "Every 12 hours": 2,
    "As needed": 6,
    "Weekly": 1,
}

OVERDOSE_THRESHOLD = {
    "Once daily": 1,
    "Twice daily": 2,
    "Three times daily": 3,
    "Four times daily": 4,
    "Every 6 hours": 4,
    "Every 8 hours": 3,
    "Every 12 hours": 2,
    "As needed": 6,
    "Weekly": 1,
}


def _get_file(username: str) -> str:
    os.makedirs("data", exist_ok=True)
    return f"data/{username}_medicines.json"


def _load(username: str) -> dict:
    path = _get_file(username)
    if not os.path.exists(path):
        return {"medicines": {}, "dose_log": {}}
    try:
        with open(path, "r") as f:
            data = json.load(f)
            # Migrate old format if needed
            if "medicines" not in data:
                data = {"medicines": data, "dose_log": {}}
            if "dose_log" not in data:
                data["dose_log"] = {}
            return data
    except (json.JSONDecodeError, FileNotFoundError):
        return {"medicines": {}, "dose_log": {}}


def _save(username: str, data: dict) -> None:
    """Atomic write: avoids a corrupted medicines file if the app is
    force-closed mid-save."""
    path = _get_file(username)
    tmp_path = path + ".tmp"
    with open(tmp_path, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp_path, path)


# ── AI Rule Engine ──────────────────────────────────────────────────────────

def check_duplicate(username: str, medicine_name: str, exclude_id: str = "") -> bool:
    """Return True if a medicine with this name already exists."""
    data = _load(username)
    name_lower = medicine_name.strip().lower()
    for mid, med in data["medicines"].items():
        if mid == exclude_id:
            continue
        if med["name"].lower() == name_lower:
            return True
    return False


def check_overdose_risk(frequency: str, dosage: str) -> Optional[str]:
    """
    Rule-based overdose detection.
    Returns a warning string if risk detected, else None.
    """
    try:
        dose_value = float("".join(c for c in dosage if c.isdigit() or c == "."))
    except ValueError:
        dose_value = 0

    # Flag very high dosage numbers (>1000 of any unit)
    if dose_value > 1000:
        return (
            f"⚠️ High dosage detected: {dosage}. "
            "Please verify with your healthcare provider."
        )

    max_doses = OVERDOSE_THRESHOLD.get(frequency, 4)
    daily_total = dose_value * max_doses
    if daily_total > 4000:  # General threshold, e.g., paracetamol limit
        return (
            f"⚠️ Potential overdose risk: {dosage} × {max_doses} doses/day "
            f"= {daily_total:.0f} total. Maximum recommended daily intake "
            "is typically 4000mg. Consult your doctor."
        )
    return None


# ── CRUD Operations ─────────────────────────────────────────────────────────

def add_medicine(
    username: str,
    name: str,
    dosage: str,
    frequency: str,
    times: list[str],
    notes: str = "",
    start_date: str = "",
    end_date: str = "",
    stock_quantity: Optional[int] = None,
) -> tuple[bool, str]:
    """Add a new medicine. Returns (success, message)."""
    name = name.strip()
    if not name:
        return False, "Medicine name cannot be empty."
    if not dosage.strip():
        return False, "Dosage cannot be empty."
    if not times:
        return False, "At least one dose time is required."

    warnings = []
    if check_duplicate(username, name):
        warnings.append(
            f"⚠️ Duplicate warning: '{name}' already exists in your list."
        )

    overdose_warn = check_overdose_risk(frequency, dosage)
    if overdose_warn:
        warnings.append(overdose_warn)

    data = _load(username)
    med_id = str(uuid.uuid4())[:8]
    data["medicines"][med_id] = {
        "id": med_id,
        "name": name,
        "dosage": dosage.strip(),
        "frequency": frequency,
        "times": times,
        "notes": notes.strip(),
        "start_date": start_date or date.today().isoformat(),
        "end_date": end_date,
        "active": True,
        "stock_quantity": stock_quantity,
        "created_at": datetime.now().isoformat(),
    }
    _save(username, data)

    msg = f"✅ '{name}' added successfully."
    if warnings:
        msg += "\n\n" + "\n".join(warnings)
    return True, msg


def update_medicine(
    username: str,
    med_id: str,
    name: str,
    dosage: str,
    frequency: str,
    times: list[str],
    notes: str = "",
    start_date: str = "",
    end_date: str = "",
    stock_quantity: Optional[int] = None,
) -> tuple[bool, str]:
    """Update an existing medicine."""
    data = _load(username)
    if med_id not in data["medicines"]:
        return False, "Medicine not found."

    name = name.strip()
    warnings = []
    if check_duplicate(username, name, exclude_id=med_id):
        warnings.append(f"⚠️ Another medicine named '{name}' already exists.")

    overdose_warn = check_overdose_risk(frequency, dosage)
    if overdose_warn:
        warnings.append(overdose_warn)

    data["medicines"][med_id].update({
        "name": name,
        "dosage": dosage.strip(),
        "frequency": frequency,
        "times": times,
        "notes": notes.strip(),
        "start_date": start_date,
        "end_date": end_date,
        "stock_quantity": stock_quantity,
        "updated_at": datetime.now().isoformat(),
    })
    _save(username, data)

    msg = f"✅ '{name}' updated successfully."
    if warnings:
        msg += "\n\n" + "\n".join(warnings)
    return True, msg


def delete_medicine(username: str, med_id: str) -> tuple[bool, str]:
    data = _load(username)
    if med_id not in data["medicines"]:
        return False, "Medicine not found."
    name = data["medicines"][med_id]["name"]
    del data["medicines"][med_id]
    _save(username, data)
    return True, f"🗑️ '{name}' deleted."


def get_all_medicines(username: str) -> dict:
    data = _load(username)
    return data["medicines"]


def get_active_medicines(username: str) -> dict:
    return {
        mid: med
        for mid, med in get_all_medicines(username).items()
        if med.get("active", True)
    }


# ── Dose Tracking ────────────────────────────────────────────────────────────

def _dose_key(med_id: str, dose_time: str, day: str) -> str:
    return f"{med_id}|{dose_time}|{day}"


def mark_dose(username: str, med_id: str, dose_time: str, taken: bool) -> None:
    """Record a dose as taken or untaken for today. Adjusts stock if tracked."""
    data = _load(username)
    today = date.today().isoformat()
    key = _dose_key(med_id, dose_time, today)
    previous = data["dose_log"].get(key)
    was_taken = previous.get("taken") if previous else None

    data["dose_log"][key] = {
        "taken": taken,
        "timestamp": datetime.now().isoformat() if taken else None,
    }

    med = data["medicines"].get(med_id)
    if med is not None and med.get("stock_quantity") is not None:
        if taken and was_taken is not True:
            med["stock_quantity"] = max(0, med["stock_quantity"] - 1)
        elif not taken and was_taken is True:
            med["stock_quantity"] = med["stock_quantity"] + 1

    _save(username, data)


def restock_medicine(username: str, med_id: str, add_amount: int) -> tuple[bool, str]:
    """Add units to a medicine's tracked stock (e.g. after refilling)."""
    data = _load(username)
    if med_id not in data["medicines"]:
        return False, "Medicine not found."
    med = data["medicines"][med_id]
    current = med.get("stock_quantity") or 0
    med["stock_quantity"] = current + add_amount
    _save(username, data)
    return True, f"✅ '{med['name']}' restocked — now {med['stock_quantity']} units."


def get_dose_status(username: str, med_id: str, dose_time: str, day: str = "") -> Optional[bool]:
    """Return True/False/None for a dose (None = not recorded yet)."""
    data = _load(username)
    day = day or date.today().isoformat()
    key = _dose_key(med_id, dose_time, day)
    entry = data["dose_log"].get(key)
    if entry is None:
        return None
    return entry.get("taken")


# ── Today's Schedule ─────────────────────────────────────────────────────────

def get_today_schedule(username: str) -> list[dict]:
    """
    Return a flat list of all dose slots for today, each with status.
    """
    medicines = get_active_medicines(username)
    today_str = date.today().isoformat()
    schedule = []

    for med_id, med in medicines.items():
        # Skip if outside active date range
        if med.get("start_date") and today_str < med["start_date"]:
            continue
        if med.get("end_date") and today_str > med["end_date"]:
            continue

        for t in med.get("times", []):
            status = get_dose_status(username, med_id, t, today_str)
            is_missed = _is_missed(t, status)
            schedule.append({
                "med_id": med_id,
                "name": med["name"],
                "dosage": med["dosage"],
                "frequency": med["frequency"],
                "time": t,
                "taken": status,
                "missed": is_missed,
                "notes": med.get("notes", ""),
            })

    # Sort by time
    def time_sort_key(item):
        try:
            return datetime.strptime(item["time"], "%H:%M")
        except ValueError:
            return datetime.min

    schedule.sort(key=time_sort_key)
    return schedule


def _is_missed(dose_time_str: str, status: Optional[bool]) -> bool:
    """A dose is 'missed' if it was scheduled before now and not marked taken."""
    if status is True:
        return False
    try:
        dose_dt = datetime.strptime(dose_time_str, "%H:%M").replace(
            year=date.today().year,
            month=date.today().month,
            day=date.today().day,
        )
        return datetime.now() > dose_dt + timedelta(minutes=30)
    except ValueError:
        return False


# ── Analytics ────────────────────────────────────────────────────────────────

def get_weekly_adherence(username: str) -> dict:
    """
    Return per-day adherence stats for the past 7 days.
    Result: { "YYYY-MM-DD": {"taken": int, "missed": int, "pending": int} }
    """
    data = _load(username)
    medicines = get_active_medicines(username)
    result = {}

    for i in range(6, -1, -1):
        day = (date.today() - timedelta(days=i)).isoformat()
        taken = missed = pending = 0

        for med_id, med in medicines.items():
            if med.get("start_date") and day < med["start_date"]:
                continue
            if med.get("end_date") and day > med["end_date"]:
                continue

            for t in med.get("times", []):
                key = _dose_key(med_id, t, day)
                entry = data["dose_log"].get(key)
                if entry is None:
                    # Past days with no entry = missed; today = pending
                    if day < date.today().isoformat():
                        missed += 1
                    else:
                        pending += 1
                elif entry.get("taken"):
                    taken += 1
                else:
                    missed += 1

        result[day] = {"taken": taken, "missed": missed, "pending": pending}

    return result


def get_medicine_stats(username: str) -> dict:
    """Overall statistics for the medicine list."""
    medicines = get_active_medicines(username)
    schedule = get_today_schedule(username)

    total = len(schedule)
    taken = sum(1 for s in schedule if s["taken"] is True)
    missed = sum(1 for s in schedule if s["missed"])
    pending = total - taken - missed

    return {
        "total_medicines": len(medicines),
        "today_total": total,
        "today_taken": taken,
        "today_missed": missed,
        "today_pending": pending,
        "adherence_pct": round((taken / total * 100) if total > 0 else 0, 1),
    }


def get_low_stock(username: str, days_threshold: int = 5) -> list[dict]:
    """
    Return active medicines whose tracked stock is running low — either
    at/near zero, or projected to run out within `days_threshold` days
    based on how many doses are taken per day.
    Medicines with stock_quantity left as None (not tracked) are skipped.
    """
    medicines = get_active_medicines(username)
    low = []

    for med_id, med in medicines.items():
        stock = med.get("stock_quantity")
        if stock is None:
            continue

        doses_per_day = max(1, len(med.get("times", [])))
        days_remaining = stock / doses_per_day if doses_per_day else None

        if stock <= 0 or (days_remaining is not None and days_remaining <= days_threshold):
            low.append({
                "med_id": med_id,
                "name": med["name"],
                "dosage": med["dosage"],
                "stock_quantity": stock,
                "doses_per_day": doses_per_day,
                "days_remaining": round(days_remaining, 1) if days_remaining is not None else None,
            })

    low.sort(key=lambda m: (m["days_remaining"] is None, m["days_remaining"] or 0))
    return low
