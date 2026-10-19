"""
appointments.py — Doctor/Clinic Appointment Tracker.
Simple CRUD for upcoming and past appointments, scoped per patient
profile (reuses the same "{username}__{profile_id}" storage key
pattern as medicine.py and reminders).
Data is stored in data/{profile_key}_appointments.json
"""

import json
import os
import uuid
from datetime import datetime, date as date_cls
from typing import Optional


def _get_file(profile_key: str) -> str:
    os.makedirs("data", exist_ok=True)
    return f"data/{profile_key}_appointments.json"


def _load(profile_key: str) -> dict:
    path = _get_file(profile_key)
    if not os.path.exists(path):
        return {"appointments": {}}
    try:
        with open(path, "r") as f:
            data = json.load(f)
            if "appointments" not in data:
                data = {"appointments": {}}
            return data
    except (json.JSONDecodeError, FileNotFoundError):
        return {"appointments": {}}


def _save(profile_key: str, data: dict) -> None:
    """Atomic write: avoids a corrupted appointments file if the app
    is force-closed mid-save."""
    path = _get_file(profile_key)
    tmp_path = path + ".tmp"
    with open(tmp_path, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp_path, path)


# ── CRUD ─────────────────────────────────────────────────────────────────────

def add_appointment(
    profile_key: str, doctor: str, appt_date: str, appt_time: str, notes: str = "",
) -> tuple[bool, str]:
    doctor = doctor.strip()
    if not doctor:
        return False, "Doctor/clinic name cannot be empty."
    if not appt_date:
        return False, "Date is required."

    data = _load(profile_key)
    appt_id = str(uuid.uuid4())[:8]
    data["appointments"][appt_id] = {
        "id": appt_id,
        "doctor": doctor,
        "date": appt_date,
        "time": appt_time or "09:00",
        "notes": notes.strip(),
        "created_at": datetime.now().isoformat(),
    }
    _save(profile_key, data)
    return True, f"✅ Appointment with {doctor} added."


def update_appointment(
    profile_key: str, appt_id: str, doctor: str, appt_date: str, appt_time: str, notes: str = "",
) -> tuple[bool, str]:
    data = _load(profile_key)
    if appt_id not in data["appointments"]:
        return False, "Appointment not found."

    doctor = doctor.strip()
    if not doctor:
        return False, "Doctor/clinic name cannot be empty."

    data["appointments"][appt_id].update({
        "doctor": doctor,
        "date": appt_date,
        "time": appt_time or "09:00",
        "notes": notes.strip(),
        "updated_at": datetime.now().isoformat(),
    })
    _save(profile_key, data)
    return True, f"✅ Appointment with {doctor} updated."


def delete_appointment(profile_key: str, appt_id: str) -> tuple[bool, str]:
    data = _load(profile_key)
    if appt_id not in data["appointments"]:
        return False, "Appointment not found."
    doctor = data["appointments"][appt_id]["doctor"]
    del data["appointments"][appt_id]
    _save(profile_key, data)
    return True, f"🗑️ Appointment with {doctor} removed."


def get_all_appointments(profile_key: str) -> dict:
    return _load(profile_key)["appointments"]


def _sort_key(appt: dict):
    return f"{appt['date']} {appt['time']}"


def get_upcoming_appointments(profile_key: str) -> list[dict]:
    """Appointments today or in the future, soonest first."""
    now = datetime.now()
    all_appts = get_all_appointments(profile_key).values()
    upcoming = [
        a for a in all_appts
        if datetime.strptime(f"{a['date']} {a['time']}", "%Y-%m-%d %H:%M") >= now
    ]
    return sorted(upcoming, key=_sort_key)


def get_past_appointments(profile_key: str) -> list[dict]:
    """Appointments that have already passed, most recent first."""
    now = datetime.now()
    all_appts = get_all_appointments(profile_key).values()
    past = [
        a for a in all_appts
        if datetime.strptime(f"{a['date']} {a['time']}", "%Y-%m-%d %H:%M") < now
    ]
    return sorted(past, key=_sort_key, reverse=True)


def get_next_appointment(profile_key: str) -> Optional[dict]:
    upcoming = get_upcoming_appointments(profile_key)
    return upcoming[0] if upcoming else None
