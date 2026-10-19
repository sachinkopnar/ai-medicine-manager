"""
theme.py - Light / Dark theme system for AI Medicine Manager
Call inject_theme() once after st.set_page_config().
"""

import streamlit as st

# ── Palette definitions ───────────────────────────────────────────────────────

DARK_PALETTE = {
    "bg":           "#0f172a",
    "surface":      "#1e293b",
    "surface2":     "#334155",
    "border":       "#334155",
    "border2":      "#475569",
    "text":         "#f1f5f9",
    "text_muted":   "#94a3b8",
    "text_subtle":  "#64748b",
    "primary":      "#3b82f6",
    "primary_dim":  "#1d4ed8",
    "taken":        "#22c55e",
    "missed":       "#ef4444",
    "pending":      "#f59e0b",
    "warn_bg":      "#451a03",
    "warn_border":  "#92400e",
    "warn_text":    "#fde68a",
    "ok_bg":        "#052e16",
    "ok_border":    "#166534",
    "ok_text":      "#86efac",
    "ocr_bg":       "#0f172a",
    "ocr_border":   "#3b82f6",
    "ocr_text":     "#bae6fd",
    "tag_med_bg":   "#1d4ed8",
    "tag_med_text": "#bfdbfe",
    "tag_dos_bg":   "#78350f",
    "tag_dos_text": "#fde68a",
    "sidebar_bg":   "#1e293b",
    "input_bg":     "#1e293b",
}

LIGHT_PALETTE = {
    "bg":           "#f8fafc",
    "surface":      "#ffffff",
    "surface2":     "#f1f5f9",
    "border":       "#e2e8f0",
    "border2":      "#cbd5e1",
    "text":         "#0f172a",
    "text_muted":   "#475569",
    "text_subtle":  "#64748b",
    "primary":      "#2563eb",
    "primary_dim":  "#1d4ed8",
    "taken":        "#16a34a",
    "missed":       "#dc2626",
    "pending":      "#d97706",
    "warn_bg":      "#fef3c7",
    "warn_border":  "#f59e0b",
    "warn_text":    "#92400e",
    "ok_bg":        "#dcfce7",
    "ok_border":    "#16a34a",
    "ok_text":      "#14532d",
    "ocr_bg":       "#eff6ff",
    "ocr_border":   "#2563eb",
    "ocr_text":     "#1e3a8a",
    "tag_med_bg":   "#dbeafe",
    "tag_med_text": "#1e3a8a",
    "tag_dos_bg":   "#fef9c3",
    "tag_dos_text": "#713f12",
    "sidebar_bg":   "#f1f5f9",
    "input_bg":     "#ffffff",
}


def get_palette() -> dict:
    return DARK_PALETTE if st.session_state.get("dark_mode", True) else LIGHT_PALETTE


def get_chart_colors() -> dict:
    """Return Matplotlib-compatible color dict for the current theme."""
    p = get_palette()
    return {
        "taken":   p["taken"],
        "missed":  p["missed"],
        "pending": p["pending"],
        "primary": p["primary"],
        "bg":      p["surface"],
        "surface": p["surface2"],
        "text":    p["text"],
    }


