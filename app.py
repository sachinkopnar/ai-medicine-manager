"""
app.py - AI Medicine Manager (Enhanced)
Full i18n/l10n: English · Hindi (हिन्दी) · Telugu (తెలుగు)
AI backends: Ollama (local) · Groq · OpenAI · Anthropic · Gemini (BYOK)
"""

import streamlit as st
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh
from datetime import datetime, date
import os
import json

# ── dotenv (optional - won't crash if python-dotenv not installed) ─────────────
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Medicine Manager",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Local imports ─────────────────────────────────────────────────────────────
import auth
import profiles as profiles_module
import medicine as med_module
import reminders as reminders_module
import reports as reports_module
import appointments as appt_module
import ocr as ocr_module
import utils
import theme as theme_mod
import ai_backend as ai
from languages import LANGUAGES, LANGUAGE_OPTIONS, get_text


# ── Session state init ────────────────────────────────────────────────────────

def init_session() -> None:
    defaults = {
        # Auth
        "logged_in":  False,
        "username":   "",
        "page":       "Dashboard",
        "edit_med_id": None,
        # Profiles (family/patient)
        "active_profile_id": None,
        "edit_profile_id":   None,
        # Appointments
        "edit_appt_id": None,
        # Reminders
        "reminders_enabled":        True,
        "reminder_sound":           True,
        "reminder_window_minutes":  15,
        "reminder_refresh_seconds": 60,
        # UI
        "dark_mode":  True,
        # i18n
        "lang": "en",
        # AI
        "ai_provider": ai.PROVIDER_GROQ,
        "ai_model":    "llama-3.3-70b-versatile",
        "ai_api_key":  "",
        "ollama_url":  "http://localhost:11434",
        # Chat
        "ai_chat_history": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Pre-load API key from env if not already set
    if not st.session_state["ai_api_key"]:
        for env_var in ("GROQ_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"):
            val = os.getenv(env_var, "")
            if val:
                st.session_state["ai_api_key"] = val
                break


def t(key: str, fallback: str = "") -> str:
    """Shorthand: get translated string for current language."""
    return get_text(st.session_state.get("lang", "en"), key, fallback)


def logout() -> None:
    st.session_state.update({
        "logged_in":  False,
        "username":   "",
        "page":       "Dashboard",
        "edit_med_id": None,
        "active_profile_id": None,
        "edit_profile_id":   None,
        "lang":       "en",
        "ai_chat_history": [],
    })
    st.rerun()


def active_profile_key() -> str:
    """Storage key for the currently active patient/family profile."""
    return profiles_module.profile_key(
        st.session_state["username"], st.session_state["active_profile_id"]
    )


def active_profile_name() -> str:
    prof = profiles_module.get_profile(
        st.session_state["username"], st.session_state["active_profile_id"]
    )
    return prof["name"] if prof else st.session_state["username"]


def render_reminder_engine() -> None:
    """
    Runs on every page while logged in. Fires a browser desktop
    notification (and optional beep) for any dose that's due, and
    triggers a lightweight script re-run periodically (via
    st_autorefresh — NOT a full page reload) so reminders keep firing
    without the user needing to click around. A full browser reload
    was used here previously and could occasionally drop the login
    session; st_autorefresh reruns only the Streamlit script over the
    same session, so login state is preserved. Browsers also require
    a real click before they'll show the permission popup or play
    sound, so we render an actual HTML button for that first step.
    """
    if not st.session_state.get("reminders_enabled", True):
        return

    st_autorefresh(
        interval=st.session_state["reminder_refresh_seconds"] * 1000,
        key="reminder_autorefresh",
    )

    schedule = med_module.get_today_schedule(active_profile_key())
    due = reminders_module.get_due_now(schedule, st.session_state["reminder_window_minutes"])
    payload      = json.dumps(due)
    profile_name = active_profile_name()
    sound_flag   = "true" if st.session_state["reminder_sound"] else "false"

    components.html(f"""
    <div id="med-reminder-box" style="font-family:sans-serif;">
        <button id="med-enable-btn" style="display:none;padding:8px 14px;border-radius:8px;
            border:1px solid #888;background:#fff;cursor:pointer;font-size:0.85rem;">
            🔔 Click to enable reminder alerts &amp; sound
        </button>
        <div id="med-status" style="font-size:0.8rem;color:#888;"></div>
    </div>
    <script>
    (function() {{
        const due = {payload};
        const soundOn = {sound_flag};
        const profileName = {json.dumps(profile_name)};
        const btn    = document.getElementById("med-enable-btn");
        const status = document.getElementById("med-status");

        function beep() {{
            // Alarm-style pattern: three rising beeps instead of one short blip.
            try {{
                const ctx = new (window.AudioContext || window.webkitAudioContext)();
                [0, 1, 2].forEach(function(i) {{
                    setTimeout(function() {{
                        const o = ctx.createOscillator();
                        const g = ctx.createGain();
                        o.connect(g); g.connect(ctx.destination);
                        o.frequency.value = 700 + i * 150;
                        g.gain.value = 0.12;
                        o.start();
                        setTimeout(function() {{ o.stop(); }}, 300);
                    }}, i * 400);
                }});
            }} catch (e) {{}}
        }}

        function notifyOne(slot) {{
            const title = "💊 Medicine reminder — " + slot.name;
            const label = slot.overdue ? "OVERDUE" : "due at " + slot.time;
            const body  = slot.dosage + " · " + label + " (" + profileName + ") — mark it taken in the app.";
            if (window.Notification && Notification.permission === "granted") {{
                // requireInteraction keeps the alert on screen until the user
                // dismisses it, instead of auto-vanishing after a few seconds.
                new Notification(title, {{ body: body, requireInteraction: true, tag: "med-" + slot.med_id + "-" + slot.time }});
                if (soundOn) beep();
            }}
        }}

        function fireDueAlerts() {{
            due.forEach(notifyOne);
        }}

        if (!window.Notification) {{
            status.textContent = "This browser doesn't support desktop notifications.";
        }} else if (Notification.permission === "granted") {{
            status.textContent = "🔔 Reminders enabled for " + profileName + ".";
            fireDueAlerts();
        }} else if (Notification.permission === "denied") {{
            status.textContent = "🔕 Notifications are blocked for this site — allow them in your browser's site settings to get alerts.";
        }} else {{
            // permission === "default": must ask via a real click
            btn.style.display = "inline-block";
            btn.onclick = function() {{
                Notification.requestPermission().then(function(result) {{
                    if (result === "granted") {{
                        status.textContent = "🔔 Reminders enabled for " + profileName + ".";
                        btn.style.display = "none";
                        new Notification("💊 Reminders are on!", {{ body: "You'll be alerted for " + profileName + "'s doses." }});
                        if (soundOn) beep();
                        fireDueAlerts();
                    }} else {{
                        status.textContent = "🔕 Permission was not granted.";
                    }}
                }});
            }};
        }}
    }})();
    </script>
    """, height=50)


# ── AI helpers ────────────────────────────────────────────────────────────────

def _resolve_api_key(provider: str) -> str:
    """Return the best API key for the given provider."""
    session_key = st.session_state.get("ai_api_key", "")

    env_map = {
        ai.PROVIDER_GROQ:      "GROQ_API_KEY",
        ai.PROVIDER_OPENAI:    "OPENAI_API_KEY",
        ai.PROVIDER_ANTHROPIC: "ANTHROPIC_API_KEY",
        ai.PROVIDER_GEMINI:    "GEMINI_API_KEY",
    }
    env_key = os.getenv(env_map.get(provider, ""), "")
    return session_key or env_key


def call_ai_with_feedback(prompt: str, system: str = "") -> tuple[bool, str]:
    provider   = st.session_state["ai_provider"]
    model      = st.session_state["ai_model"]
    api_key    = _resolve_api_key(provider)
    ollama_url = st.session_state["ollama_url"]

    return ai.call_ai(
        prompt,
        provider=provider,
        model=model,
        api_key=api_key,
        system=system,
        ollama_url=ollama_url,
    )


def ai_configured() -> bool:
    p = st.session_state["ai_provider"]
    if p == ai.PROVIDER_OLLAMA:
        return True
    return bool(_resolve_api_key(p))


# ── Auth page ─────────────────────────────────────────────────────────────────

def page_auth() -> None:
    p = theme_mod.get_palette()
    st.markdown(
        f"<h1 style='text-align:center;color:{p['primary']};margin-bottom:4px'>💊 AI Medicine Manager</h1>"
        f"<p style='text-align:center;color:{p['text_muted']};margin-bottom:28px'>"
        f"{t('app_tagline')}</p>",
        unsafe_allow_html=True,
    )

    col_l, col_m, col_r = st.columns([1, 1.4, 1])
    with col_m:
        tab_login, tab_signup = st.tabs([f"🔐 {t('login')}", f"📝 {t('signup')}"])

        with tab_login:
            st.markdown(f"### {t('welcome_back')}")
            username = st.text_input(t("username"), key="login_user", placeholder="your_username")
            password = st.text_input(t("password"), type="password", key="login_pass", placeholder="••••••••")
            if st.button(t("login"), use_container_width=True, key="login_btn", type="primary"):
                ok, msg = auth.login(username, password)
                if ok:
                    clean_user = username.strip().lower()
                    st.session_state["logged_in"] = True
                    st.session_state["username"]  = clean_user
                    st.session_state["active_profile_id"] = (
                        profiles_module.ensure_default_profile(clean_user)
                    )
                    st.rerun()
                else:
                    st.error(msg)
            st.markdown(
                f"<p style='color:{p['text_subtle']};font-size:0.8rem;text-align:center;margin-top:8px'>"
                f"{t('demo_hint')}</p>",
                unsafe_allow_html=True,
            )

        with tab_signup:
            st.markdown(f"### {t('create_account_h')}")
            new_user  = st.text_input(t("username"),         key="su_user",  placeholder="choose_username")
            new_email = st.text_input(t("email_optional"),   key="su_email", placeholder="you@example.com")
            new_pass  = st.text_input(t("password"),         type="password", key="su_pass",  placeholder="min 6 chars")
            new_pass2 = st.text_input(t("confirm_password"), type="password", key="su_pass2", placeholder="repeat password")
            if st.button(t("create_account"), use_container_width=True, key="su_btn", type="primary"):
                if new_pass != new_pass2:
                    st.error(t("passwords_no_match"))
                else:
                    ok, msg = auth.signup(new_user, new_pass, new_email)
                    if ok:
                        st.success(msg + f" {t('demo_hint')}")
                    else:
                        st.error(msg)


# ── Sidebar ───────────────────────────────────────────────────────────────────

def render_sidebar() -> None:
    p = theme_mod.get_palette()

    with st.sidebar:
        # ── Header row ────────────────────────────────────────────────────────
        col_logo, col_theme = st.columns([3, 1])
        with col_logo:
            st.markdown(
                f"<div style='padding:12px 0 4px'>"
                f"<div style='font-size:1.4rem;font-weight:700;color:{p['primary']}'>💊 MedManager</div>"
                f"<div style='color:{p['text_muted']};font-size:0.82rem'>@{st.session_state['username']}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
        with col_theme:
            st.markdown("<div style='padding-top:14px'>", unsafe_allow_html=True)
            icon = "🌙" if st.session_state["dark_mode"] else "☀️"
            if st.button(icon, key="theme_toggle", help="Toggle light/dark mode"):
                st.session_state["dark_mode"] = not st.session_state["dark_mode"]
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")

        # ── Patient/Family profile switcher ─────────────────────────────────────
        all_profiles = profiles_module.list_profiles(st.session_state["username"])
        if st.session_state["active_profile_id"] not in all_profiles:
            st.session_state["active_profile_id"] = next(iter(all_profiles))

        prof_ids    = list(all_profiles.keys())
        prof_labels = [
            f"{prof['name']} ({prof['relation']})" for prof in all_profiles.values()
        ]
        current_idx = prof_ids.index(st.session_state["active_profile_id"])

        selected_label = st.selectbox(
            "👤 Profile", prof_labels, index=current_idx, key="profile_select",
        )
        selected_id = prof_ids[prof_labels.index(selected_label)]
        if selected_id != st.session_state["active_profile_id"]:
            st.session_state["active_profile_id"] = selected_id
            st.session_state["page"] = "Dashboard"
            st.rerun()

        if st.button("👨‍👩‍👧 Manage Profiles", use_container_width=True, key="nav_profiles"):
            st.session_state["page"] = "Profiles"
            st.rerun()

        st.markdown("---")

        # ── Language selector (i18n) ───────────────────────────────────────────
        lang_codes  = list(LANGUAGE_OPTIONS.keys())
        lang_labels = list(LANGUAGE_OPTIONS.values())
        current_idx = lang_codes.index(st.session_state.get("lang", "en"))

        selected_label = st.selectbox(
            t("language_label"),
            lang_labels,
            index=current_idx,
            key="lang_select",
        )
        new_lang = lang_codes[lang_labels.index(selected_label)]
        if new_lang != st.session_state["lang"]:
            st.session_state["lang"] = new_lang
            st.rerun()

        st.markdown("---")

        # ── Navigation ─────────────────────────────────────────────────────────
        nav_map = [
            (t("dashboard"),     "Dashboard",    "🏠"),
            (t("add_medicine"),  "Add Medicine", "➕"),
            (t("my_medicines"),  "My Medicines", "💊"),
            (t("ocr"),           "OCR Scanner",  "📷"),
            (t("analytics"),     "Analytics",    "📊"),
            ("Reminders",        "Reminders",    "🔔"),
            ("Appointments",     "Appointments", "📅"),
            ("Report",           "Report",       "📑"),
            (t("ai_assistant"),  "AI Assistant", "🤖"),
            (t("ai_settings"),   "AI Settings",  "⚙️"),
        ]

        for display_name, page_key, icon_str in nav_map:
            active    = st.session_state["page"] == page_key
            btn_style = "primary" if active else "secondary"
            if st.button(
                f"{icon_str}  {display_name}",
                key=f"nav_{page_key}",
                use_container_width=True,
                type=btn_style,
            ):
                st.session_state["page"]        = page_key
                st.session_state["edit_med_id"] = None
                st.rerun()

        st.markdown("---")

        # ── AI status indicator ────────────────────────────────────────────────
        provider = st.session_state["ai_provider"]
        api_key  = _resolve_api_key(provider)

        if provider == ai.PROVIDER_OLLAMA:
            running = ai.is_ollama_running(st.session_state["ollama_url"])
            dot   = "🟢" if running else "🔴"
            label = f"Ollama {t('ai_status_running') if running else t('ai_status_offline')}"
        elif provider == ai.PROVIDER_GROQ:
            dot   = "🟢" if api_key else "🔴"
            label = f"Groq {t('ai_status_ready') if api_key else t('ai_status_no_key')}"
        else:
            dot   = "🟢" if api_key else "🟡"
            pname = provider.split(" ")[0]
            label = f"{pname} {t('ai_status_ready') if api_key else t('ai_status_no_key')}"

        st.markdown(
            f"<div style='color:{p['text_muted']};font-size:0.78rem;margin-bottom:4px'>"
            f"{dot} AI: {label}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div style='color:{p['text_subtle']};font-size:0.78rem;margin-bottom:6px'>"
            f"📅 {date.today().strftime('%A, %B %d')}</div>",
            unsafe_allow_html=True,
        )

        if st.button(f"🚪  {t('logout')}", use_container_width=True, key="logout_btn"):
            logout()


# ── Dashboard ─────────────────────────────────────────────────────────────────

def page_dashboard() -> None:
    user = active_profile_key()
    p    = theme_mod.get_palette()

    hour = datetime.now().hour
    greeting = (
        t("greeting_morning")   if hour < 12 else
        t("greeting_afternoon") if hour < 17 else
        t("greeting_evening")
    )
    st.markdown(
        f"<h2 style='margin-bottom:4px'>{greeting}, {st.session_state['username']} 👋</h2>"
        f"<p style='color:{p['text_subtle']}'>"
        f"📋 Viewing: <b>{active_profile_name()}</b> &nbsp;|&nbsp; "
        f"{date.today().strftime('%A, %B %d, %Y')}</p>",
        unsafe_allow_html=True,
    )

    # ── Due-now reminder banner ──────────────────────────────────────────────
    schedule_for_alerts = med_module.get_today_schedule(user)
    due_now = reminders_module.get_due_now(
        schedule_for_alerts, st.session_state["reminder_window_minutes"]
    )
    if due_now:
        st.markdown("<div class='section-title'>🔔 Due Now</div>", unsafe_allow_html=True)
        for slot in due_now:
            when = "overdue" if slot["overdue"] else f"in {slot['minutes_until']} min"
            col_msg, col_btn = st.columns([4, 1])
            with col_msg:
                st.markdown(
                    f"<div class='info-card'>💊 <b>{slot['name']}</b> ({slot['dosage']}) "
                    f"— {slot['time']} &nbsp;<span style='color:{p['missed'] if slot['overdue'] else p['text_muted']}'>"
                    f"({when})</span></div>",
                    unsafe_allow_html=True,
                )
            with col_btn:
                if st.button("✅ Taken", key=f"due_taken_{slot['med_id']}_{slot['time']}"):
                    med_module.mark_dose(user, slot["med_id"], slot["time"], taken=True)
                    st.rerun()
        st.markdown("---")

    # ── Low-stock banner ──────────────────────────────────────────────────────
    low_stock = med_module.get_low_stock(user, days_threshold=5)
    if low_stock:
        st.markdown("<div class='section-title'>📦 Low Stock</div>", unsafe_allow_html=True)
        for item in low_stock:
            days_txt = (
                "out of stock" if item["stock_quantity"] <= 0
                else f"~{item['days_remaining']} day(s) left"
            )
            col_msg, col_amt, col_btn = st.columns([3, 1, 1])
            with col_msg:
                st.markdown(
                    f"<div class='info-card'>📦 <b>{item['name']}</b> ({item['dosage']}) "
                    f"— {item['stock_quantity']} left &nbsp;"
                    f"<span style='color:{p['missed']}'>({days_txt})</span></div>",
                    unsafe_allow_html=True,
                )
            with col_amt:
                restock_amt = st.number_input(
                    "Add", min_value=1, value=10, step=1,
                    key=f"restock_amt_{item['med_id']}", label_visibility="collapsed",
                )
            with col_btn:
                if st.button("↻ Restock", key=f"restock_btn_{item['med_id']}"):
                    med_module.restock_medicine(user, item["med_id"], int(restock_amt))
                    st.rerun()
        st.markdown("---")

    # ── Next appointment card ────────────────────────────────────────────────
    next_appt = appt_module.get_next_appointment(user)
    if next_appt:
        when = datetime.strptime(next_appt["date"], "%Y-%m-%d").strftime("%a, %d %b %Y") + " · " + \
            datetime.strptime(next_appt["time"], "%H:%M").strftime("%I:%M %p")
        st.markdown(
            f"<div style='background:linear-gradient(135deg,{p['primary']},{p['primary_dim']});"
            f"border-radius:14px;padding:16px 20px;margin-bottom:18px;color:white;'>"
            f"<div style='font-size:0.75rem;text-transform:uppercase;opacity:0.85'>⏰ Next Appointment</div>"
            f"<div style='font-size:1.1rem;font-weight:700;margin:4px 0 2px'>{next_appt['doctor']}</div>"
            f"<div style='font-size:0.9rem;opacity:0.95'>{when}</div></div>",
            unsafe_allow_html=True,
        )

    stats = med_module.get_medicine_stats(user)

    c1, c2, c3, c4, c5 = st.columns(5)

    def kpi(col, val, label, color=None):
        color = color or p["text"]
        col.markdown(
            f"<div class='metric-card'>"
            f"<div class='val' style='color:{color}'>{val}</div>"
            f"<div class='lbl'>{label}</div></div>",
            unsafe_allow_html=True,
        )

    kpi(c1, stats["total_medicines"], t("medicines"))
    kpi(c2, stats["today_total"],     t("todays_doses"))
    kpi(c3, stats["today_taken"],     t("taken"),    p["taken"])
    kpi(c4, stats["today_missed"],    t("missed"),   p["missed"])
    kpi(c5, f"{stats['adherence_pct']}%", t("adherence"),
        utils.adherence_color(stats["adherence_pct"]))

    st.markdown("---")
    left, right = st.columns([2, 1])

    with right:
        st.markdown(f"<div class='section-title'>{t('todays_overview')}</div>", unsafe_allow_html=True)
        st.image(
            utils.make_donut_chart(stats["today_taken"], stats["today_missed"], stats["today_pending"]),
            use_container_width=True,
        )
        if ai_configured() and stats["today_total"] > 0:
            if st.button(t("ai_tip"), key="dash_ai_tip", use_container_width=True):
                with st.spinner("Getting AI insight…"):
                    medicines = list(med_module.get_all_medicines(user).values())
                    weekly    = med_module.get_weekly_adherence(user)
                    prompt    = ai.ai_adherence_insights(stats, weekly, medicines)
                    ok, resp  = call_ai_with_feedback(prompt, ai.SYSTEM_HEALTH_ASSISTANT)
                if ok:
                    st.markdown(f"<div class='ai-response-box'>{resp}</div>", unsafe_allow_html=True)
                else:
                    st.error(resp)

    with left:
        st.markdown(f"<div class='section-title'>{t('todays_schedule')}</div>", unsafe_allow_html=True)
        schedule = med_module.get_today_schedule(user)
        if not schedule:
            st.info(t("no_medicines_hint"))
        else:
            for slot in schedule:
                _render_dose_slot(user, slot)


def _render_dose_slot(user: str, slot: dict) -> None:
    p            = theme_mod.get_palette()
    status_class = "taken" if slot["taken"] else ("missed" if slot["missed"] else "pending")
    emoji        = utils.status_emoji(slot["taken"], slot["missed"])
    time_fmt     = utils.format_time_12h(slot["time"])

    if slot["taken"] is True:
        label = t("status_taken")
    elif slot["missed"]:
        label = t("status_missed")
    else:
        label = t("status_pending")

    col_info, col_btn = st.columns([5, 1])
    with col_info:
        st.markdown(
            f"<div class='dose-card {status_class}'>"
            f"<span style='font-size:1.4rem'>{emoji}</span>"
            f"<div style='flex:1'>"
            f"  <div style='font-weight:600;font-size:1rem;color:{p['text']}'>{slot['name']} - {slot['dosage']}</div>"
            f"  <div style='color:{p['text_muted']};font-size:0.82rem'>{time_fmt} &nbsp;·&nbsp; {slot['frequency']}"
            + (f" &nbsp;·&nbsp; {slot['notes']}" if slot["notes"] else "")
            + f"</div></div>"
            f"<span style='font-size:0.78rem;color:{p['text_subtle']};white-space:nowrap'>{label}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with col_btn:
        if slot["taken"] is not True:
            if st.button(t("mark_taken"), key=f"take_{slot['med_id']}_{slot['time']}",
                         use_container_width=True):
                med_module.mark_dose(user, slot["med_id"], slot["time"], taken=True)
                st.rerun()
        else:
            if st.button(t("undo_taken"), key=f"undo_{slot['med_id']}_{slot['time']}",
                         use_container_width=True):
                med_module.mark_dose(user, slot["med_id"], slot["time"], taken=False)
                st.rerun()


# ── Add / Edit Medicine ───────────────────────────────────────────────────────

def page_add_medicine() -> None:
    user     = active_profile_key()
    edit_id  = st.session_state.get("edit_med_id")
    existing = med_module.get_all_medicines(user).get(edit_id) if edit_id else None

    title = t("edit_medicine") if existing else t("add_new_medicine")
    st.markdown(f"<h2>{title}</h2>", unsafe_allow_html=True)

    FREQUENCIES  = list(med_module.FREQUENCY_MAX_DOSES.keys())
    TIME_OPTIONS = [f"{h:02d}:{m:02d}" for h in range(24) for m in [0, 30]]

    ocr_prefill = st.session_state.pop("ocr_prefill_name", None)
    ocr_ai_data = st.session_state.pop("ocr_ai_data", None)

    with st.form("med_form", clear_on_submit=not bool(existing)):
        col1, col2 = st.columns(2)
        with col1:
            default_name = (
                ocr_ai_data["name"] if ocr_ai_data else
                ocr_prefill if ocr_prefill else
                (existing["name"] if existing else "")
            )
            name = st.text_input(t("medicine_name"), value=default_name,
                                 placeholder=t("medicine_name_ph"))

            default_dosage = (
                ocr_ai_data.get("dosage", "") if ocr_ai_data else
                (existing["dosage"] if existing else "")
            )
            dosage = st.text_input(t("dosage"), value=default_dosage,
                                   placeholder=t("dosage_ph"))

            default_freq = (
                ocr_ai_data.get("frequency", FREQUENCIES[0]) if ocr_ai_data else
                (existing["frequency"] if existing and existing["frequency"] in FREQUENCIES else FREQUENCIES[0])
            )
            freq_idx  = FREQUENCIES.index(default_freq) if default_freq in FREQUENCIES else 0
            frequency = st.selectbox(t("frequency"), FREQUENCIES, index=freq_idx)

        with col2:
            start_val = (
                date.fromisoformat(existing["start_date"])
                if existing and existing.get("start_date") else date.today()
            )
            start_date = st.date_input(t("start_date"), value=start_val)

            end_date_enabled = st.checkbox(
                t("set_end_date"),
                value=bool(existing and existing.get("end_date")),
            )
            end_date = None
            if end_date_enabled:
                end_val = (
                    date.fromisoformat(existing["end_date"])
                    if existing and existing.get("end_date") else date.today()
                )
                end_date = st.date_input(t("end_date"), value=end_val)

        max_times      = med_module.FREQUENCY_MAX_DOSES.get(frequency, 4)
        st.markdown(f"**{t('dose_times')}** (up to {max_times})")
        time_cols      = st.columns(min(max_times, 4))
        default_times  = existing["times"] if existing else []
        selected_times = []
        for i in range(max_times):
            with time_cols[i % 4]:
                default_val = default_times[i] if i < len(default_times) else "08:00"
                sel = st.selectbox(
                    f"{t('time_label')} {i+1}", TIME_OPTIONS,
                    index=TIME_OPTIONS.index(default_val) if default_val in TIME_OPTIONS else 0,
                    key=f"time_{i}",
                )
                selected_times.append(sel)

        default_notes = (
            ocr_ai_data.get("instructions", "") if ocr_ai_data else
            (existing["notes"] if existing else "")
        )
        notes = st.text_area(t("notes_optional"), value=default_notes,
                             placeholder=t("notes_ph"), height=80)

        # ── Optional stock tracking ─────────────────────────────────────────
        existing_stock = existing.get("stock_quantity") if existing else None
        track_stock = st.checkbox(
            "📦 Track stock level (get a low-stock alert when it's running out)",
            value=existing_stock is not None,
        )
        stock_quantity = None
        if track_stock:
            stock_quantity = st.number_input(
                "Current stock (number of pills/units)",
                min_value=0, step=1,
                value=existing_stock if existing_stock is not None else 0,
            )

        btn_label = t("update_medicine_btn") if existing else t("add_medicine_btn")
        submitted = st.form_submit_button(btn_label, use_container_width=True, type="primary")

        if submitted:
            end_date_str = end_date.isoformat() if end_date else ""
            if existing:
                ok, msg = med_module.update_medicine(
                    user, edit_id, name, dosage, frequency,
                    selected_times, notes, start_date.isoformat(), end_date_str,
                    stock_quantity=stock_quantity,
                )
            else:
                ok, msg = med_module.add_medicine(
                    user, name, dosage, frequency,
                    selected_times, notes, start_date.isoformat(), end_date_str,
                    stock_quantity=stock_quantity,
                )
            lines = msg.split("\n\n")
            if ok:
                st.markdown(f"<div class='success-box'>{lines[0]}</div>", unsafe_allow_html=True)
            else:
                st.error(lines[0])
            for warn_line in lines[1:]:
                if warn_line.strip():
                    st.markdown(f"<div class='warn-box'>{warn_line}</div>", unsafe_allow_html=True)
            if ok and existing:
                st.session_state["edit_med_id"] = None

    # ── AI explainer ──────────────────────────────────────────────────────────
    if ai_configured():
        st.markdown("---")
        st.markdown(f"<div class='section-title'>{t('ai_explainer_title')}</div>",
                    unsafe_allow_html=True)
        exp_name = st.text_input(t("medicine_to_explain"), placeholder=t("explain_ph"),
                                 key="explain_name_input")
        exp_dose = st.text_input(t("dosage"),              placeholder=t("dosage_explain_ph"),
                                 key="explain_dose_input")
        if st.button(t("explain_btn"), key="explain_btn", type="primary"):
            if exp_name:
                with st.spinner("Asking AI…"):
                    prompt   = ai.ai_explain_medicine(exp_name, exp_dose, "", "")
                    ok, resp = call_ai_with_feedback(prompt, ai.SYSTEM_HEALTH_ASSISTANT)
                if ok:
                    st.markdown(f"<div class='ai-response-box'>{resp}</div>", unsafe_allow_html=True)
                else:
                    st.error(resp)
            else:
                st.warning("Please enter a medicine name.")
    else:
        st.info(t("configure_ai_hint"))


# ── My Medicines ──────────────────────────────────────────────────────────────

def page_my_medicines() -> None:
    user     = active_profile_key()
    p        = theme_mod.get_palette()
    all_meds = med_module.get_all_medicines(user)

    st.markdown(f"<h2>{t('my_medicines_h')}</h2>", unsafe_allow_html=True)

    if not all_meds:
        st.info(t("no_medicines_yet"))
        return

    col_search, col_interact_btn = st.columns([3, 1])
    with col_search:
        search = st.text_input(t("search_label"), placeholder=t("search_ph"))
    with col_interact_btn:
        st.markdown("<div style='padding-top:26px'>", unsafe_allow_html=True)
        check_interact = st.button(t("check_interactions"), use_container_width=True,
                                   key="check_interactions_btn", type="primary")
        st.markdown("</div>", unsafe_allow_html=True)

    if check_interact:
        if not ai_configured():
            st.warning(t("configure_ai_first"))
        else:
            med_list = list(all_meds.values())
            if len(med_list) < 2:
                st.info("Add at least 2 medicines to check interactions.")
            else:
                with st.spinner("🧪 Analysing drug interactions with AI…"):
                    prompt   = ai.ai_analyze_interactions(med_list)
                    ok, resp = call_ai_with_feedback(prompt, ai.SYSTEM_HEALTH_ASSISTANT)
                st.markdown("<div class='ai-badge'>🤖 AI Drug Interaction Analysis</div>",
                            unsafe_allow_html=True)
                if ok:
                    st.markdown(f"<div class='ai-response-box'>{resp}</div>", unsafe_allow_html=True)
                else:
                    st.error(resp)

    if ai_configured() and all_meds:
        if st.button(t("suggest_schedule"), key="suggest_schedule_btn"):
            with st.spinner("Optimising your schedule…"):
                prompt   = ai.ai_suggest_schedule(list(all_meds.values()))
                ok, resp = call_ai_with_feedback(prompt, ai.SYSTEM_HEALTH_ASSISTANT)
            if ok:
                st.markdown(
                    f"<div class='ai-badge'>🤖 Schedule Optimisation</div>"
                    f"<div class='ai-response-box'>{resp}</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.error(resp)

    st.markdown("---")

    for mid, m in all_meds.items():
        if search and search.lower() not in m["name"].lower() \
                  and search.lower() not in m["dosage"].lower():
            continue

        with st.expander(f"💊 {m['name']} - {m['dosage']}  ({m['frequency']})", expanded=False):
            col_info, col_actions = st.columns([3, 1])
            with col_info:
                st.markdown(f"**{t('frequency_label')}** {m['frequency']}")
                st.markdown(f"**{t('times_label')}** {', '.join(utils.format_time_12h(x) for x in m.get('times', []))}")
                st.markdown(f"**{t('start_label')}** {m.get('start_date','-')}  &nbsp; **{t('end_label')}** {m.get('end_date', t('ongoing'))}")
                if m.get("notes"):
                    st.markdown(f"**{t('notes_label')}** {m['notes']}")
                if m.get("stock_quantity") is not None:
                    low = m["stock_quantity"] <= 5
                    color = p["missed"] if low else p["text_muted"]
                    st.markdown(
                        f"**📦 Stock:** <span style='color:{color}'>{m['stock_quantity']} unit(s)</span>",
                        unsafe_allow_html=True,
                    )

            with col_actions:
                if st.button(t("edit_btn"),   key=f"edit_{mid}", use_container_width=True):
                    st.session_state["edit_med_id"] = mid
                    st.session_state["page"]        = "Add Medicine"
                    st.rerun()
                if st.button(t("delete_btn"), key=f"del_{mid}",  use_container_width=True):
                    ok, msg = med_module.delete_medicine(user, mid)
                    if ok:
                        st.success(msg); st.rerun()
                    else:
                        st.error(msg)
                if ai_configured():
                    if st.button(t("explain_btn_short"), key=f"explain_{mid}", use_container_width=True):
                        with st.spinner("Asking AI…"):
                            prompt   = ai.ai_explain_medicine(
                                m["name"], m["dosage"], m["frequency"], m.get("notes", ""))
                            ok, resp = call_ai_with_feedback(prompt, ai.SYSTEM_HEALTH_ASSISTANT)
                        if ok:
                            st.markdown(
                                f"<div class='ai-badge'>🤖 {m['name']}</div>"
                                f"<div class='ai-response-box'>{resp}</div>",
                                unsafe_allow_html=True,
                            )
                        else:
                            st.error(resp)


# ── OCR Scanner ───────────────────────────────────────────────────────────────

def page_ocr_scanner() -> None:
    p = theme_mod.get_palette()
    st.markdown(f"<h2>{t('ocr_title')}</h2>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color:{p['text_muted']}'>{t('ocr_subtitle')}</p>",
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader(
        t("upload_label"),
        type=["png", "jpg", "jpeg", "bmp", "tiff", "webp"],
        help=t("upload_hint"),
    )

    if not uploaded:
        st.markdown(
            f"<div style='background:{p['surface']};border:2px dashed {p['border']};border-radius:12px;"
            f"padding:40px;text-align:center;color:{p['text_muted']};'>"
            f"<div style='font-size:3rem'>📋</div>"
            f"<div style='margin-top:8px'>{t('upload_placeholder')}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        return

    col_img, col_result = st.columns([1, 1])

    with col_img:
        st.markdown(f"<div class='section-title'>{t('uploaded_prescription')}</div>",
                    unsafe_allow_html=True)
        st.image(uploaded, use_container_width=True)

    image_bytes = uploaded.read()

    with col_result:
        st.markdown(f"<div class='section-title'>{t('extracted_info')}</div>",
                    unsafe_allow_html=True)

        with st.spinner("🔍 Running OCR…"):
            result = ocr_module.process_prescription(image_bytes)

        if not result["success"]:
            st.error(f"OCR failed: {result['error']}")
            st.info(t("ocr_tips"))
            return

        parsed = result["parsed"]

        if parsed["detected_medicines"]:
            st.markdown(f"**{t('rule_medicines')}**")
            for med_name in parsed["detected_medicines"]:
                st.markdown(f"<span class='tag tag-med'>{med_name}</span>",
                            unsafe_allow_html=True)
        if parsed["dosages"]:
            st.markdown(f"**{t('detected_dosages')}**")
            for d in parsed["dosages"]:
                st.markdown(f"<span class='tag tag-dos'>{d}</span>", unsafe_allow_html=True)

        if parsed["highlighted_lines"]:
            st.markdown(f"**📋 {t('medicine_lines')} ({len(parsed['highlighted_lines'])}):**")
            for line in parsed["highlighted_lines"][:20]:
                st.markdown(f"<div class='ocr-line'>{line}</div>", unsafe_allow_html=True)

        with st.expander(t("full_text")):
            st.code(parsed["full_text"] or "(No text)", language=None)

        st.markdown("---")
        st.markdown(f"<div class='section-title'>{t('ai_enhanced_parse')}</div>",
                    unsafe_allow_html=True)

        if not ai_configured():
            st.info(t("configure_ai_hint"))
        else:
            if st.button(t("ai_parse_btn"), key="ai_parse_btn", type="primary"):
                with st.spinner("AI is reading the prescription…"):
                    prompt   = ai.ai_ocr_enhance(parsed["full_text"])
                    ok, resp = call_ai_with_feedback(prompt)

                if ok:
                    ai_data = ai.parse_ai_ocr_json(resp)
                    if ai_data and "medicines" in ai_data:
                        found = len(ai_data["medicines"])
                        st.success(f"{t('ai_found')} {found} {t('medicines_word')}")
                        for med_item in ai_data["medicines"]:
                            muted_color = p["text_muted"]
                            st.markdown(
                                f"<div class='info-card'>"
                                f"<b>{med_item.get('name','?')}</b> - {med_item.get('dosage','?')}<br>"
                                f"<span style='color:{muted_color};font-size:0.85rem'>"
                                f"Frequency: {med_item.get('frequency','?')} &nbsp;|&nbsp; "
                                f"Duration: {med_item.get('duration','?')} &nbsp;|&nbsp; "
                                f"{med_item.get('instructions','')}</span>"
                                f"</div>",
                                unsafe_allow_html=True,
                            )
                            col_add, _ = st.columns([1, 3])
                            with col_add:
                                btn_key = f"add_ai_med_{med_item.get('name','x').replace(' ','_')}"
                                if st.button(f"➕ Add {med_item.get('name','')}", key=btn_key):
                                    st.session_state["page"]        = "Add Medicine"
                                    st.session_state["ocr_ai_data"] = med_item
                                    st.rerun()
                    else:
                        st.markdown(f"<div class='ai-response-box'>{resp}</div>",
                                    unsafe_allow_html=True)
                else:
                    st.error(resp)

        if parsed["detected_medicines"]:
            st.markdown("---")
            st.markdown(f"**{t('quick_add_label')}**")
            chosen = st.selectbox(t("select_medicine"), parsed["detected_medicines"])
            if st.button(t("go_add_medicine"), type="primary"):
                st.session_state["page"]             = "Add Medicine"
                st.session_state["ocr_prefill_name"] = chosen
                st.rerun()


# ── Analytics ─────────────────────────────────────────────────────────────────

def page_analytics() -> None:
    import pandas as pd

    user     = active_profile_key()
    p        = theme_mod.get_palette()
    stats    = med_module.get_medicine_stats(user)
    weekly   = med_module.get_weekly_adherence(user)
    all_meds = med_module.get_all_medicines(user)

    st.markdown(f"<h2>{t('analytics_title')}</h2>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    def kpi(col, val, label, color=None):
        color = color or p["text"]
        col.markdown(
            f"<div class='metric-card'>"
            f"<div class='val' style='color:{color}'>{val}</div>"
            f"<div class='lbl'>{label}</div></div>",
            unsafe_allow_html=True,
        )

    kpi(c1, stats["total_medicines"], t("active_medicines"))
    kpi(c2, f"{stats['adherence_pct']}%", t("todays_adherence"),
        utils.adherence_color(stats["adherence_pct"]))
    total_week_taken = sum(d["taken"] for d in weekly.values())
    total_week_doses = sum(d["taken"] + d["missed"] + d["pending"] for d in weekly.values())
    week_pct = round(total_week_taken / total_week_doses * 100) if total_week_doses > 0 else 0
    kpi(c3, f"{week_pct}%", t("7day_adherence"), utils.adherence_color(week_pct))

    st.markdown("---")
    col_a, col_b = st.columns([2, 1])

    with col_a:
        st.markdown(f"<div class='section-title'>{t('7day_chart_title')}</div>",
                    unsafe_allow_html=True)
        if any(sum(v.values()) > 0 for v in weekly.values()):
            st.image(utils.make_weekly_adherence_chart(weekly), use_container_width=True)
        else:
            st.info(t("no_dose_data"))

    with col_b:
        st.markdown(f"<div class='section-title'>{t('todays_summary')}</div>",
                    unsafe_allow_html=True)
        st.image(
            utils.make_donut_chart(stats["today_taken"], stats["today_missed"], stats["today_pending"]),
            use_container_width=True,
        )

    st.markdown("---")
    st.markdown(f"<div class='section-title'>{t('by_frequency')}</div>", unsafe_allow_html=True)
    if all_meds:
        col_fc, _ = st.columns([2, 1])
        with col_fc:
            st.image(utils.make_medicine_frequency_chart(all_meds), use_container_width=True)
    else:
        st.info(t("no_medicines_data"))

    st.markdown("---")
    st.markdown(f"<div class='section-title'>{t('weekly_breakdown')}</div>", unsafe_allow_html=True)
    rows = []
    for day, vals in weekly.items():
        total = vals["taken"] + vals["missed"] + vals["pending"]
        pct   = round(vals["taken"] / total * 100) if total > 0 else 0
        rows.append({
            t("date_col"):      day,
            f"✅ {t('taken')}":  vals["taken"],
            f"❌ {t('missed')}": vals["missed"],
            f"⏳ {t('pending')}":vals["pending"],
            t("total_col"):     total,
            t("adherence_col"): f"{pct}%",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown(f"<div class='section-title'>{t('ai_coach_title')}</div>", unsafe_allow_html=True)
    if not ai_configured():
        st.info(t("configure_ai_coach"))
    else:
        if st.button(t("get_coaching"), key="adherence_coach_btn", type="primary"):
            with st.spinner("Analysing your adherence patterns…"):
                medicines = list(all_meds.values())
                prompt    = ai.ai_adherence_insights(stats, weekly, medicines)
                ok, resp  = call_ai_with_feedback(prompt, ai.SYSTEM_HEALTH_ASSISTANT)
            st.markdown("<div class='ai-badge'>🤖 Personalised Adherence Coaching</div>",
                        unsafe_allow_html=True)
            if ok:
                st.markdown(f"<div class='ai-response-box'>{resp}</div>", unsafe_allow_html=True)
            else:
                st.error(resp)


# ── AI Assistant ──────────────────────────────────────────────────────────────

def page_ai_assistant() -> None:
    user = active_profile_key()
    p    = theme_mod.get_palette()

    st.markdown(f"<h2>{t('ai_assistant_title')}</h2>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color:{p['text_muted']}'>{t('ai_assistant_sub')}</p>",
        unsafe_allow_html=True,
    )

    if not ai_configured():
        st.warning(t("configure_ai_first_long"))
        if st.button(t("go_ai_settings"), type="primary"):
            st.session_state["page"] = "AI Settings"
            st.rerun()
        return

    provider = st.session_state["ai_provider"]
    model    = st.session_state["ai_model"]
    st.markdown(f"<div class='ai-badge'>🤖 {provider} · {model}</div>", unsafe_allow_html=True)

    all_meds = med_module.get_all_medicines(user)
    st.markdown(f"**{t('quick_actions')}**")
    qa_cols = st.columns(4)

    quick_actions = [
        (t("drug_interactions"), "check_interactions"),
        (t("optimise_schedule"), "optimise_schedule"),
        (t("adherence_tips"),    "adherence_tips"),
        (t("clear_chat"),        "clear_chat"),
    ]
    for col_obj, (label, key) in zip(qa_cols, quick_actions):
        with col_obj:
            if st.button(label, key=f"qa_{key}", use_container_width=True):
                if key == "clear_chat":
                    st.session_state["ai_chat_history"] = []
                    st.rerun()
                elif key == "check_interactions" and all_meds:
                    with st.spinner("Checking interactions…"):
                        prompt   = ai.ai_analyze_interactions(list(all_meds.values()))
                        ok, resp = call_ai_with_feedback(prompt, ai.SYSTEM_HEALTH_ASSISTANT)
                    _add_chat("Check drug interactions for my medicines.",
                              resp if ok else f"Error: {resp}", ok)
                elif key == "optimise_schedule" and all_meds:
                    with st.spinner("Optimising schedule…"):
                        prompt   = ai.ai_suggest_schedule(list(all_meds.values()))
                        ok, resp = call_ai_with_feedback(prompt, ai.SYSTEM_HEALTH_ASSISTANT)
                    _add_chat("Suggest an optimised medication schedule.",
                              resp if ok else f"Error: {resp}", ok)
                elif key == "adherence_tips":
                    with st.spinner("Generating tips…"):
                        stats    = med_module.get_medicine_stats(user)
                        weekly   = med_module.get_weekly_adherence(user)
                        prompt   = ai.ai_adherence_insights(stats, weekly, list(all_meds.values()))
                        ok, resp = call_ai_with_feedback(prompt, ai.SYSTEM_HEALTH_ASSISTANT)
                    _add_chat("Give me adherence coaching tips.",
                              resp if ok else f"Error: {resp}", ok)
                st.rerun()

    st.markdown("---")

    for msg in st.session_state.get("ai_chat_history", []):
        role_icon = "🧑" if msg["role"] == "user" else "🤖"
        bg        = p["surface2"] if msg["role"] == "user" else p["surface"]
        border    = p["border"] if msg["role"] == "user" else p["primary"] + "55"
        rl        = t("you") if msg["role"] == "user" else t("ai")
        st.markdown(
            f"<div style='background:{bg};border:1px solid {border};border-radius:10px;"
            f"padding:12px 16px;margin:6px 0;'>"
            f"<span style='font-weight:700;color:{p['primary']}'>{role_icon} {rl}</span><br>"
            f"<span style='color:{p['text']}'>{msg['content']}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    user_input = st.text_area(
        "Ask a question…",
        placeholder=t("ask_placeholder"),
        height=100,
        key="ai_chat_input",
    )

    col_send, col_context = st.columns([2, 1])
    with col_context:
        include_meds = st.checkbox(t("include_meds"), value=True)
    with col_send:
        send_btn = st.button(t("send_btn"), key="ai_send_btn", type="primary",
                             use_container_width=True)

    if send_btn and user_input.strip():
        context = ""
        if include_meds and all_meds:
            med_summary = "\n".join(
                f"- {m['name']} {m['dosage']} ({m['frequency']})"
                for m in list(all_meds.values())[:15]
            )
            context = f"Patient's current medications:\n{med_summary}\n\n"

        with st.spinner(t("ai_thinking")):
            ok, resp = call_ai_with_feedback(
                context + user_input.strip(), ai.SYSTEM_HEALTH_ASSISTANT
            )
        _add_chat(user_input.strip(), resp if ok else f"Error: {resp}", ok)
        st.rerun()


def _add_chat(user_msg: str, ai_msg: str, ok: bool) -> None:  # noqa: F811
    hist = st.session_state.setdefault("ai_chat_history", [])
    hist.append({"role": "user",      "content": user_msg})
    hist.append({"role": "assistant", "content": ai_msg})
    if len(hist) > 40:
        st.session_state["ai_chat_history"] = hist[-40:]


# ── AI Settings ───────────────────────────────────────────────────────────────

def page_ai_settings() -> None:
    p = theme_mod.get_palette()
    st.markdown(f"<h2>{t('ai_settings_title')}</h2>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color:{p['text_muted']}'>{t('ai_settings_sub')}</p>",
        unsafe_allow_html=True,
    )

    st.markdown(f"<div class='section-title'>{t('ai_provider_label')}</div>",
                unsafe_allow_html=True)
    provider = st.selectbox(
        t("select_provider"),
        ai.ALL_PROVIDERS,
        index=ai.ALL_PROVIDERS.index(st.session_state["ai_provider"])
              if st.session_state["ai_provider"] in ai.ALL_PROVIDERS else 0,
        key="ai_provider_select",
    )
    if provider != st.session_state["ai_provider"]:
        st.session_state["ai_provider"] = provider
        # Reset model to provider default
        defaults = {
            ai.PROVIDER_OLLAMA:    "phi3:mini",
            ai.PROVIDER_GROQ:      "llama-3.3-70b-versatile",
            ai.PROVIDER_OPENAI:    "gpt-4o-mini",
            ai.PROVIDER_ANTHROPIC: "claude-haiku-4-5-20251001",
            ai.PROVIDER_GEMINI:    "gemini-2.0-flash",
        }
        st.session_state["ai_model"] = defaults.get(provider, "")
        st.rerun()

    st.markdown("---")

    # ── Ollama ────────────────────────────────────────────────────────────────
    if provider == ai.PROVIDER_OLLAMA:
        st.markdown("<div class='section-title'>🦙 Ollama - Local Inference</div>",
                    unsafe_allow_html=True)
        st.markdown(
            f"<div class='info-card'>"
            f"<b>Run AI completely offline</b> - no API keys required.<br>"
            f"Install: <code>https://ollama.com</code><br>"
            f"Then pull a model: <code>ollama pull llama3.2</code>"
            f"</div>",
            unsafe_allow_html=True,
        )
        ollama_url = st.text_input(t("ollama_url"), value=st.session_state["ollama_url"],
                                   placeholder="http://localhost:11434")
        st.session_state["ollama_url"] = ollama_url

        col_check, _ = st.columns([1, 2])
        with col_check:
            if st.button(t("test_connection"), key="test_ollama"):
                with st.spinner("Connecting…"):
                    running = ai.is_ollama_running(ollama_url)
                if running:
                    st.success("✅ Ollama is running!")
                else:
                    st.error("❌ Cannot reach Ollama. Is it running?")

        running = ai.is_ollama_running(ollama_url)
        if running:
            available = ai.get_ollama_models(ollama_url)
            if available:
                st.markdown(f"**Available models ({len(available)}):**")
                model = st.selectbox(
                    t("select_model"), available,
                    index=available.index(st.session_state["ai_model"])
                          if st.session_state["ai_model"] in available else 0,
                    key="ollama_model_sel",
                )
            else:
                st.warning("No models found. Pull one: `ollama pull llama3.2`")
                model = st.text_input("Or type model name manually",
                                      value=st.session_state["ai_model"],
                                      key="ollama_model_manual")
        else:
            model = st.selectbox(
                f"{t('select_model')} (will be used when Ollama starts)",
                ai.DEFAULT_OLLAMA_MODELS,
                index=ai.DEFAULT_OLLAMA_MODELS.index(st.session_state["ai_model"])
                      if st.session_state["ai_model"] in ai.DEFAULT_OLLAMA_MODELS else 0,
                key="ollama_model_offline",
            )
        st.session_state["ai_model"] = model

        st.markdown(
            f"<div class='info-card' style='margin-top:10px'>"
            f"💡 <b>Recommended:</b><br>"
            f"• <code>llama3.2</code> - Fast, general (3B)<br>"
            f"• <code>mistral</code> - Great reasoning (7B)<br>"
            f"• <code>llama3.1</code> - Best quality (8B)<br>"
            f"• <code>medllama2</code> - Medical fine-tune"
            f"</div>",
            unsafe_allow_html=True,
        )

    # ── Groq ──────────────────────────────────────────────────────────────────
    elif provider == ai.PROVIDER_GROQ:
        st.markdown("<div class='section-title'>⚡ Groq Cloud</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='info-card'>"
            f"Fast cloud inference - works great on Hugging Face Spaces.<br>"
            f"Get a free key at <b>console.groq.com</b>"
            f"</div>",
            unsafe_allow_html=True,
        )

        env_key = os.getenv("GROQ_API_KEY", "")
        if env_key:
            st.success("✅ GROQ_API_KEY found in environment (Space secret or .env)")
            st.info("The environment key is used automatically. You can also override it below.")
        else:
            st.warning("⚠️  No GROQ_API_KEY environment variable found.")
            st.info("On Hugging Face Spaces: add GROQ_API_KEY in Settings → Repository secrets.")

        manual_key = st.text_input(
            f"{t('api_key_label')} (override / BYOK)",
            value=st.session_state["ai_api_key"] if st.session_state["ai_api_key"] != env_key else "",
            type="password",
            placeholder="gsk_…",
            key="groq_api_key_input",
        )
        if manual_key:
            st.session_state["ai_api_key"] = manual_key
        elif env_key and not st.session_state["ai_api_key"]:
            st.session_state["ai_api_key"] = env_key

        model = st.selectbox(
            t("select_model"), ai.GROQ_MODELS,
            index=ai.GROQ_MODELS.index(st.session_state["ai_model"])
                  if st.session_state["ai_model"] in ai.GROQ_MODELS else 0,
            key="groq_model_sel",
        )
        st.session_state["ai_model"] = model

        if st.session_state["ai_api_key"]:
            col_test, _ = st.columns([1, 2])
            with col_test:
                if st.button(t("test_api_key"), key="test_groq"):
                    with st.spinner("Testing…"):
                        ok, resp = ai.call_groq(
                            "Reply with exactly: API key works!",
                            api_key=st.session_state["ai_api_key"],
                            model=model,
                        )
                    if ok:
                        st.success("✅ Groq API key is valid!")
                    else:
                        st.error(f"❌ {resp}")

    # ── OpenAI ────────────────────────────────────────────────────────────────
    elif provider == ai.PROVIDER_OPENAI:
        st.markdown("<div class='section-title'>🔑 OpenAI - Bring Your Own Key</div>",
                    unsafe_allow_html=True)
        api_key = st.text_input(
            f"OpenAI {t('api_key_label')}",
            value=st.session_state["ai_api_key"],
            type="password", placeholder="sk-…",
        )
        st.session_state["ai_api_key"] = api_key

        model = st.selectbox(
            t("select_model"), ai.OPENAI_MODELS,
            index=ai.OPENAI_MODELS.index(st.session_state["ai_model"])
                  if st.session_state["ai_model"] in ai.OPENAI_MODELS else 0,
            key="openai_model_sel",
        )
        st.session_state["ai_model"] = model

        if api_key:
            col_test, _ = st.columns([1, 2])
            with col_test:
                if st.button(t("test_api_key"), key="test_openai"):
                    with st.spinner("Testing…"):
                        ok, resp = ai.call_openai("Say: API key works!", api_key=api_key, model=model)
                    st.success("✅ API key is valid!") if ok else st.error(f"❌ {resp}")
        else:
            st.info("Get your key at https://platform.openai.com/api-keys")

    # ── Anthropic ─────────────────────────────────────────────────────────────
    elif provider == ai.PROVIDER_ANTHROPIC:
        st.markdown("<div class='section-title'>🔑 Anthropic Claude - Bring Your Own Key</div>",
                    unsafe_allow_html=True)
        api_key = st.text_input(
            f"Anthropic {t('api_key_label')}",
            value=st.session_state["ai_api_key"],
            type="password", placeholder="sk-ant-…",
        )
        st.session_state["ai_api_key"] = api_key

        model = st.selectbox(
            t("select_model"), ai.ANTHROPIC_MODELS,
            index=ai.ANTHROPIC_MODELS.index(st.session_state["ai_model"])
                  if st.session_state["ai_model"] in ai.ANTHROPIC_MODELS else 0,
            key="anthropic_model_sel",
        )
        st.session_state["ai_model"] = model

        if api_key:
            col_test, _ = st.columns([1, 2])
            with col_test:
                if st.button(t("test_api_key"), key="test_anthropic"):
                    with st.spinner("Testing…"):
                        ok, resp = ai.call_anthropic("Say: API key works!", api_key=api_key, model=model)
                    st.success("✅ API key is valid!") if ok else st.error(f"❌ {resp}")
        else:
            st.info("Get your key at https://console.anthropic.com")

    # ── Gemini ────────────────────────────────────────────────────────────────
    elif provider == ai.PROVIDER_GEMINI:
        st.markdown("<div class='section-title'>🔑 Google Gemini - Bring Your Own Key</div>",
                    unsafe_allow_html=True)
        api_key = st.text_input(
            f"Gemini {t('api_key_label')}",
            value=st.session_state["ai_api_key"],
            type="password", placeholder="AIza…",
        )
        st.session_state["ai_api_key"] = api_key

        model = st.selectbox(
            t("select_model"), ai.GEMINI_MODELS,
            index=ai.GEMINI_MODELS.index(st.session_state["ai_model"])
                  if st.session_state["ai_model"] in ai.GEMINI_MODELS else 0,
            key="gemini_model_sel",
        )
        st.session_state["ai_model"] = model

        if api_key:
            col_test, _ = st.columns([1, 2])
            with col_test:
                if st.button(t("test_api_key"), key="test_gemini"):
                    with st.spinner("Testing…"):
                        ok, resp = ai.call_gemini("Say: API key works!", api_key=api_key, model=model)
                    st.success("✅ API key is valid!") if ok else st.error(f"❌ {resp}")
        else:
            st.info("Get your key at https://aistudio.google.com/apikey")

    st.markdown("---")
    st.markdown(
        f"<div class='info-card'>{t('privacy_note')}</div>",
        unsafe_allow_html=True,
    )


# ── Profiles (family/patient management) ────────────────────────────────────

def page_profiles() -> None:
    p = theme_mod.get_palette()
    st.markdown("<h2>👨‍👩‍👧 Patient / Family Profiles</h2>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color:{p['text_muted']}'>Manage medicines for yourself and your "
        f"family members from one account. Switch the active profile from the sidebar.</p>",
        unsafe_allow_html=True,
    )

    username     = st.session_state["username"]
    all_profiles = profiles_module.list_profiles(username)
    edit_id      = st.session_state.get("edit_profile_id")
    editing      = profiles_module.get_profile(username, edit_id) if edit_id else None

    st.markdown("---")
    st.markdown(f"<div class='section-title'>{'✏️ Edit Profile' if editing else '➕ Add a Profile'}</div>",
                unsafe_allow_html=True)

    with st.form("profile_form", clear_on_submit=not editing):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name", value=editing["name"] if editing else "")
            age  = st.text_input("Age", value=editing["age"] if editing else "")
        with col2:
            rel_options = profiles_module.RELATIONS
            rel_index   = rel_options.index(editing["relation"]) if editing and editing["relation"] in rel_options else 0
            relation = st.selectbox("Relation", rel_options, index=rel_index)
            gender   = st.selectbox(
                "Gender", ["", "Male", "Female", "Other"],
                index=(["", "Male", "Female", "Other"].index(editing["gender"])
                       if editing and editing.get("gender") in ["", "Male", "Female", "Other"] else 0),
            )

        col_save, col_cancel = st.columns([1, 1])
        with col_save:
            submitted = st.form_submit_button(
                "💾 Update Profile" if editing else "➕ Add Profile",
                use_container_width=True, type="primary",
            )
        with col_cancel:
            cancelled = editing and st.form_submit_button("✖️ Cancel", use_container_width=True)

        if cancelled:
            st.session_state["edit_profile_id"] = None
            st.rerun()

        if submitted:
            if editing:
                ok, msg = profiles_module.update_profile(username, edit_id, name, relation, age, gender)
            else:
                ok, msg, _ = profiles_module.create_profile(username, name, relation, age, gender)
            if ok:
                st.success(msg)
                st.session_state["edit_profile_id"] = None
                st.rerun()
            else:
                st.error(msg)

    st.markdown("---")
    st.markdown(f"<div class='section-title'>All Profiles ({len(all_profiles)})</div>",
                unsafe_allow_html=True)

    for pid, prof in all_profiles.items():
        is_active = pid == st.session_state["active_profile_id"]
        med_count = len(med_module.get_all_medicines(profiles_module.profile_key(username, pid)))

        with st.container():
            col_info, col_switch, col_edit, col_del = st.columns([3, 1, 1, 1])
            with col_info:
                star = "⭐ " if is_active else ""
                st.markdown(
                    f"<div class='info-card'>{star}<b>{prof['name']}</b> - {prof['relation']}"
                    f"<br><span style='color:{p['text_muted']};font-size:0.85rem'>"
                    f"{prof.get('age','?')} yrs &nbsp;|&nbsp; {med_count} medicine(s)</span></div>",
                    unsafe_allow_html=True,
                )
            with col_switch:
                if not is_active and st.button("Switch", key=f"switch_{pid}"):
                    st.session_state["active_profile_id"] = pid
                    st.session_state["page"] = "Dashboard"
                    st.rerun()
            with col_edit:
                if st.button("✏️", key=f"edit_{pid}"):
                    st.session_state["edit_profile_id"] = pid
                    st.rerun()
            with col_del:
                if len(all_profiles) > 1 and st.button("🗑️", key=f"del_{pid}"):
                    ok, msg = profiles_module.delete_profile(username, pid)
                    if ok and is_active:
                        st.session_state["active_profile_id"] = next(iter(
                            profiles_module.list_profiles(username)
                        ))
                    st.success(msg) if ok else st.error(msg)
                    st.rerun()


# ── Reminders (settings + due list) ──────────────────────────────────────────

def page_reminders() -> None:
    p = theme_mod.get_palette()
    st.markdown("<h2>🔔 Dosage Reminders</h2>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color:{p['text_muted']}'>Get alerted when a dose is due for "
        f"<b>{active_profile_name()}</b> — as a desktop notification and an on-screen "
        f"banner on the Dashboard. Keep this browser tab open for reminders to keep firing.</p>",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown(f"<div class='section-title'>Settings</div>", unsafe_allow_html=True)

    enabled = st.toggle("Enable reminders", value=st.session_state["reminders_enabled"])
    sound   = st.toggle("Play a sound with each alert", value=st.session_state["reminder_sound"])

    window_minutes = st.slider(
        "Alert me this many minutes before a dose is due",
        min_value=0, max_value=60, step=5,
        value=st.session_state["reminder_window_minutes"],
    )
    refresh_seconds = st.slider(
        "Check for due doses every (seconds)",
        min_value=30, max_value=300, step=30,
        value=st.session_state["reminder_refresh_seconds"],
    )

    if st.button("💾 Save Settings", type="primary"):
        st.session_state["reminders_enabled"]        = enabled
        st.session_state["reminder_sound"]            = sound
        st.session_state["reminder_window_minutes"]   = window_minutes
        st.session_state["reminder_refresh_seconds"]  = refresh_seconds
        st.success("✅ Reminder settings saved.")
        st.rerun()

    st.markdown("---")
    st.markdown(
        f"<div class='info-card'>🔓 The first time reminders run, your browser will ask "
        f"permission to show notifications — click <b>Allow</b>. If you accidentally "
        f"clicked Block, you can re-enable it from your browser's site settings for "
        f"this page.</div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown(f"<div class='section-title'>Due Right Now</div>", unsafe_allow_html=True)
    schedule = med_module.get_today_schedule(active_profile_key())
    due = reminders_module.get_due_now(schedule, st.session_state["reminder_window_minutes"])

    if not due:
        st.info("Nothing due right now. ✅")
    else:
        for slot in due:
            when = "overdue" if slot["overdue"] else f"in {slot['minutes_until']} min"
            st.markdown(
                f"<div class='info-card'>💊 <b>{slot['name']}</b> ({slot['dosage']}) "
                f"— {slot['time']} ({when})</div>",
                unsafe_allow_html=True,
            )


# ── Automatic Patient Medication Report (PDF) ────────────────────────────────

def page_report() -> None:
    p = theme_mod.get_palette()
    st.markdown("<h2>📑 Medication Report</h2>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color:{p['text_muted']}'>Generate a printable PDF summary for "
        f"<b>{active_profile_name()}</b> — current medicines, today's adherence, and "
        f"the last 7 days of dose history. Handy to bring along to a doctor's visit.</p>",
        unsafe_allow_html=True,
    )

    username = st.session_state["username"]
    profile  = profiles_module.get_profile(username, st.session_state["active_profile_id"])
    user_key = active_profile_key()

    medicines        = med_module.get_active_medicines(user_key)
    stats            = med_module.get_medicine_stats(user_key)
    weekly_adherence = med_module.get_weekly_adherence(user_key)

    st.markdown("---")
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Active Medicines", stats["total_medicines"])
    col_b.metric("Today's Adherence", f"{stats['adherence_pct']}%")
    col_c.metric("Doses Today", stats["today_total"])
    st.markdown("---")

    if st.button("📑 Generate PDF Report", type="primary", use_container_width=True):
        with st.spinner("Building report..."):
            pdf_bytes = reports_module.generate_medication_report(
                profile=profile,
                account_username=username,
                medicines=medicines,
                stats=stats,
                weekly_adherence=weekly_adherence,
            )
        st.session_state["_report_pdf"] = pdf_bytes
        st.success("✅ Report ready — download it below.")

    if st.session_state.get("_report_pdf"):
        filename = f"medication_report_{profile['name'].replace(' ', '_')}_{date.today().isoformat()}.pdf"
        st.download_button(
            "⬇️ Download PDF",
            data=st.session_state["_report_pdf"],
            file_name=filename,
            mime="application/pdf",
            use_container_width=True,
        )


# ── Appointments (doctor/clinic visit tracker) ───────────────────────────────

def page_appointments() -> None:
    p = theme_mod.get_palette()
    st.markdown("<h2>📅 Appointments</h2>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color:{p['text_muted']}'>Track upcoming and past doctor/clinic visits for "
        f"<b>{active_profile_name()}</b>.</p>",
        unsafe_allow_html=True,
    )

    user_key = active_profile_key()
    edit_id  = st.session_state.get("edit_appt_id")
    editing  = appt_module.get_all_appointments(user_key).get(edit_id) if edit_id else None

    st.markdown("---")
    st.markdown(f"<div class='section-title'>{'✏️ Edit Appointment' if editing else '➕ Add an Appointment'}</div>",
                unsafe_allow_html=True)

    with st.form("appt_form", clear_on_submit=not editing):
        doctor = st.text_input("Doctor / Clinic", value=editing["doctor"] if editing else "",
                                placeholder="e.g. Dr. Rao — Cardiologist")
        col1, col2 = st.columns(2)
        with col1:
            appt_date = st.date_input(
                "Date",
                value=datetime.strptime(editing["date"], "%Y-%m-%d").date() if editing else date.today(),
            )
        with col2:
            appt_time = st.time_input(
                "Time",
                value=datetime.strptime(editing["time"], "%H:%M").time() if editing else datetime.strptime("09:00", "%H:%M").time(),
            )
        notes = st.text_area("Notes (optional)", value=editing["notes"] if editing else "",
                              placeholder="e.g. Bring previous reports", height=70)

        col_save, col_cancel = st.columns([1, 1])
        with col_save:
            submitted = st.form_submit_button(
                "💾 Update Appointment" if editing else "➕ Add Appointment",
                use_container_width=True, type="primary",
            )
        with col_cancel:
            cancelled = editing and st.form_submit_button("✖️ Cancel", use_container_width=True)

        if cancelled:
            st.session_state["edit_appt_id"] = None
            st.rerun()

        if submitted:
            if editing:
                ok, msg = appt_module.update_appointment(
                    user_key, edit_id, doctor, appt_date.isoformat(), appt_time.strftime("%H:%M"), notes,
                )
            else:
                ok, msg = appt_module.add_appointment(
                    user_key, doctor, appt_date.isoformat(), appt_time.strftime("%H:%M"), notes,
                )
            if ok:
                st.success(msg)
                st.session_state["edit_appt_id"] = None
                st.rerun()
            else:
                st.error(msg)

    st.markdown("---")
    st.markdown(f"<div class='section-title'>🗓️ Upcoming</div>", unsafe_allow_html=True)
    upcoming = appt_module.get_upcoming_appointments(user_key)
    if not upcoming:
        st.info("No upcoming appointments.")
    else:
        for a in upcoming:
            _render_appt_card(a, is_past=False, p=p)

    st.markdown("---")
    st.markdown(f"<div class='section-title'>✅ Past</div>", unsafe_allow_html=True)
    past = appt_module.get_past_appointments(user_key)
    if not past:
        st.info("No past appointments on record.")
    else:
        for a in past:
            _render_appt_card(a, is_past=True, p=p)


def _render_appt_card(a: dict, is_past: bool, p: dict) -> None:
    user_key = active_profile_key()
    when = datetime.strptime(a["date"], "%Y-%m-%d").strftime("%a, %d %b %Y") + " · " + \
        datetime.strptime(a["time"], "%H:%M").strftime("%I:%M %p")
    icon = "✅" if is_past else "🗓️"
    col_info, col_edit, col_del = st.columns([5, 1, 1])
    with col_info:
        notes_line = f"<br><span style='color:{p['text_muted']};font-size:0.82rem'>📝 {a['notes']}</span>" if a.get("notes") else ""
        st.markdown(
            f"<div class='info-card'>{icon} <b>{a['doctor']}</b><br>"
            f"<span style='color:{p['text_muted']}'>{when}</span>{notes_line}</div>",
            unsafe_allow_html=True,
        )
    with col_edit:
        if st.button("✏️", key=f"edit_appt_{a['id']}"):
            st.session_state["edit_appt_id"] = a["id"]
            st.rerun()
    with col_del:
        if st.button("🗑️", key=f"del_appt_{a['id']}"):
            ok, msg = appt_module.delete_appointment(user_key, a["id"])
            st.success(msg) if ok else st.error(msg)
            st.rerun()


# ── Main router ───────────────────────────────────────────────────────────────

def main() -> None:
    init_session()
    os.makedirs("data", exist_ok=True)
    theme_mod.inject_theme()

    if not st.session_state["logged_in"]:
        page_auth()
        return

    render_sidebar()
    render_reminder_engine()

    dispatch = {
        "Dashboard":    page_dashboard,
        "Add Medicine": page_add_medicine,
        "My Medicines": page_my_medicines,
        "OCR Scanner":  page_ocr_scanner,
        "Analytics":    page_analytics,
        "AI Assistant": page_ai_assistant,
        "AI Settings":  page_ai_settings,
        "Profiles":     page_profiles,
        "Reminders":    page_reminders,
        "Appointments": page_appointments,
        "Report":       page_report,
    }
    dispatch.get(st.session_state["page"], page_dashboard)()


if __name__ == "__main__":
    main()

