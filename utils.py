"""
utils.py - Shared utilities for AI Medicine Manager
Matplotlib chart generators, formatting helpers, and Streamlit UI helpers.
Charts now honour the current light/dark theme via get_chart_colors().
"""

from datetime import datetime, date
from typing import Optional
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker
import pandas as pd
import io

# Fallback colours (dark) used when theme.py is not yet imported
_DEFAULT_COLORS = {
    "taken":   "#22c55e",
    "missed":  "#ef4444",
    "pending": "#f59e0b",
    "primary": "#3b82f6",
    "bg":      "#1e293b",
    "surface": "#334155",
    "text":    "#f1f5f9",
}

COLORS = _DEFAULT_COLORS   # kept for backward compatibility


def _c() -> dict:
    """Return chart colours for the active theme (with fallback)."""
    try:
        from theme import get_chart_colors
        return get_chart_colors()
    except Exception:
        return _DEFAULT_COLORS


# ── Chart Generators ──────────────────────────────────────────────────────────

def make_weekly_adherence_chart(weekly_data: dict) -> bytes:
    c = _c()
    days   = list(weekly_data.keys())
    taken  = [weekly_data[d]["taken"]   for d in days]
    missed = [weekly_data[d]["missed"]  for d in days]
    pending= [weekly_data[d]["pending"] for d in days]

    labels = [_short_date(d) for d in days]
    x      = range(len(days))
    width  = 0.28

    fig, ax = plt.subplots(figsize=(10, 4.5))
    fig.patch.set_facecolor(c["bg"])
    ax.set_facecolor(c["surface"])

    bars_t = ax.bar([i - width for i in x], taken,   width, label="Taken",   color=c["taken"],   alpha=0.9, zorder=3)
    bars_m = ax.bar([i          for i in x], missed,  width, label="Missed",  color=c["missed"],  alpha=0.9, zorder=3)
    bars_p = ax.bar([i + width  for i in x], pending, width, label="Pending", color=c["pending"], alpha=0.9, zorder=3)

    for bars in [bars_t, bars_m, bars_p]:
        for bar in bars:
            h = bar.get_height()
            if h > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2, h + 0.05,
                    str(int(h)), ha="center", va="bottom",
                    fontsize=8, color=c["text"], fontweight="bold",
                )

    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, color=c["text"], fontsize=9)
    ax.tick_params(axis="y", colors=c["text"])
    ax.set_ylabel("Doses", color=c["text"], fontsize=10)
    ax.set_title("7-Day Dose Adherence", color=c["text"], fontsize=13, fontweight="bold", pad=12)
    ax.legend(
        handles=[
            mpatches.Patch(color=c["taken"],   label="Taken"),
            mpatches.Patch(color=c["missed"],  label="Missed"),
            mpatches.Patch(color=c["pending"], label="Pending"),
        ],
        facecolor=c["bg"], labelcolor=c["text"], fontsize=9,
    )
    ax.spines[:].set_color(c["surface"])
    ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", linestyle="--", alpha=0.3, color=c["text"], zorder=0)
    fig.tight_layout()
    return _fig_to_bytes(fig)


