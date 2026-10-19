"""
profiles.py - Multiple Patient / Family Profile management
Lets one user account manage medicines for several people
(e.g. self, parent, child). Each profile gets its own medicine
data, scoped via a profile key of the form "{username}__{profile_id}"
that is passed straight into medicine.py's existing storage functions
(medicine.py only ever uses that string as an opaque file key, so no
changes to medicine.py are required).
Data is stored per-user in data/{username}_profiles.json
"""

import json
import os
import uuid
from datetime import datetime
from typing import Optional

RELATIONS = [
    "Self", "Father", "Mother", "Spouse", "Son", "Daughter",
    "Grandfather", "Grandmother", "Brother", "Sister", "Other",
]


def _get_file(username: str) -> str:
    os.makedirs("data", exist_ok=True)
    return f"data/{username}_profiles.json"


def _load(username: str) -> dict:
    path = _get_file(username)
    if not os.path.exists(path):
        return {"profiles": {}}
    try:
        with open(path, "r") as f:
            data = json.load(f)
            if "profiles" not in data:
                data = {"profiles": {}}
            return data
    except (json.JSONDecodeError, FileNotFoundError):
        return {"profiles": {}}


def _save(username: str, data: dict) -> None:
    """Atomic write: avoids a corrupted profiles file if the app is
    force-closed mid-save."""
    path = _get_file(username)
    tmp_path = path + ".tmp"
    with open(tmp_path, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp_path, path)


def profile_key(username: str, profile_id: str) -> str:
    """Storage key passed into medicine.py - one JSON file per profile."""
    return f"{username}__{profile_id}"


# ── CRUD ─────────────────────────────────────────────────────────────────────

def create_profile(
    username: str,
    name: str,
    relation: str = "Self",
    age: str = "",
    gender: str = "",
) -> tuple[bool, str, Optional[str]]:
    """Add a new patient/family profile. Returns (success, message, profile_id)."""
    name = name.strip()
    if not name:
        return False, "Profile name cannot be empty.", None

    data = _load(username)
    for pid, prof in data["profiles"].items():
        if prof["name"].strip().lower() == name.lower():
            return False, f"A profile named '{name}' already exists.", None

    profile_id = str(uuid.uuid4())[:8]
    data["profiles"][profile_id] = {
        "id": profile_id,
        "name": name,
        "relation": relation,
        "age": age,
        "gender": gender,
        "created_at": datetime.now().isoformat(),
    }
    _save(username, data)
    return True, f"✅ Profile '{name}' added.", profile_id


def update_profile(
    username: str,
    profile_id: str,
    name: str,
    relation: str,
    age: str = "",
    gender: str = "",
) -> tuple[bool, str]:
    data = _load(username)
    if profile_id not in data["profiles"]:
        return False, "Profile not found."

    name = name.strip()
    if not name:
        return False, "Profile name cannot be empty."

    data["profiles"][profile_id].update({
        "name": name,
        "relation": relation,
        "age": age,
        "gender": gender,
        "updated_at": datetime.now().isoformat(),
    })
    _save(username, data)
    return True, f"✅ Profile '{name}' updated."


def delete_profile(username: str, profile_id: str) -> tuple[bool, str]:
    data = _load(username)
    if profile_id not in data["profiles"]:
        return False, "Profile not found."
    if len(data["profiles"]) <= 1:
        return False, "You must keep at least one profile."

    name = data["profiles"][profile_id]["name"]
    del data["profiles"][profile_id]
    _save(username, data)

    # Also remove that profile's medicine data file, if any.
    med_file = f"data/{profile_key(username, profile_id)}_medicines.json"
    if os.path.exists(med_file):
        os.remove(med_file)

    return True, f"🗑️ Profile '{name}' deleted."


def list_profiles(username: str) -> dict:
    return _load(username)["profiles"]


def get_profile(username: str, profile_id: str) -> Optional[dict]:
    return _load(username)["profiles"].get(profile_id)


def ensure_default_profile(username: str) -> str:
    """
    Guarantee the user has at least one profile (auto-create a 'Self'
    profile on first login). Returns a valid profile_id to make active.
    """
    profiles = list_profiles(username)
    if profiles:
        return next(iter(profiles))

    ok, _, profile_id = create_profile(username, name=username.title(), relation="Self")
    return profile_id