def inject_theme():
    """Inject full CSS theme into Streamlit app based on current mode."""
    p = get_palette()

    css = f"""
<style>
/* ══ Root & App ══════════════════════════════════════════════════════════════ */
[data-testid="stAppViewContainer"] {{
    background: {p["bg"]} !important;
    color: {p["text"]} !important;
}}
[data-testid="stMain"] {{
    background: {p["bg"]} !important;
}}
.main .block-container {{
    background: {p["bg"]} !important;
    color: {p["text"]} !important;
}}

/* ══ Sidebar ════════════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {{
    background: {p["sidebar_bg"]} !important;
    border-right: 1px solid {p["border"]} !important;
}}
[data-testid="stSidebar"] * {{
    color: {p["text"]} !important;
}}

/* ══ Typography ═════════════════════════════════════════════════════════════ */
h1, h2, h3, h4, h5, h6, p, span, div, label {{
    color: {p["text"]};
}}
.stMarkdown {{
    color: {p["text"]};
}}

/* ══ Inputs ════════════════════════════════════════════════════════════════ */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input {{
    background: {p["input_bg"]} !important;
    color: {p["text"]} !important;
    border: 1px solid {p["border2"]} !important;
    border-radius: 8px !important;
}}
.stTextInput input:focus,
.stTextArea textarea:focus {{
    border-color: {p["primary"]} !important;
    box-shadow: 0 0 0 2px {p["primary"]}33 !important;
}}
.stSelectbox > div > div {{
    background: {p["input_bg"]} !important;
    color: {p["text"]} !important;
    border: 1px solid {p["border2"]} !important;
    border-radius: 8px !important;
}}
.stSelectbox [data-baseweb="select"] * {{
    background: {p["input_bg"]} !important;
    color: {p["text"]} !important;
}}

/* ══ Buttons ════════════════════════════════════════════════════════════════ */
.stButton > button {{
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.15s ease !important;
}}
.stButton > button[kind="primary"] {{
    background: {p["primary"]} !important;
    color: #fff !important;
    border: none !important;
}}
.stButton > button[kind="secondary"] {{
    background: {p["surface"]} !important;
    color: {p["text"]} !important;
    border: 1px solid {p["border"]} !important;
}}

/* ══ Tabs ════════════════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {{
    background: {p["surface"]} !important;
    border-radius: 10px !important;
    padding: 4px !important;
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent !important;
    color: {p["text_muted"]} !important;
    border-radius: 7px !important;
}}
.stTabs [aria-selected="true"] {{
    background: {p["primary"]} !important;
    color: #fff !important;
}}

/* ══ Expander ════════════════════════════════════════════════════════════════ */
[data-testid="stExpander"] {{
    background: {p["surface"]} !important;
    border: 1px solid {p["border"]} !important;
    border-radius: 10px !important;
}}
[data-testid="stExpander"] summary {{
    color: {p["text"]} !important;
}}

/* ══ DataFrame ═══════════════════════════════════════════════════════════════ */
[data-testid="stDataFrame"] {{
    background: {p["surface"]} !important;
}}
.dvn-scroller {{
    background: {p["surface"]} !important;
}}

/* ══ Alerts ══════════════════════════════════════════════════════════════════ */
[data-testid="stAlert"] {{
    border-radius: 8px !important;
}}

/* ══ Checkbox / Radio ════════════════════════════════════════════════════════ */
.stCheckbox label,
.stRadio label {{
    color: {p["text"]} !important;
}}

/* ══ Custom component classes ════════════════════════════════════════════════ */
.metric-card {{
    background: {p["surface"]};
    border: 1px solid {p["border"]};
    border-radius: 12px;
    padding: 18px 20px;
    text-align: center;
    margin-bottom: 6px;
    transition: transform 0.1s ease, box-shadow 0.1s ease;
}}
.metric-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 4px 12px {p["primary"]}22;
}}
.metric-card .val {{
    font-size: 2.2rem;
    font-weight: 700;
    line-height: 1.1;
    color: {p["text"]};
}}
.metric-card .lbl {{
    font-size: 0.78rem;
    color: {p["text_muted"]};
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-top: 4px;
}}

.dose-card {{
    background: {p["surface"]};
    border: 1px solid {p["border"]};
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 14px;
}}
.dose-card.taken  {{ border-left: 4px solid {p["taken"]}; }}
.dose-card.missed {{ border-left: 4px solid {p["missed"]}; }}
.dose-card.pending{{ border-left: 4px solid {p["pending"]}; }}

.section-title {{
    font-size: 1.15rem;
    font-weight: 700;
    color: {p["text"]};
    margin: 12px 0 10px;
    border-bottom: 1px solid {p["border"]};
    padding-bottom: 6px;
}}

.warn-box {{
    background: {p["warn_bg"]};
    border: 1px solid {p["warn_border"]};
    border-radius: 8px;
    padding: 12px 16px;
    color: {p["warn_text"]};
    font-size: 0.9rem;
    margin: 8px 0;
}}
.success-box {{
    background: {p["ok_bg"]};
    border: 1px solid {p["ok_border"]};
    border-radius: 8px;
    padding: 12px 16px;
    color: {p["ok_text"]};
    font-size: 0.9rem;
    margin: 8px 0;
}}

.ocr-line {{
    background: {p["ocr_bg"]};
    border-left: 3px solid {p["ocr_border"]};
    padding: 6px 12px;
    margin: 4px 0;
    border-radius: 0 6px 6px 0;
    font-family: monospace;
    font-size: 0.88rem;
    color: {p["ocr_text"]};
}}

.ai-response-box {{
    background: {p["surface"]};
    border: 1px solid {p["primary"]}55;
    border-left: 4px solid {p["primary"]};
    border-radius: 10px;
    padding: 16px 18px;
    margin: 10px 0;
    color: {p["text"]};
    font-size: 0.92rem;
    line-height: 1.6;
}}
.ai-response-box h4 {{
    color: {p["primary"]};
    margin-top: 0;
}}

.ai-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: {p["primary"]}22;
    color: {p["primary"]};
    border: 1px solid {p["primary"]}44;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    margin-bottom: 10px;
}}

.provider-card {{
    background: {p["surface"]};
    border: 1px solid {p["border"]};
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 8px;
}}
.provider-card.active {{
    border-color: {p["primary"]};
    background: {p["primary"]}11;
}}

.tag {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    margin: 3px;
    font-size: 0.85rem;
    font-weight: 500;
}}
.tag-med {{
    background: {p["tag_med_bg"]};
    color: {p["tag_med_text"]};
}}
.tag-dos {{
    background: {p["tag_dos_bg"]};
    color: {p["tag_dos_text"]};
}}

.theme-toggle-btn {{
    cursor: pointer;
    background: {p["surface2"]};
    border: 1px solid {p["border"]};
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.85rem;
    color: {p["text"]};
    display: inline-flex;
    align-items: center;
    gap: 6px;
}}

.info-card {{
    background: {p["surface"]};
    border: 1px solid {p["border"]};
    border-radius: 10px;
    padding: 14px 18px;
    margin: 6px 0;
    color: {p["text"]};
}}

/* ══ Scrollbar ═══════════════════════════════════════════════════════════════ */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: {p["bg"]}; }}
::-webkit-scrollbar-thumb {{ background: {p["border2"]}; border-radius: 3px; }}
::-webkit-scrollbar-thumb:hover {{ background: {p["primary"]}; }}
</style>
"""
    st.markdown(css, unsafe_allow_html=True)