def make_donut_chart(taken: int, missed: int, pending: int) -> bytes:
    c = _c()
    total = taken + missed + pending
    if total == 0:
        values      = [1]
        labels_list = ["No doses today"]
        colors_list = [c["surface"]]
    else:
        values, labels_list, colors_list = [], [], []
        if taken  > 0: values.append(taken);   labels_list.append(f"Taken ({taken})");    colors_list.append(c["taken"])
        if missed > 0: values.append(missed);  labels_list.append(f"Missed ({missed})");  colors_list.append(c["missed"])
        if pending> 0: values.append(pending); labels_list.append(f"Pending ({pending})");colors_list.append(c["pending"])

    fig, ax = plt.subplots(figsize=(4.5, 4.5))
    fig.patch.set_facecolor(c["bg"])
    ax.set_facecolor(c["bg"])

    wedges, _ = ax.pie(
        values, colors=colors_list, startangle=90,
        wedgeprops={"width": 0.5, "edgecolor": c["bg"], "linewidth": 2},
    )
    pct = f"{round(taken / total * 100) if total > 0 else 0}%"
    ax.text(0,  0.05, pct,    ha="center", va="center", fontsize=22, fontweight="bold", color=c["text"])
    ax.text(0, -0.22, "taken",ha="center", va="center", fontsize=10, color=c["surface"])
    ax.legend(wedges, labels_list, loc="lower center", bbox_to_anchor=(0.5, -0.15),
              ncol=2, facecolor=c["bg"], labelcolor=c["text"], fontsize=8)
    ax.set_title("Today's Adherence", color=c["text"], fontsize=12, fontweight="bold", pad=8)
    fig.tight_layout()
    return _fig_to_bytes(fig)


def make_medicine_frequency_chart(medicines: dict) -> bytes:
    c = _c()
    freq_counts: dict[str, int] = {}
    for med in medicines.values():
        f = med.get("frequency", "Unknown")
        freq_counts[f] = freq_counts.get(f, 0) + 1

    if not freq_counts:
        fig, ax = plt.subplots(figsize=(7, 3))
        fig.patch.set_facecolor(c["bg"])
        ax.set_facecolor(c["bg"])
        ax.text(0.5, 0.5, "No medicine data", ha="center", va="center",
                color=c["text"], fontsize=12, transform=ax.transAxes)
        ax.axis("off")
        return _fig_to_bytes(fig)

    df = pd.DataFrame(list(freq_counts.items()), columns=["Frequency", "Count"])
    df = df.sort_values("Count", ascending=True)

    fig, ax = plt.subplots(figsize=(8, max(3, len(df) * 0.6 + 1.5)))
    fig.patch.set_facecolor(c["bg"])
    ax.set_facecolor(c["surface"])

    bars = ax.barh(df["Frequency"], df["Count"], color=c["primary"], alpha=0.85, zorder=3)
    for bar in bars:
        w = bar.get_width()
        ax.text(w + 0.05, bar.get_y() + bar.get_height() / 2,
                str(int(w)), va="center", color=c["text"], fontsize=9, fontweight="bold")

    ax.set_xlabel("Number of Medicines", color=c["text"], fontsize=10)
    ax.set_title("Medicines by Frequency", color=c["text"], fontsize=12, fontweight="bold", pad=10)
    ax.tick_params(colors=c["text"])
    ax.spines[:].set_color(c["surface"])
    ax.grid(axis="x", linestyle="--", alpha=0.3, color=c["text"], zorder=0)
    ax.set_xlim(right=df["Count"].max() + 1)
    fig.tight_layout()
    return _fig_to_bytes(fig)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _fig_to_bytes(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def _short_date(iso_date: str) -> str:
    try:
        d = date.fromisoformat(iso_date)
        if d == date.today():
            return "Today"
        return d.strftime("%b %d")
    except ValueError:
        return iso_date


def format_time_12h(time_24: str) -> str:
    try:
        dt = datetime.strptime(time_24, "%H:%M")
        return dt.strftime("%I:%M %p").lstrip("0")
    except ValueError:
        return time_24


def get_greeting() -> str:
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    elif hour < 17:
        return "Good afternoon"
    return "Good evening"


def status_emoji(taken: Optional[bool], missed: bool) -> str:
    if taken is True: return "✅"
    if missed:        return "❌"
    return "⏳"


def status_label(taken: Optional[bool], missed: bool) -> str:
    if taken is True: return "Taken"
    if missed:        return "Missed"
    return "Pending"


def adherence_color(pct: float) -> str:
    c = _c()
    if pct >= 80:   return c["taken"]
    elif pct >= 50: return c["pending"]
    return c["missed"]
