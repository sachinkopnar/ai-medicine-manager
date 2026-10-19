"""
reminders.py — Dosage reminder helpers.
Builds on medicine.py's existing today's-schedule data to work out which
doses need an alert right now, so the UI can show an on-screen "Due Now"
banner and fire browser desktop notifications.
"""

from datetime import datetime
from typing import Optional


def get_due_now(schedule: list[dict], window_minutes: int = 15) -> list[dict]:
    """
    From today's schedule (as returned by medicine.get_today_schedule),
    return dose slots that need an alert right now: either coming up
    within `window_minutes`, or already past due and not yet taken.
    Doses already marked taken are excluded.
    """
    now = datetime.now()
    due = []

    for slot in schedule:
        if slot.get("taken") is True:
            continue
        try:
            dose_dt = datetime.strptime(slot["time"], "%H:%M").replace(
                year=now.year, month=now.month, day=now.day
            )
        except (ValueError, KeyError):
            continue

        minutes_until = (dose_dt - now).total_seconds() / 60

        # Alert window: from `window_minutes` before the dose time,
        # through the rest of the day if it's overdue and still unmarked.
        if minutes_until <= window_minutes:
            due.append({
                "med_id": slot["med_id"],
                "name": slot["name"],
                "dosage": slot["dosage"],
                "time": slot["time"],
                "minutes_until": round(minutes_until),
                "overdue": minutes_until < 0,
            })

    due.sort(key=lambda s: s["minutes_until"])
    return due
