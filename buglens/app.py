"""
BugLens — Defect Quality Checker
Redesigned Streamlit frontend: clean, modern, enterprise-grade UI.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import plotly.express as px
import streamlit as st

try:
    from .modules import BugLensStore, DefectAnalyzer, send_email_report, smtp_configuration_status
    from .ui import (
        NAV_PAGES,
        inject_theme,
        render_auth_hero,
        render_chip,
        render_empty_state,
        render_info_card,
        render_issue_item,
        render_metric_cards,
        render_nav_card,
        render_nav_item_active,
        render_score_card,
        render_section_header,
    )
except ImportError:
    try:
        from modules import BugLensStore, DefectAnalyzer, send_email_report, smtp_configuration_status
        from ui import (
            NAV_PAGES,
            inject_theme,
            render_auth_hero,
            render_chip,
            render_empty_state,
            render_info_card,
            render_issue_item,
            render_metric_cards,
            render_nav_card,
            render_nav_item_active,
            render_score_card,
            render_section_header,
        )
    except ImportError:
        from buglens.modules import BugLensStore, DefectAnalyzer, send_email_report, smtp_configuration_status
        from buglens.ui import (
            NAV_PAGES,
            inject_theme,
            render_auth_hero,
            render_chip,
            render_empty_state,
            render_info_card,
            render_issue_item,
            render_metric_cards,
            render_nav_card,
            render_nav_item_active,
            render_score_card,
            render_section_header,
        )


APP_TITLE = "BugLens — Defect Quality Checker"
DEFAULT_MODEL = "gpt-4o-mini"
PAGE_SEQUENCE = ["dashboard", "analyze", "history", "compare", "settings"]

ROLES = [
    "QA Engineer",
    "QA Lead",
    "Developer",
    "Analyst",
    "Product Manager",
    "Support Engineer",
    "DevOps",
]

DEMO_ACCOUNTS = [
    {
        "name": "Maya Chen",
        "role": "QA Lead",
        "username": "maya",
        "password": "maya123",
        "focus": "Release readiness and defect triage",
    },
    {
        "name": "Ravi Patel",
        "role": "Backend Engineer",
        "username": "ravi",
        "password": "ravi123",
        "focus": "API regressions and logs",
    },
    {
        "name": "Nina Brooks",
        "role": "Product Analyst",
        "username": "nina",
        "password": "nina123",
        "focus": "Customer-impact review",
    },
    {
        "name": "Omar Silva",
        "role": "Support Triage",
        "username": "omar",
        "password": "omar123",
        "focus": "Fast ticket cleanup for incoming bugs",
    },
]

DATA_DIR = Path(__file__).parent / "data"
SAMPLES_FILE = DATA_DIR / "sample_defects.json"
SMTP_CONFIG_PATH = Path(__file__).parent / "smtp_config.json"
_STORE = BugLensStore()

EMPTY_FORM_DATA: Dict[str, str] = {
    "title": "",
    "description": "",
    "steps_to_reproduce": "",
    "expected_result": "",
    "actual_result": "",
    "environment": "",
    "severity": "",
}

FORM_FIELD_KEYS = {
    "title": "defect_title",
    "description": "defect_description",
    "steps_to_reproduce": "defect_steps_to_reproduce",
    "expected_result": "defect_expected_result",
    "actual_result": "defect_actual_result",
    "environment": "defect_environment",
    "severity": "defect_severity",
}

# ─────────────────────────────────────────────
#  Plotly chart theme
# ─────────────────────────────────────────────

def _apply_chart_theme(fig: Any, height: int = 300) -> Any:
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
            size=11,
            color="#64748b",
        ),
        height=height,
        margin=dict(t=10, l=0, r=0, b=0),
        xaxis=dict(showgrid=False, showline=False, tickfont=dict(color="#94a3b8", size=10)),
        yaxis=dict(
            gridcolor="#f1f5f9",
            gridwidth=1,
            showline=False,
            tickfont=dict(color="#94a3b8", size=10),
            zeroline=False,
        ),
        legend=dict(font=dict(size=11, color="#64748b"), bgcolor="rgba(0,0,0,0)"),
    )
    return fig


# ─────────────────────────────────────────────
#  State helpers
# ─────────────────────────────────────────────

def init_state() -> None:
    if "logged_in" not in st.session_state:
        st.session_state.update(
            {
                "logged_in": False,
                "current_user": "",
                "auth_view": "login",
                "auth_error": "",
                "auth_notice": "",
                "user_directory": {
                    a["username"]: {
                        "password": a["password"],
                        "name": a["name"],
                        "role": a["role"],
                        "focus": a["focus"],
                        "is_demo": True,
                    }
                    for a in DEMO_ACCOUNTS
                },
                "page": "dashboard",
                "analysis_history": load_persisted_history(),
                "analysis_result": None,
                "analysis_payload": None,
                "recipient_email": "",
                "preferred_model": DEFAULT_MODEL,
                "default_landing_page": "dashboard",
                "compare_left_id": "",
                "compare_right_id": "",
                "defect_form_version": 0,
                "form_data": EMPTY_FORM_DATA.copy(),
            }
        )


def ensure_form_version() -> None:
    if "defect_form_version" not in st.session_state:
        st.session_state["defect_form_version"] = 0


def widget_key(field: str) -> str:
    ensure_form_version()
    return f"{FORM_FIELD_KEYS[field]}_{st.session_state['defect_form_version']}"


def set_page(page: str) -> None:
    st.session_state["page"] = page


def authenticate(username: str, password: str) -> bool:
    account = st.session_state["user_directory"].get(username)
    return bool(account and account["password"] == password)


def login_user(username: str) -> None:
    st.session_state.update(
        {
            "logged_in": True,
            "current_user": username,
            "auth_error": "",
            "auth_notice": "",
            "page": st.session_state.get("default_landing_page", "dashboard"),
        }
    )


def logout_user() -> None:
    st.session_state.update(
        {
            "logged_in": False,
            "current_user": "",
            "auth_view": "login",
            "auth_error": "",
            "auth_notice": "",
            "page": "dashboard",
        }
    )


def signup(name: str, username: str, password: str, role: str) -> dict:
    clean_name = name.strip()
    clean_user = username.strip().lower()
    if not clean_name or not clean_user or not password:
        return {"ok": False, "error": "Name, username, and password are required."}
    if len(clean_user) < 3:
        return {"ok": False, "error": "Username must be at least 3 characters."}
    if len(password) < 6:
        return {"ok": False, "error": "Password must be at least 6 characters."}
    if clean_user in st.session_state["user_directory"]:
        return {"ok": False, "error": "That username is already taken."}
    st.session_state["user_directory"][clean_user] = {
        "password": password,
        "name": clean_name,
        "role": role.strip(),
        "focus": "Personal workspace",
        "is_demo": False,
    }
    return {"ok": True, "username": clean_user}


def load_samples() -> list:
    if not SAMPLES_FILE.exists():
        return []
    with SAMPLES_FILE.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def load_persisted_history(limit: int = 24) -> list:
    try:
        return _STORE.list_analyses(limit=limit)
    except Exception:
        return []


@st.cache_data
def cached_samples() -> list:
    return load_samples()


def sync_form_state(data: Optional[dict] = None, *, reset_widgets: bool = False) -> None:
    source = EMPTY_FORM_DATA.copy()
    if data:
        source.update(data)
    st.session_state["form_data"] = source.copy()
    if reset_widgets:
        st.session_state["defect_form_version"] = (
            st.session_state.get("defect_form_version", 0) + 1
        )


def clear_analysis_form() -> None:
    sync_form_state(reset_widgets=True)
    st.session_state["analysis_result"] = None
    st.session_state["analysis_payload"] = None
    st.session_state["recipient_email"] = ""


def load_sample_defect(sample_name: str, samples: list, *, page: str | None = None) -> bool:
    if not sample_name or sample_name.startswith("—"):
        return False
    chosen = next((s for s in samples if s["name"] == sample_name), None)
    if not chosen:
        return False
    sync_form_state(chosen["data"], reset_widgets=True)
    st.session_state["active_sample_name"] = sample_name
    if page:
        set_page(page)
    return True


def issue_summary(issues: List[Any]) -> Dict[str, int]:
    counts: Dict[str, int] = {"error": 0, "warning": 0, "info": 0}
    for issue in issues:
        counts[issue.severity] = counts.get(issue.severity, 0) + 1
    return counts


def severity_tone(severity: str) -> str:
    return {
        "error": "danger",
        "warning": "warning",
        "info": "info",
        "blocker": "danger",
        "critical": "danger",
        "major": "warning",
        "minor": "info",
        "trivial": "neutral",
    }.get(severity, "neutral")


def score_tone(score: int) -> str:
    if score >= 85:
        return "success"
    if score >= 70:
        return "primary"
    if score >= 55:
        return "warning"
    if score >= 40:
        return "warning"
    return "danger"


def latest_history_entry() -> Optional[dict]:
    history = st.session_state.get("analysis_history", [])
    return history[-1] if history else None


def clear_workspace_history() -> None:
    st.session_state.update(
        {
            "analysis_history": [],
            "analysis_result": None,
            "analysis_payload": None,
            "compare_left_id": "",
            "compare_right_id": "",
        }
    )
    try:
        _STORE.clear_analyses()
    except Exception:
        pass


def register_analysis(payload: dict, result: Any) -> None:
    try:
        entry = _STORE.save_analysis(payload, result)
    except Exception:
        counts = issue_summary(result.issues)
        entry = {
            "id": uuid.uuid4().hex[:10],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "payload": payload.copy(),
            "result": result,
            "title": payload.get("title", "").strip() or "Untitled defect",
            "score": result.score.total,
            "grade": result.score.grade,
            "verdict": result.score.verdict,
            "issue_count": len(result.issues),
            "error_count": issue_summary(result.issues)["error"],
            "warning_count": issue_summary(result.issues)["warning"],
            "info_count": issue_summary(result.issues)["info"],
        }
    history = st.session_state.setdefault("analysis_history", [])
    history.append(entry)
    st.session_state["compare_left_id"] = entry["id"]
    if not st.session_state.get("compare_right_id"):
        st.session_state["compare_right_id"] = entry["id"]
    if len(history) > 24:
        del history[:-24]


def compare_entry_by_id(entry_id: str) -> Optional[dict]:
    for entry in st.session_state.get("analysis_history", []):
        if entry["id"] == entry_id:
            return entry
    return None


def current_profile() -> dict:
    username = st.session_state.get("current_user", "")
    return st.session_state.get("user_directory", {}).get(username, {})


def save_smtp_settings(payload: dict) -> None:
    with SMTP_CONFIG_PATH.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
    for key, value in payload.items():
        if value:
            os.environ[key] = value


def clear_smtp_settings() -> None:
    if SMTP_CONFIG_PATH.exists():
        SMTP_CONFIG_PATH.unlink()
    for key in ("SMTP_HOST", "SMTP_PORT", "SMTP_USERNAME", "SMTP_PASSWORD", "SMTP_FROM", "SMTP_USE_TLS"):
        os.environ.pop(key, None)


# ─────────────────────────────────────────────
#  Auth page
# ─────────────────────────────────────────────

def render_auth_page() -> None:
    features = [
        {
            "icon": "🎯",
            "title": "Real-time scoring",
            "body": "Score reports instantly with a deterministic 6-section rubric and letter grade.",
        },
        {
            "icon": "✦",
            "title": "AI + rules",
            "body": "A local rule engine works offline; attach an OpenAI key for GPT-powered rewrites.",
        },
        {
            "icon": "⇄",
            "title": "Compare & iterate",
            "body": "Place two defect reports side by side and see the score delta at a glance.",
        },
    ]

    render_auth_hero(
        "Sharpen defect reports before they reach engineering.",
        "Score, validate, and rewrite bug reports into polished, developer-ready tickets.",
        features,
    )

    col_info, col_form = st.columns([1.1, 0.9], gap="large")

    with col_info:
        st.markdown("#### What you can do")
        st.markdown(
            "- Catch missing fields, vague language, and unnumbered steps instantly.\n"
            "- Get a 0–100 quality score with per-section breakdown.\n"
            "- Compare two defect reports side by side.\n"
            "- Download or email a professionally rewritten ticket."
        )
        st.markdown("#### Demo accounts")
        for account in DEMO_ACCOUNTS:
            initial = account["name"][0].upper()
            st.markdown(
                f'<div class="bl-demo-card">'
                f'  <div class="bl-demo-avatar">{initial}</div>'
                f'  <div>'
                f'    <div class="bl-demo-name">{account["name"]}</div>'
                f'    <div class="bl-demo-role">{account["role"]} · {account["focus"]}</div>'
                f'  </div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            if st.button(
                f"Sign in as {account['username']}",
                key=f"demo_login_{account['username']}",
                use_container_width=True,
            ):
                login_user(account["username"])
                st.rerun()

    with col_form:
        st.markdown('<div class="bl-auth-form-panel">', unsafe_allow_html=True)

        view = st.session_state["auth_view"]
        tab_cols = st.columns(2)
        with tab_cols[0]:
            if st.button(
                "Login",
                key="auth_login_tab",
                use_container_width=True,
                type="primary" if view == "login" else "secondary",
            ):
                st.session_state.update({"auth_view": "login", "auth_error": "", "auth_notice": ""})
        with tab_cols[1]:
            if st.button(
                "Sign Up",
                key="auth_signup_tab",
                use_container_width=True,
                type="primary" if view == "signup" else "secondary",
            ):
                st.session_state.update({"auth_view": "signup", "auth_error": "", "auth_notice": ""})

        if st.session_state["auth_notice"]:
            st.success(st.session_state["auth_notice"])
        if st.session_state["auth_error"]:
            st.error(st.session_state["auth_error"])

        if view == "login":
            st.markdown("##### Welcome back")
            st.caption("Use a demo account or your own credentials.")
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="maya")
                password = st.text_input("Password", type="password", placeholder="Enter password")
                submitted = st.form_submit_button("Enter BugLens →", use_container_width=True)
                if submitted:
                    clean = username.strip().lower()
                    if authenticate(clean, password):
                        login_user(clean)
                        st.rerun()
                    st.session_state.update(
                        {"auth_error": "Invalid username or password.", "auth_notice": ""}
                    )
                    st.rerun()
        else:
            st.markdown("##### Create a profile")
            st.caption("New accounts are workspace-scoped — no email required.")
            with st.form("signup_form"):
                full_name = st.text_input("Full name", placeholder="Aarav Singh")
                username = st.text_input("Username", placeholder="aarav")
                role = st.selectbox("Role", ROLES)
                password = st.text_input("Password", type="password", placeholder="At least 6 characters")
                submitted = st.form_submit_button("Create account", use_container_width=True)
                if submitted:
                    res = signup(full_name, username, password, role)
                    if res["ok"]:
                        st.session_state.update(
                            {
                                "auth_view": "login",
                                "auth_notice": f"Account created for {full_name.strip()}. Sign in with @{res['username']}.",
                                "auth_error": "",
                            }
                        )
                        st.rerun()
                    st.session_state.update({"auth_error": res["error"], "auth_notice": ""})
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()


# ─────────────────────────────────────────────
#  Sidebar
# ─────────────────────────────────────────────

def render_sidebar() -> None:
    profile = current_profile()
    current_page = st.session_state.get("page", "dashboard")
    history = st.session_state.get("analysis_history", [])
    samples = cached_samples()

    with st.sidebar:
        # Brand wordmark
        st.markdown(
            '<div class="bl-sb-wordmark">'
            '  <div class="bl-sb-logo-text">🪲 BugLens</div>'
            '  <div class="bl-sb-logo-sub">Defect quality workspace</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        # User profile
        initial = profile.get("name", "?")[0].upper()
        st.markdown(
            f'<div class="bl-sb-profile">'
            f'  <div class="bl-sb-avatar">{initial}</div>'
            f'  <div>'
            f'    <div class="bl-sb-name">{profile.get("name","Unknown")}</div>'
            f'    <div class="bl-sb-role">{profile.get("role","")}</div>'
            f'  </div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if st.button("↩  Sign out", key="logout_btn", use_container_width=True):
            logout_user()
            st.rerun()

        # Navigation
        st.markdown('<div class="bl-sb-sep"></div>', unsafe_allow_html=True)
        st.markdown('<div class="bl-sb-section">Navigation</div>', unsafe_allow_html=True)

        for page_id in PAGE_SEQUENCE:
            meta = NAV_PAGES[page_id]
            if current_page == page_id:
                render_nav_item_active(meta["icon"], meta["label"], meta["subtitle"])
            else:
                if st.button(
                    f"{meta['icon']}  {meta['label']}",
                    key=f"nav_{page_id}",
                    use_container_width=True,
                ):
                    set_page(page_id)
                    st.rerun()

        # Workspace — model + mode
        st.markdown('<div class="bl-sb-sep"></div>', unsafe_allow_html=True)
        st.markdown('<div class="bl-sb-section">Workspace</div>', unsafe_allow_html=True)

        model_options = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
        model_choice = st.selectbox(
            "AI model",
            options=model_options,
            index=model_options.index(st.session_state.get("preferred_model", DEFAULT_MODEL)),
            key="sidebar_model_choice",
        )
        st.session_state["preferred_model"] = model_choice

        ai_active = bool(os.getenv("OPENAI_API_KEY"))
        dot_cls = "ok" if ai_active else "warn"
        mode_label = "AI rewrite active" if ai_active else "Local rewrite mode"
        st.markdown(
            f'<div style="font-size:0.78rem; color:var(--sb-muted); padding:3px 0 8px; display:flex; align-items:center; gap:5px;">'
            f'  <span class="bl-sb-dot {dot_cls}"></span>{mode_label}'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Quick stats
        latest = history[-1] if history else None
        latest_score_str = f"{latest['score']}/100" if latest else "—"
        st.markdown(
            f'<div class="bl-sb-stat">'
            f'  <div class="bl-sb-stat-label">Analyses this session</div>'
            f'  <div class="bl-sb-stat-value">{len(history)}</div>'
            f'</div>'
            f'<div class="bl-sb-stat">'
            f'  <div class="bl-sb-stat-label">Latest score</div>'
            f'  <div class="bl-sb-stat-value">{latest_score_str}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Sample loader
        st.markdown('<div class="bl-sb-sep"></div>', unsafe_allow_html=True)
        st.markdown('<div class="bl-sb-section">Sample defects</div>', unsafe_allow_html=True)

        sample_choice = st.selectbox(
            "Pick a sample",
            options=["— blank form —"] + [s["name"] for s in samples],
            index=0,
            key="sidebar_sample_choice",
            label_visibility="collapsed",
        )
        scols = st.columns(2)
        with scols[0]:
            if st.button("Load", use_container_width=True, key="sb_load_sample"):
                if load_sample_defect(sample_choice, samples, page="analyze"):
                    st.rerun()
                else:
                    st.warning("Pick a sample first.")
        with scols[1]:
            if st.button("Clear", use_container_width=True, key="sb_clear_sample"):
                sync_form_state(reset_widgets=True)
                set_page("analyze")
                st.rerun()

        # Delivery status
        st.markdown('<div class="bl-sb-sep"></div>', unsafe_allow_html=True)
        smtp_ok, smtp_missing = smtp_configuration_status()
        dot = "ok" if smtp_ok else "warn"
        smtp_label = "SMTP ready" if smtp_ok else "SMTP not configured"
        st.markdown(
            f'<div style="font-size:0.8rem; color:var(--sb-muted); padding:4px 0;">'
            f'  <span class="bl-sb-dot {dot}"></span>{smtp_label}'
            f'</div>',
            unsafe_allow_html=True,
        )
        if not smtp_ok and smtp_missing:
            st.caption("Missing: " + ", ".join(smtp_missing))


# ─────────────────────────────────────────────
#  Dashboard
# ─────────────────────────────────────────────

def render_dashboard() -> None:
    history = st.session_state.get("analysis_history", [])
    profile = current_profile()
    latest = latest_history_entry()

    render_section_header(
        "Dashboard",
        "Track defect quality trends and jump back into your workflow.",
        "◈",
    )

    # Metric row
    render_metric_cards(
        [
            {
                "icon": "📋",
                "label": "Reports analyzed",
                "value": len(history),
                "caption": "Saved in this session.",
                "tone": "primary",
            },
            {
                "icon": "🎯",
                "label": "Latest score",
                "value": f"{latest['score']}/100" if latest else "—",
                "caption": "Most recent analysis.",
                "tone": score_tone(latest["score"]) if latest else "neutral",
            },
            {
                "icon": "★",
                "label": "Latest grade",
                "value": latest["grade"] if latest else "—",
                "caption": latest["verdict"] if latest else "No analysis yet.",
                "tone": score_tone(latest["score"]) if latest else "neutral",
            },
            {
                "icon": "△",
                "label": "Open issues",
                "value": latest["issue_count"] if latest else 0,
                "caption": "Issues in the latest report.",
                "tone": "warning" if latest and latest["issue_count"] else "success",
            },
        ]
    )

    # Quick actions
    st.markdown('<p class="bl-section-heading">Quick actions</p>', unsafe_allow_html=True)
    a1, a2, a3 = st.columns(3, gap="medium")

    with a1:
        st.markdown(
            '<div class="bl-action-card">'
            '  <span class="bl-action-icon">◎</span>'
            '  <div class="bl-action-title">Analyze a defect</div>'
            '  <p class="bl-action-desc">Open the 7-field form and get an instant quality score, issues list, and professional rewrite.</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        if st.button("Open analysis →", key="goto_analyze", use_container_width=True):
            set_page("analyze")
            st.rerun()

    with a2:
        st.markdown(
            '<div class="bl-action-card">'
            '  <span class="bl-action-icon">◷</span>'
            '  <div class="bl-action-title">Review history</div>'
            '  <p class="bl-action-desc">Browse past analyses, reload any report into the form, or select two for side-by-side comparison.</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        if st.button("Open history →", key="goto_history", use_container_width=True):
            set_page("history")
            st.rerun()

    with a3:
        st.markdown(
            '<div class="bl-action-card">'
            '  <span class="bl-action-icon">⇄</span>'
            '  <div class="bl-action-title">Compare reports</div>'
            '  <p class="bl-action-desc">Place two defect reports side by side and inspect score changes, issue counts, and field differences.</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        if st.button("Open compare →", key="goto_compare", use_container_width=True):
            set_page("compare")
            st.rerun()

    # Trend chart + latest snapshot
    left, right = st.columns([1.15, 0.85], gap="large")

    with left:
        st.markdown('<p class="bl-section-heading">Score trend</p>', unsafe_allow_html=True)
        if len(history) >= 2:
            df = pd.DataFrame(
                [
                    {"Report": i + 1, "Score": e["score"], "Title": e["title"], "Grade": e["grade"]}
                    for i, e in enumerate(history)
                ]
            )
            fig = px.line(
                df, x="Report", y="Score", markers=True,
                hover_data=["Title", "Grade"],
                color_discrete_sequence=["#2563eb"],
            )
            fig.update_traces(
                line=dict(width=2.5),
                marker=dict(size=7, color="#2563eb", line=dict(width=2, color="#fff")),
            )
            _apply_chart_theme(fig, height=300)
            fig.update_layout(yaxis=dict(range=[0, 100]))
            st.plotly_chart(fig, use_container_width=True)
        elif len(history) == 1:
            st.info("Analyze one more defect to see the score trend chart.")
        else:
            render_empty_state(
                "No analyses yet",
                "Submit a defect in the Analyze view and score trends will appear here.",
                "Use a sample from the sidebar for a quick start.",
                icon="◷",
            )

    with right:
        st.markdown('<p class="bl-section-heading">Latest report</p>', unsafe_allow_html=True)
        if latest:
            tone = score_tone(latest["score"])
            with st.container(border=True):
                st.markdown(f"**{latest['title']}**")
                st.caption(latest["created_at"])
                cols = st.columns(2)
                with cols[0]:
                    st.metric("Score", f"{latest['score']}/100")
                with cols[1]:
                    st.metric("Grade", latest["grade"])
                st.markdown(f"*{latest['verdict']}*")
                err_col, warn_col, info_col = st.columns(3)
                with err_col:
                    st.metric("Errors", latest["error_count"])
                with warn_col:
                    st.metric("Warnings", latest["warning_count"])
                with info_col:
                    st.metric("Info", latest["info_count"])
        else:
            render_empty_state(
                "No report yet",
                f"{profile.get('name', 'This workspace')} hasn't analyzed a defect yet.",
                action_hint="Navigate to Analyze Defect to get started.",
                icon="◌",
            )

        render_info_card(
            "Workspace focus",
            f"{profile.get('name', 'Unknown')} — {profile.get('role', 'Role not set')}. {profile.get('focus', '')}.",
            tone="info",
            footer="Session data is stored locally and not shared.",
        )


# ─────────────────────────────────────────────
#  Analysis
# ─────────────────────────────────────────────

def render_analysis() -> None:
    samples = cached_samples()
    form_data = st.session_state.get("form_data", EMPTY_FORM_DATA.copy())
    model = st.session_state.get("preferred_model", DEFAULT_MODEL)

    render_section_header(
        "Analyze Defect",
        "Fill in the structured form to score quality, surface issues, and generate a professional rewrite.",
        "◎",
    )

    # Sample loader toolbar
    tb_left, tb_right = st.columns([1.5, 1], gap="medium")
    with tb_left:
        st.caption("Load a sample to jump-start the form, or write a defect from scratch.")
    with tb_right:
        sample_choice = st.selectbox(
            "Load sample",
            options=["— blank form —"] + [s["name"] for s in samples],
            index=0,
            key="analysis_sample_choice",
            label_visibility="collapsed",
        )
        sb1, sb2 = st.columns(2)
        with sb1:
            if st.button("Load sample", use_container_width=True, key="analysis_load_btn"):
                if load_sample_defect(sample_choice, samples, page="analyze"):
                    st.rerun()
                else:
                    st.warning("Choose a sample first.")
        with sb2:
            if st.button("Clear form", use_container_width=True, key="analysis_clear_btn"):
                clear_analysis_form()
                st.rerun()

    # Main two-column layout
    col_form, col_out = st.columns([1, 1.1], gap="large")

    # ── Form ──────────────────────────────────
    with col_form:
        with st.container(border=True):
            st.markdown("#### Core details")
            with st.form("defect_form", clear_on_submit=False):
                title = st.text_input(
                    "Bug title",
                    value=form_data.get("title", ""),
                    key=widget_key("title"),
                    placeholder="Login button returns 500 on Safari 17",
                )
                description = st.text_area(
                    "Description",
                    value=form_data.get("description", ""),
                    key=widget_key("description"),
                    height=100,
                    placeholder="What happened, when, who is affected, how often?",
                )

                st.markdown("#### Reproduction")
                steps_to_reproduce = st.text_area(
                    "Steps to reproduce",
                    value=form_data.get("steps_to_reproduce", ""),
                    key=widget_key("steps_to_reproduce"),
                    height=130,
                    placeholder="1. Navigate to /login\n2. Enter email and password\n3. Click Sign in",
                )

                fc1, fc2 = st.columns(2)
                with fc1:
                    expected_result = st.text_area(
                        "Expected result",
                        value=form_data.get("expected_result", ""),
                        key=widget_key("expected_result"),
                        height=85,
                        placeholder="User logged in, redirected to /dashboard",
                    )
                with fc2:
                    actual_result = st.text_area(
                        "Actual result",
                        value=form_data.get("actual_result", ""),
                        key=widget_key("actual_result"),
                        height=85,
                        placeholder="500 Internal Server Error",
                    )

                bc1, bc2 = st.columns(2)
                with bc1:
                    environment = st.text_input(
                        "Environment",
                        value=form_data.get("environment", ""),
                        key=widget_key("environment"),
                        placeholder="macOS 14.4 · Safari 17.4 · app v2.3.1",
                    )
                with bc2:
                    sev_opts = ["", "blocker", "critical", "major", "minor", "trivial"]
                    current_sev = form_data.get("severity", "")
                    severity = st.selectbox(
                        "Severity",
                        options=sev_opts,
                        index=sev_opts.index(current_sev) if current_sev in sev_opts else 0,
                        key=widget_key("severity"),
                    )

                ac1, ac2 = st.columns(2)
                with ac1:
                    submitted = st.form_submit_button(
                        "Analyze defect →", use_container_width=True, type="primary"
                    )
                with ac2:
                    cleared = st.form_submit_button(
                        "Clear", use_container_width=True, type="secondary"
                    )

    if cleared:
        clear_analysis_form()
        st.rerun()

    # ── Output ────────────────────────────────
    with col_out:
        result = None
        if submitted:
            payload = {
                "title": title,
                "description": description,
                "steps_to_reproduce": steps_to_reproduce,
                "expected_result": expected_result,
                "actual_result": actual_result,
                "environment": environment,
                "severity": severity,
            }
            st.session_state["form_data"] = payload.copy()
            with st.spinner("Analyzing defect…"):
                analyzer = DefectAnalyzer(model=model)
                result = analyzer.analyze(payload)
                st.session_state["analysis_result"] = result
                st.session_state["analysis_payload"] = payload
                register_analysis(payload, result)
        else:
            result = st.session_state.get("analysis_result")

        if result is None:
            render_empty_state(
                "Ready when you are",
                "Fill in the defect report and press Analyze to see the score, issues, and rewrite.",
                "Use a sample from the toolbar above for a quick demo.",
                icon="◎",
            )
            return

        # Score card
        score = result.score.total
        tone = score_tone(score)
        render_score_card(score, result.score.grade, result.score.verdict, result.rewrite.mode, tone)

        # Section breakdown chart
        st.markdown('<p class="bl-section-heading" style="margin-top:1.25rem;">Section breakdown</p>', unsafe_allow_html=True)
        section_df = pd.DataFrame(
            [{"Section": s.label, "Score": s.score, "Max": s.max_score} for s in result.score.sections]
        )
        fig = px.bar(
            section_df, x="Section", y="Score",
            hover_data=["Max"],
            color="Score",
            color_continuous_scale=[[0, "#fee2e2"], [0.4, "#fef3c7"], [0.75, "#dbeafe"], [1, "#2563eb"]],
            range_color=[0, 25],
            range_y=[0, max(26, int(section_df["Max"].max()) + 1)],
        )
        fig.update_traces(marker_line_width=0)
        _apply_chart_theme(fig, height=260)
        fig.update_layout(coloraxis_showscale=False, xaxis_tickangle=-20)
        st.plotly_chart(fig, use_container_width=True)

        # Issues
        st.markdown('<p class="bl-section-heading">Issues found</p>', unsafe_allow_html=True)
        if not result.issues:
            st.success("✓ No issues found — this report looks clean.")
        else:
            counts = issue_summary(result.issues)
            ic1, ic2, ic3 = st.columns(3)
            with ic1:
                st.metric("Errors", counts["error"])
            with ic2:
                st.metric("Warnings", counts["warning"])
            with ic3:
                st.metric("Info", counts["info"])

            st.markdown('<div style="margin-top:0.75rem;">', unsafe_allow_html=True)
            for issue in result.issues:
                render_issue_item(
                    field=issue.field,
                    severity=issue.severity,
                    code=issue.code,
                    message=issue.message,
                    suggestion=issue.suggestion,
                    tone=severity_tone(issue.severity),
                )
            st.markdown("</div>", unsafe_allow_html=True)

        # Suggestions
        if result.rewrite.suggestions:
            st.markdown('<p class="bl-section-heading" style="margin-top:1rem;">Improvement suggestions</p>', unsafe_allow_html=True)
            sugg_html = []
            for s in result.rewrite.suggestions[:8]:
                from html import escape as _esc
                sugg_html.append(
                    f'<div class="bl-suggestion-item">'
                    f'  <span class="bl-suggestion-dot"></span>'
                    f'  <span>{_esc(s)}</span>'
                    f'</div>'
                )
            st.markdown("".join(sugg_html), unsafe_allow_html=True)

        if result.rewrite.grammar_notes:
            with st.expander("Grammar & clarity notes"):
                for note in result.rewrite.grammar_notes[:8]:
                    st.markdown(f"- {note}")

        # Rewrite
        st.markdown('<p class="bl-section-heading" style="margin-top:1rem;">Professional rewrite</p>', unsafe_allow_html=True)
        st.text_area(
            "Copy this into your bug tracker",
            value=result.rewrite.rewritten_text,
            height=280,
            label_visibility="visible",
        )

        dl1, dl2 = st.columns(2)
        with dl1:
            st.download_button(
                "⬇ Download .md",
                data=result.rewrite.rewritten_text,
                file_name="buglens_rewrite.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with dl2:
            with st.expander("Full JSON output"):
                st.code(result.to_json(), language="json")

        # Email delivery
        st.markdown('<p class="bl-section-heading" style="margin-top:1rem;">Email report</p>', unsafe_allow_html=True)
        smtp_ok, smtp_missing = smtp_configuration_status()
        if not smtp_ok:
            st.warning("SMTP not configured. Go to Settings to set up email delivery. Missing: " + ", ".join(smtp_missing))
        else:
            recipient_email = st.text_input(
                "Recipient email",
                value=st.session_state.get("recipient_email", ""),
                placeholder="qa.lead@example.com",
                key="recipient_email",
            )
            if st.button("Send report →", use_container_width=True):
                try:
                    send_email_report(
                        to_email=recipient_email,
                        subject=title or "BugLens defect report",
                        body=result.rewrite.rewritten_text,
                    )
                    st.success(f"Report sent to {recipient_email}.")
                except Exception as exc:
                    st.error(f"Email failed: {exc}")


# ─────────────────────────────────────────────
#  History
# ─────────────────────────────────────────────

def render_history() -> None:
    history = list(reversed(st.session_state.get("analysis_history", [])))

    render_section_header(
        "History",
        "Review saved analyses, reload a report, or pick two for comparison.",
        "◷",
    )

    if not history:
        render_empty_state(
            "No saved analyses yet",
            "Once you analyze a defect, each result is stored here for later review and comparison.",
            "Run a sample defect from the sidebar to populate history.",
            icon="◷",
        )
        return

    left_col, right_col = st.columns([1.15, 0.85], gap="large")

    with left_col:
        for entry in history:
            tone = score_tone(entry["score"])
            st.markdown(
                f'<div class="bl-history-card">'
                f'  <div style="display:flex; align-items:flex-start; justify-content:space-between; gap:1rem; margin-bottom:0.6rem;">'
                f'    <div style="min-width:0; flex:1;">'
                f'      <div class="bl-history-title">{entry["title"]}</div>'
                f'      <div class="bl-history-meta">{entry["created_at"]} · {entry["verdict"]}</div>'
                f'    </div>'
                f'    <div style="text-align:right; flex-shrink:0;">'
                f'      <div class="bl-history-score">{entry["score"]}</div>'
                f'      <div class="bl-history-denom">/100 · {entry["grade"]}</div>'
                f'    </div>'
                f'  </div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            chip_c, act_c = st.columns([1, 1.8])
            with chip_c:
                render_chip(f"{entry['error_count']} errors", "danger" if entry["error_count"] else "success")
                render_chip(f"{entry['warning_count']} warns", "warning" if entry["warning_count"] else "neutral")
            with act_c:
                btn1, btn2, btn3 = st.columns(3)
                with btn1:
                    if st.button("Load", key=f"load_{entry['id']}", use_container_width=True):
                        sync_form_state(entry["payload"], reset_widgets=True)
                        set_page("analyze")
                        st.rerun()
                with btn2:
                    if st.button("Set A", key=f"cmp_a_{entry['id']}", use_container_width=True):
                        st.session_state["compare_left_id"] = entry["id"]
                        set_page("compare")
                        st.rerun()
                with btn3:
                    if st.button("Set B", key=f"cmp_b_{entry['id']}", use_container_width=True):
                        st.session_state["compare_right_id"] = entry["id"]
                        set_page("compare")
                        st.rerun()
            st.markdown("<hr style='margin:0.5rem 0; border:none; border-top:1px solid #f1f5f9;'>", unsafe_allow_html=True)

    with right_col:
        st.markdown('<p class="bl-section-heading">Score overview</p>', unsafe_allow_html=True)
        all_entries = list(st.session_state.get("analysis_history", []))
        df = pd.DataFrame(
            [{"Report": i + 1, "Score": e["score"], "Grade": e["grade"], "Title": e["title"]}
             for i, e in enumerate(all_entries)]
        )
        fig = px.bar(
            df, x="Report", y="Score",
            color="Score",
            color_continuous_scale=[[0, "#fee2e2"], [0.5, "#fef3c7"], [1, "#2563eb"]],
            range_color=[0, 100],
            hover_data=["Title", "Grade"],
        )
        fig.update_traces(marker_line_width=0)
        _apply_chart_theme(fig, height=240)
        fig.update_layout(coloraxis_showscale=False, yaxis=dict(range=[0, 100]))
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('<p class="bl-section-heading">Workspace stats</p>', unsafe_allow_html=True)
        best = max(e["score"] for e in history)
        avg = round(sum(e["score"] for e in history) / len(history))
        s1, s2 = st.columns(2)
        with s1:
            st.metric("Total reports", len(history))
            st.metric("Best score", f"{best}/100")
        with s2:
            st.metric("Average score", f"{avg}/100")
            st.metric("Latest grade", history[0]["grade"])


# ─────────────────────────────────────────────
#  Compare
# ─────────────────────────────────────────────

def render_compare() -> None:
    history = st.session_state.get("analysis_history", [])

    render_section_header(
        "Compare Reports",
        "Pick two saved analyses to inspect score changes, issue counts, and section differences.",
        "⇄",
    )

    if len(history) < 2:
        render_empty_state(
            "Need at least two reports",
            "Run the analysis workflow twice to unlock side-by-side comparison.",
            "Use the built-in sample defects to quickly create a pair.",
            icon="⇄",
        )
        return

    options = list(reversed(history))
    labels = {
        e["id"]: f"{e['title']}  ·  {e['created_at']}  ·  {e['score']}/100"
        for e in options
    }
    ids = [e["id"] for e in options]

    def _idx(key: str, fallback: int) -> int:
        stored = st.session_state.get(key, "")
        try:
            return ids.index(stored)
        except ValueError:
            return min(fallback, len(ids) - 1)

    sel1, sel2 = st.columns(2, gap="medium")
    with sel1:
        left_id = st.selectbox(
            "Report A",
            options=ids,
            format_func=lambda i: labels[i],
            index=_idx("compare_left_id", 0),
            key="compare_left_selector",
        )
    with sel2:
        right_id = st.selectbox(
            "Report B",
            options=ids,
            format_func=lambda i: labels[i],
            index=_idx("compare_right_id", 1),
            key="compare_right_selector",
        )

    st.session_state["compare_left_id"] = left_id
    st.session_state["compare_right_id"] = right_id

    left_e = compare_entry_by_id(left_id)
    right_e = compare_entry_by_id(right_id)
    if not left_e or not right_e:
        render_empty_state("Comparison unavailable", "Select two saved reports to continue.")
        return

    # Summary cards
    sc1, sc2 = st.columns(2, gap="medium")
    for col, entry, lbl in [(sc1, left_e, "A"), (sc2, right_e, "B")]:
        with col:
            tone = score_tone(entry["score"])
            st.markdown(
                f'<div class="bl-compare-card">'
                f'  <div class="bl-compare-label">Report {lbl}</div>'
                f'  <div style="font-size:0.9375rem; font-weight:700; margin-bottom:0.2rem;">{entry["title"]}</div>'
                f'  <div style="font-size:0.8rem; color:var(--c-text-4); margin-bottom:0.75rem;">{entry["created_at"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Score", f"{entry['score']}/100")
            with m2:
                st.metric("Grade", entry["grade"])
            with m3:
                st.metric("Issues", entry["issue_count"])

    # Delta row
    st.markdown('<p class="bl-section-heading" style="margin-top:1.25rem;">Score delta (B vs A)</p>', unsafe_allow_html=True)
    d1, d2, d3, d4 = st.columns(4)
    with d1:
        st.metric("Score Δ", right_e["score"] - left_e["score"],
                  delta=right_e["score"] - left_e["score"])
    with d2:
        st.metric("Issues Δ", right_e["issue_count"] - left_e["issue_count"],
                  delta=-(right_e["issue_count"] - left_e["issue_count"]))
    with d3:
        st.metric("Errors Δ", right_e["error_count"] - left_e["error_count"],
                  delta=-(right_e["error_count"] - left_e["error_count"]))
    with d4:
        st.metric("Warnings Δ", right_e["warning_count"] - left_e["warning_count"],
                  delta=-(right_e["warning_count"] - left_e["warning_count"]))

    # Section comparison chart
    st.markdown('<p class="bl-section-heading">Section scores</p>', unsafe_allow_html=True)
    score_df = pd.DataFrame(
        [{"Section": s.label, "Score": s.score, "Report": "A"} for s in left_e["result"].score.sections]
        + [{"Section": s.label, "Score": s.score, "Report": "B"} for s in right_e["result"].score.sections]
    )
    fig = px.bar(
        score_df, x="Section", y="Score", color="Report", barmode="group",
        color_discrete_map={"A": "#2563eb", "B": "#7c3aed"},
    )
    fig.update_traces(marker_line_width=0)
    _apply_chart_theme(fig, height=320)
    fig.update_layout(xaxis_tickangle=-20)
    st.plotly_chart(fig, use_container_width=True)

    # Field diff + rewrites
    fd_col, rw_col = st.columns(2, gap="large")

    with fd_col:
        st.markdown('<p class="bl-section-heading">Field differences</p>', unsafe_allow_html=True)
        fields = [
            ("title", "Title"),
            ("description", "Description"),
            ("steps_to_reproduce", "Steps to reproduce"),
            ("expected_result", "Expected result"),
            ("actual_result", "Actual result"),
            ("environment", "Environment"),
            ("severity", "Severity"),
        ]
        from html import escape as _esc
        for key, label in fields:
            lv = left_e["payload"].get(key, "") or "(empty)"
            rv = right_e["payload"].get(key, "") or "(empty)"
            st.markdown(
                f'<div class="bl-field-diff">'
                f'  <div class="bl-field-diff-label">{_esc(label)}</div>'
                f'  <div class="bl-field-diff-row">'
                f'    <div class="bl-field-diff-side"><div class="bl-field-diff-side-label">A</div>{_esc(lv)}</div>'
                f'    <div class="bl-field-diff-side"><div class="bl-field-diff-side-label">B</div>{_esc(rv)}</div>'
                f'  </div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    with rw_col:
        st.markdown('<p class="bl-section-heading">Rewrite comparison</p>', unsafe_allow_html=True)
        st.caption("Report A rewrite")
        st.text_area("A", value=left_e["result"].rewrite.rewritten_text, height=210, label_visibility="collapsed")
        st.caption("Report B rewrite")
        st.text_area("B", value=right_e["result"].rewrite.rewritten_text, height=210, label_visibility="collapsed")


# ─────────────────────────────────────────────
#  Settings
# ─────────────────────────────────────────────

def render_settings() -> None:
    smtp_ok, smtp_missing = smtp_configuration_status()

    render_section_header(
        "Settings",
        "Workspace preferences, AI model, and email delivery configuration.",
        "⚙",
    )

    col_prefs, col_smtp = st.columns(2, gap="large")

    with col_prefs:
        st.markdown('<div class="bl-settings-panel">', unsafe_allow_html=True)
        st.markdown('<div class="bl-settings-panel-title">Workspace preferences</div>', unsafe_allow_html=True)

        model_options = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
        model_choice = st.selectbox(
            "Default AI model",
            options=model_options,
            index=model_options.index(st.session_state.get("preferred_model", DEFAULT_MODEL)),
            key="settings_model_choice",
        )
        st.session_state["preferred_model"] = model_choice

        landing_choice = st.selectbox(
            "Landing page after login",
            options=PAGE_SEQUENCE,
            index=PAGE_SEQUENCE.index(st.session_state.get("default_landing_page", "dashboard")),
            format_func=lambda p: NAV_PAGES[p]["label"],
            key="settings_landing_choice",
        )
        st.session_state["default_landing_page"] = landing_choice

        st.markdown("---")
        st.markdown("**Danger zone**")
        st.caption("Clearing history removes all saved analyses from this session and the local database.")
        if st.button("Clear workspace history", use_container_width=True):
            clear_workspace_history()
            st.success("Workspace history cleared.")

        st.markdown("</div>", unsafe_allow_html=True)

    with col_smtp:
        st.markdown('<div class="bl-settings-panel">', unsafe_allow_html=True)
        st.markdown('<div class="bl-settings-panel-title">Email delivery (SMTP)</div>', unsafe_allow_html=True)

        if smtp_ok:
            render_chip("SMTP configured", "success", "●")
        else:
            render_chip("Not configured", "warning", "●")
            if smtp_missing:
                st.caption("Missing: " + ", ".join(smtp_missing))

        cfg_host = st.text_input("SMTP host", value=os.getenv("SMTP_HOST", ""))
        cfg_port = st.text_input("SMTP port", value=os.getenv("SMTP_PORT", "587"))
        cfg_user = st.text_input("SMTP username", value=os.getenv("SMTP_USERNAME", ""))
        cfg_pass = st.text_input("SMTP password", value="", type="password")
        cfg_from = st.text_input("From email (optional)", value=os.getenv("SMTP_FROM", ""))
        cfg_tls = st.checkbox("Use TLS", value=(os.getenv("SMTP_USE_TLS", "true").lower() != "false"))

        save_c, clear_c = st.columns(2)
        with save_c:
            if st.button("Save SMTP", use_container_width=True):
                try:
                    save_smtp_settings(
                        {
                            "SMTP_HOST": cfg_host.strip(),
                            "SMTP_PORT": cfg_port.strip(),
                            "SMTP_USERNAME": cfg_user.strip(),
                            "SMTP_PASSWORD": cfg_pass,
                            "SMTP_FROM": cfg_from.strip(),
                            "SMTP_USE_TLS": "true" if cfg_tls else "false",
                        }
                    )
                    st.success("SMTP settings saved.")
                except Exception as exc:
                    st.error(f"Failed: {exc}")
        with clear_c:
            if st.button("Clear SMTP", use_container_width=True):
                try:
                    clear_smtp_settings()
                    st.success("SMTP cleared.")
                except Exception as exc:
                    st.error(f"Failed: {exc}")

        st.markdown("</div>", unsafe_allow_html=True)

    # About section
    st.markdown('<p class="bl-section-heading" style="margin-top:1.5rem;">About this workspace</p>', unsafe_allow_html=True)
    render_metric_cards(
        [
            {
                "icon": "◈",
                "label": "Views",
                "value": "5",
                "caption": "Dashboard · Analyze · History · Compare · Settings",
                "tone": "primary",
            },
            {
                "icon": "◌",
                "label": "Data",
                "value": "Session",
                "caption": "History stays inside the current workspace session.",
                "tone": "info",
            },
            {
                "icon": "●",
                "label": "Rewrite",
                "value": "Local",
                "caption": "Works fully offline without an API key.",
                "tone": "warning",
            },
            {
                "icon": "✉",
                "label": "Email",
                "value": "SMTP",
                "caption": "Send rewritten reports directly from analysis view.",
                "tone": "success" if smtp_ok else "neutral",
            },
        ]
    )


# ─────────────────────────────────────────────
#  App shell
# ─────────────────────────────────────────────

def render_workspace() -> None:
    page = st.session_state.get("page", "dashboard")
    if page == "dashboard":
        render_dashboard()
    elif page == "analyze":
        render_analysis()
    elif page == "history":
        render_history()
    elif page == "compare":
        render_compare()
    elif page == "settings":
        render_settings()
    else:
        render_dashboard()


def main() -> None:
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="🪲",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_theme()
    init_state()

    if not st.session_state["logged_in"]:
        render_auth_page()

    render_sidebar()
    render_workspace()


main()
