"""
BugLens — Defect Quality Checker
Streamlit UI.

Layout:
    │ Sidebar  →  sample loader, mode info, model choice         │
    │ Header   →  product hero + score badge                      │
    │ Form     →  7 input fields (title, desc, steps, exp, act…)  │
    │ Output   →  score breakdown + issues + rewrite + tips       │
    └─────────────────────────────────────────────────────────────┘
"""

import json
import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

try:
    from .modules import (
        DefectAnalyzer,
        send_email_report,
        smtp_configured,
    )
except ImportError:
    try:
        from modules import (
            DefectAnalyzer,
            send_email_report,
            smtp_configured,
        )
    except ImportError:
        from buglens.modules import (
            DefectAnalyzer,
            send_email_report,
            smtp_configured,
        )


def smtp_configuration_status() -> tuple[bool, list[str]]:
    required = ("SMTP_HOST", "SMTP_USERNAME", "SMTP_PASSWORD")
    missing = [name for name in required if not os.getenv(name)]
    return len(missing) == 0, missing
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

ROLES = [
    "QA Engineer",
    "QA Lead",
    "Developer",
    "Analyst",
    "Product Manager",
    "Support Engineer",
    "DevOps",
]


def init_auth_state() -> None:
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["current_user"] = ""
        st.session_state["auth_view"] = "login"
        st.session_state["auth_error"] = ""
        st.session_state["auth_notice"] = ""
        st.session_state["user_directory"] = {
            account["username"]: {
                "password": account["password"],
                "name": account["name"],
                "role": account["role"],
                "focus": account["focus"],
                "is_demo": True,
            }
            for account in DEMO_ACCOUNTS
        }


def authenticate(username: str, password: str) -> bool:
    account = st.session_state["user_directory"].get(username)
    return bool(account and account["password"] == password)


def login_user(username: str) -> None:
    st.session_state["logged_in"] = True
    st.session_state["current_user"] = username
    st.session_state["auth_error"] = ""
    st.session_state["auth_notice"] = ""


def logout_user() -> None:
    st.session_state["logged_in"] = False
    st.session_state["current_user"] = ""
    st.session_state["auth_view"] = "login"
    st.session_state["auth_error"] = ""
    st.session_state["auth_notice"] = ""


def signup(name: str, username: str, password: str, role: str) -> dict:
    clean_name = name.strip()
    clean_user = username.strip().lower()
    clean_role = role.strip()

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
        "role": clean_role,
        "focus": "Personal workspace",
        "is_demo": False,
    }
    return {"ok": True, "username": clean_user}


def _render_login_page() -> None:
    return render_auth_screen()
    quote = 'BugLens — Defect Quality Checker · "Turning confusion into clarity." · '
    repeat = quote * 8
    marquee_rows = []
    for i in range(8):
        marquee_rows.append(
            f'<div class="bl-login-marquee-row"><span class="bl-login-marquee-text">{repeat}</span><span class="bl-login-marquee-text" aria-hidden="true">{repeat}</span></div>'
        )

    st.markdown(
        '<div class="bl-login-bg">'
        '<div class="bl-login-blob"></div>'
        '<div class="bl-login-grid"></div>'
        '<div class="bl-login-marquee">' + ''.join(marquee_rows) + '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div style="min-height:100vh; display:flex; align-items:center; justify-content:center; padding:2rem;">'
        '<div class="bl-login-card">'
        '<div style="display:flex; align-items:center; gap:10px; margin-bottom:1.6rem;">'
        '<div style="width:38px; height:38px; background:#1a1714; border-radius:9px; display:flex; align-items:center; justify-content:center;">'
        '<svg viewBox="0 0 22 22" fill="none" width="22" height="22">'
        '<circle cx="11" cy="11" r="9" stroke="#4ade80" stroke-width="1.5"/>'
        '<path d="M7 11l3 3 5-5" stroke="#4ade80" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
        '</svg>'
        '</div>'
        '<div class="bl-serif" style="font-size:1.4rem; color:#1a1714;">Bug<em style="color:#c4410c; font-style:normal;">Lens</em></div>'
        '</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div style="max-width:440px; margin:0 auto;">', unsafe_allow_html=True)

    mode = st.session_state["login_mode"]
    cols = st.columns([1, 1])
    with cols[0]:
        if st.button("Sign In", key="tab_login"):
            st.session_state["login_mode"] = "login"
            st.session_state["login_error"] = ""
            st.session_state["sign_error"] = ""
    with cols[1]:
        if st.button("Create Account", key="tab_signup"):
            st.session_state["login_mode"] = "signup"
            st.session_state["login_error"] = ""
            st.session_state["sign_error"] = ""

    st.markdown("<div style='margin-top:1.5rem; padding:1rem; background:#fffefb; border-radius:18px; box-shadow:0 10px 30px rgba(0,0,0,.08);'>", unsafe_allow_html=True)

    if mode == "login":
        st.markdown('<h2 class="bl-serif" style="font-size:1.45rem; color:#1a1714; margin-bottom:.18rem;">Welcome back</h2>', unsafe_allow_html=True)
        st.markdown('<p class="bl-mono" style="font-size:.8rem; color:#7a756e; margin-bottom:1.5rem;">// AI-powered defect quality platform</p>', unsafe_allow_html=True)
        if st.session_state["login_error"]:
            st.error(st.session_state["login_error"])

        with st.form("login_form"):
            login_user = st.text_input("Username", value=st.session_state["login_user"], key="login_user_input")
            login_pass = st.text_input("Password", type="password", value=st.session_state["login_pass"], key="login_pass_input")
            submitted = st.form_submit_button("Sign In →")
            if submitted:
                if authenticate(login_user.strip().lower(), login_pass):
                    st.session_state["logged_in"] = True
                    st.session_state["current_user"] = login_user.strip().lower()
                    st.session_state["login_error"] = ""
                    st.experimental_rerun()
                else:
                    st.session_state["login_error"] = "Invalid username or password."
                    st.session_state["login_pass"] = ""

        st.markdown('<div style="margin-top:1.4rem; padding-top:1.1rem; border-top:1px solid #d4cfc5;">', unsafe_allow_html=True)
        st.markdown('<p class="bl-mono" style="font-size:.77rem; color:#a09a92; margin-bottom:.5rem;">// Demo accounts — click to sign in instantly</p>', unsafe_allow_html=True)
        demo_cols = st.columns(2)
        for index, acc in enumerate(DEMO_ACCOUNTS):
            if demo_cols[index % 2].button(f"{acc['role']} — {acc['username']}", key=f"demo_{acc['username']}"):
                st.session_state["login_user"] = acc["username"]
                st.session_state["login_pass"] = acc["password"]
                st.session_state["logged_in"] = True
                st.session_state["current_user"] = acc["username"]
                st.experimental_rerun()
    else:
        st.markdown('<h2 class="bl-serif" style="font-size:1.45rem; color:#1a1714; margin-bottom:.18rem;">Create your account</h2>', unsafe_allow_html=True)
        st.markdown('<p class="bl-mono" style="font-size:.8rem; color:#7a756e; margin-bottom:1.5rem;">// Free — no credit card required</p>', unsafe_allow_html=True)
        if st.session_state["sign_error"]:
            st.error(st.session_state["sign_error"])

        with st.form("signup_form"):
            sign_name = st.text_input("Full Name", value=st.session_state["sign_name"], key="sign_name_input")
            sign_user = st.text_input("Username", value=st.session_state["sign_user"], key="sign_user_input")
            sign_pass = st.text_input("Password", type="password", value=st.session_state["sign_pass"], key="sign_pass_input")
            sign_role = st.selectbox("Role", options=ROLES, index=ROLES.index(st.session_state["sign_role"]), key="sign_role_select")
            submitted = st.form_submit_button("Create Account →")
            if submitted:
                result = signup(sign_user, sign_pass, sign_name, sign_role)
                if result["ok"]:
                    st.session_state["login_mode"] = "login"
                    st.session_state["login_user"] = sign_user.strip().lower()
                    st.session_state["login_pass"] = sign_pass
                    st.session_state["sign_error"] = ""
                    st.session_state["login_error"] = ""
                    st.success("Account created. Please sign in.")
                    st.experimental_rerun()
                else:
                    st.session_state["sign_error"] = result["error"]

        st.markdown('<p style="text-align:center; font-size:.8rem; color:#a09a92; margin-top:1rem; font-family:\'DM Mono\', monospace;">Already have an account?</p>', unsafe_allow_html=True)
        if st.button("Sign in", key="switch_to_login"):
            st.session_state["login_mode"] = "login"
            st.session_state["login_error"] = ""
            st.session_state["sign_error"] = ""
            st.experimental_rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


def render_auth_screen() -> None:
    st.markdown(
        """
        <div class="bl-auth-shell">
            <div class="bl-auth-banner">
                <div class="bl-auth-kicker">BugLens workspace access</div>
                <h1>Sharpen defect reports before they reach engineering.</h1>
                <p>Sign in with a demo account or create your own workspace profile to analyze, score, and rewrite bug reports.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    info_col, form_col = st.columns([1.15, 0.95], gap="large")

    with info_col:
        st.markdown("### Why this login exists")
        st.markdown(
            "- Keeps the analysis workspace separate for each reviewer.\n"
            "- Gives you ready-to-use demo users for walkthroughs.\n"
            "- Lets interview or demo sessions create accounts on the fly."
        )

        st.markdown("### Demo users")
        for account in DEMO_ACCOUNTS:
            with st.container(border=True):
                st.markdown(
                    f"**{account['name']}**  \n"
                    f"`{account['role']}`  \n"
                    f"{account['focus']}"
                )
                if st.button(
                    f"Use {account['username']} / {account['password']}",
                    key=f"demo_login_{account['username']}",
                    use_container_width=True,
                ):
                    login_user(account["username"])
                    st.rerun()

    with form_col:
        st.markdown('<div class="bl-auth-card">', unsafe_allow_html=True)
        toggle_cols = st.columns(2)
        with toggle_cols[0]:
            if st.button("Login", key="auth_login_tab", use_container_width=True):
                st.session_state["auth_view"] = "login"
                st.session_state["auth_error"] = ""
                st.session_state["auth_notice"] = ""
        with toggle_cols[1]:
            if st.button("Sign Up", key="auth_signup_tab", use_container_width=True):
                st.session_state["auth_view"] = "signup"
                st.session_state["auth_error"] = ""
                st.session_state["auth_notice"] = ""

        if st.session_state["auth_notice"]:
            st.success(st.session_state["auth_notice"])
        if st.session_state["auth_error"]:
            st.error(st.session_state["auth_error"])

        if st.session_state["auth_view"] == "login":
            st.markdown("### Welcome back")
            st.caption("Use a demo account or your own credentials.")
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="maya")
                password = st.text_input("Password", type="password", placeholder="Enter password")
                submitted = st.form_submit_button("Enter BugLens", use_container_width=True)
                if submitted:
                    clean_user = username.strip().lower()
                    if authenticate(clean_user, password):
                        login_user(clean_user)
                        st.rerun()
                    else:
                        st.session_state["auth_error"] = "Invalid username or password."
                        st.session_state["auth_notice"] = ""
                        st.rerun()
        else:
            st.markdown("### Create a workspace profile")
            st.caption("New users can sign up here without changing the app data.")
            with st.form("signup_form"):
                full_name = st.text_input("Full name", placeholder="Aarav Singh")
                username = st.text_input("Username", placeholder="aarav")
                role = st.selectbox("Role", ROLES, index=0)
                password = st.text_input("Password", type="password", placeholder="At least 6 characters")
                submitted = st.form_submit_button("Create account", use_container_width=True)
                if submitted:
                    result = signup(full_name, username, password, role)
                    if result["ok"]:
                        st.session_state["auth_view"] = "login"
                        st.session_state["auth_notice"] = (
                            f"Account created for {full_name.strip()}. Sign in with @{result['username']}."
                        )
                        st.session_state["auth_error"] = ""
                        st.rerun()
                    else:
                        st.session_state["auth_error"] = result["error"]
                        st.session_state["auth_notice"] = ""
                        st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()
# --- page config & global styling ------------------------------------------

st.set_page_config(
    page_title="BugLens — Defect Quality Checker",
    page_icon="🐞",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Compact, clean CSS. No external assets required.
_CSS = """
<style>
    .bl-hero {background: linear-gradient(135deg,#5b6cff 0%,#8b5cf6 50%,#ec4899 100%);
              padding: 1.4rem 1.6rem; border-radius: 14px; color: white; margin-bottom: 1.2rem;}
    .bl-hero h1 {margin:0; font-size: 1.6rem; font-weight: 700;}
    .bl-hero p  {margin:0.2rem 0 0 0; opacity: 0.92; font-size: 0.95rem;}
    .bl-section {background:#0f1115; border:1px solid #2a2f3a; border-radius:12px; padding:1rem 1.2rem; margin-bottom:0.8rem;}
    .bl-section h3 {margin-top:0; color:#cfd2da; font-size:1.05rem;}
    .bl-pill {display:inline-block; padding:2px 10px; border-radius:999px; font-size:0.78rem; font-weight:600;}
    .bl-pill-err  {background:#3b1d1d; color:#ff8a8a; border:1px solid #7a2a2a;}
    .bl-pill-warn {background:#3b321d; color:#ffd27a; border:1px solid #7a5d22;}
    .bl-pill-info {background:#1d2a3b; color:#9ec5ff; border:1px solid #2d4a78;}
    .bl-pill-ok   {background:#1d3b25; color:#7ee2a8; border:1px solid #2c6c44;}
    .bl-score-num {font-size: 3.2rem; font-weight: 800; line-height:1;}

    /* Auth screen styling */
    .bl-auth-shell {
        background:
            radial-gradient(circle at top left, rgba(255, 214, 102, 0.22), transparent 28%),
            radial-gradient(circle at bottom right, rgba(74, 222, 128, 0.15), transparent 24%),
            linear-gradient(135deg, #07111f 0%, #10253f 55%, #17375b 100%);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 28px;
        padding: 2rem 2.2rem;
        margin-bottom: 1.4rem;
        color: #f7fafc;
        box-shadow: 0 22px 60px rgba(0,0,0,0.25);
    }
    .bl-auth-banner h1 {margin: 0.35rem 0 0.7rem; font-size: 2.3rem; line-height: 1.05;}
    .bl-auth-banner p {margin: 0; max-width: 44rem; color: rgba(247,250,252,0.82);}
    .bl-auth-kicker {
        display: inline-block;
        padding: 0.35rem 0.7rem;
        border-radius: 999px;
        background: rgba(255,255,255,0.1);
        color: #fde68a;
        font-size: 0.8rem;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        font-weight: 700;
    }
    .bl-auth-card {
        background: linear-gradient(180deg, rgba(12,21,36,0.96), rgba(11,29,49,0.96));
        border: 1px solid rgba(148,163,184,0.24);
        border-radius: 24px;
        padding: 1.2rem;
        box-shadow: 0 20px 40px rgba(2, 6, 23, 0.28);
    }
</style>
"""
st.markdown(_CSS, unsafe_allow_html=True)
init_auth_state()
if not st.session_state["logged_in"]:
    render_auth_screen()


# --- sample data loader ------------------------------------------------------

DATA_DIR = Path(__file__).parent / "data"
SAMPLES_FILE = DATA_DIR / "sample_defects.json"


@st.cache_data
def load_samples() -> list[dict]:
    if not SAMPLES_FILE.exists():
        return []
    with SAMPLES_FILE.open("r", encoding="utf-8") as fh:
        return json.load(fh)


# --- sidebar -----------------------------------------------------------------

with st.sidebar:
    st.markdown("### 🐞 BugLens")
    st.caption("Defect Quality Checker · v1.0")
    current_username = st.session_state.get("current_user", "")
    current_profile = st.session_state["user_directory"].get(current_username, {})
    st.markdown(f"**Signed in as** `{current_username}`")
    if current_username:
        st.caption(f"{current_profile.get('name', '')} · {current_profile.get('role', '')}")
    if st.button("Logout"):
        logout_user()
        st.rerun()
    st.divider()

    samples = load_samples()
    sample_choice = st.selectbox(
        "📦 Load a sample defect",
        options=["— blank form —"] + [s["name"] for s in samples],
        index=0,
    )
    if sample_choice and sample_choice != "— blank form —":
        chosen = next(s for s in samples if s["name"] == sample_choice)
        st.session_state["form_data"] = chosen["data"]
        st.success(f"Loaded: **{sample_choice}**")

    st.divider()
    st.markdown("#### ⚙️ Mode")
    has_key = bool(os.getenv("OPENAI_API_KEY"))
    if has_key:
        st.markdown('<span class="bl-pill bl-pill-ok">AI rewrite enabled</span>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<span class="bl-pill bl-pill-warn">Local rewrite mode (no OPENAI_API_KEY)</span>',
            unsafe_allow_html=True,
        )
        st.caption("Set `OPENAI_API_KEY` in your env to enable GPT-powered rewrite.")

    model = st.selectbox(
        "Model",
        options=["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
        index=0,
        disabled=not has_key,
    )

    st.divider()
    st.markdown("#### 📊 Section weights")
    st.caption(
        "• Field completeness 25  \n"
        "• Reproduction quality 25  \n"
        "• Expected vs actual 15  \n"
        "• Environment quality 15  \n"
        "• Readability 10  \n"
        "• Severity validity 10"
    )
    st.divider()
    st.markdown("#### ✉️ Delivery")
    smtp_ok, smtp_missing = smtp_configuration_status()
    if smtp_ok:
        st.markdown('<span class="bl-pill bl-pill-ok">SMTP email enabled</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="bl-pill bl-pill-warn">SMTP email not configured</span>', unsafe_allow_html=True)
        st.caption(
            "Set SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, and optionally SMTP_FROM. "
            f"Missing: {', '.join(smtp_missing)}"
        )

    # --- SMTP settings form (persist to buglens/smtp_config.json) ---
    with st.expander("Configure SMTP settings (save locally)"):
        cfg_host = st.text_input("SMTP host", value=os.getenv("SMTP_HOST", ""))
        cfg_port = st.text_input("SMTP port", value=os.getenv("SMTP_PORT", "587"))
        cfg_user = st.text_input("SMTP username", value=os.getenv("SMTP_USERNAME", ""))
        cfg_pass = st.text_input("SMTP password", value="", type="password")
        cfg_from = st.text_input("From email (optional)", value=os.getenv("SMTP_FROM", ""))
        cfg_tls = st.checkbox("Use TLS", value=(os.getenv("SMTP_USE_TLS", "true").lower() != "false"))

        cfg_path = Path(__file__).parent / "smtp_config.json"

        if st.button("Save SMTP settings locally"):
            payload = {
                "SMTP_HOST": cfg_host.strip(),
                "SMTP_PORT": cfg_port.strip(),
                "SMTP_USERNAME": cfg_user.strip(),
                "SMTP_PASSWORD": cfg_pass,
                "SMTP_FROM": cfg_from.strip(),
                "SMTP_USE_TLS": "true" if cfg_tls else "false",
            }
            try:
                with cfg_path.open("w", encoding="utf-8") as fh:
                    json.dump(payload, fh, indent=2)
                # also set in env for immediate effect
                for k, v in payload.items():
                    if v:
                        os.environ[k] = v
                st.success(f"Saved SMTP settings to {cfg_path.name}")
            except Exception as exc:
                st.error(f"Failed to save SMTP config: {exc}")

        if st.button("Clear saved SMTP settings"):
            try:
                if cfg_path.exists():
                    cfg_path.unlink()
                # remove env vars we may have set
                for k in ("SMTP_HOST", "SMTP_PORT", "SMTP_USERNAME", "SMTP_PASSWORD", "SMTP_FROM", "SMTP_USE_TLS"):
                    os.environ.pop(k, None)
                st.success("Cleared saved SMTP settings")
            except Exception as exc:
                st.error(f"Failed to clear SMTP config: {exc}")


# --- header ------------------------------------------------------------------

st.markdown(
    '<div class="bl-hero">'
    '<h1>🐞 BugLens — Defect Quality Checker</h1>'
    '<p>Score, validate, and rewrite software defect reports with rule-based + AI analysis.</p>'
    '</div>',
    unsafe_allow_html=True,
)

st.caption(
    "Built with Streamlit · Python · OpenAI · Plotly · "
    "[github.com/9harshithp/BugLens-Defect-Quality-Checker](#)"
)


# --- form --------------------------------------------------------------------

form_data = st.session_state.get("form_data", {})

col_form, col_out = st.columns([1.05, 1.2], gap="large")

with col_form:
    st.markdown('<div class="bl-section"><h3>📝 Defect Report Input</h3></div>',
                unsafe_allow_html=True)
    with st.form("defect_form", clear_on_submit=False):
        title = st.text_input("Bug title", value=form_data.get("title", ""),
                              placeholder="Login button 500s on Safari 17")
        description = st.text_area(
            "Description", value=form_data.get("description", ""), height=100,
            placeholder="What happened, when, who is affected, how often?",
        )
        steps_to_reproduce = st.text_area(
            "Steps to reproduce", value=form_data.get("steps_to_reproduce", ""), height=120,
            placeholder="1. Go to /login\n2. Enter email + password\n3. Click 'Sign in'",
        )
        c1, c2 = st.columns(2)
        with c1:
            expected_result = st.text_area(
                "Expected result", value=form_data.get("expected_result", ""), height=80,
                placeholder="User is logged in and redirected to /dashboard",
            )
        with c2:
            actual_result = st.text_area(
                "Actual result", value=form_data.get("actual_result", ""), height=80,
                placeholder="500 error: 'Internal Server Error'",
            )
        c3, c4 = st.columns(2)
        with c3:
            environment = st.text_input(
                "Environment", value=form_data.get("environment", ""),
                placeholder="macOS 14.4 · Safari 17.4 · app v2.3.1",
            )
        with c4:
            severity = st.selectbox(
                "Severity",
                options=["", "blocker", "critical", "major", "minor", "trivial"],
                index=["", "blocker", "critical", "major", "minor", "trivial"].index(
                    form_data.get("severity", "")
                ) if form_data.get("severity", "") in ["", "blocker", "critical", "major", "minor", "trivial"] else 0,
            )

        submitted = st.form_submit_button("🔍 Analyze defect", use_container_width=True)

# --- analysis ----------------------------------------------------------------

with col_out:
    st.markdown('<div class="bl-section"><h3>📊 Analysis Output</h3></div>',
                unsafe_allow_html=True)

    result = None
    if submitted:
        payload = {
            "title": title, "description": description,
            "steps_to_reproduce": steps_to_reproduce,
            "expected_result": expected_result, "actual_result": actual_result,
            "environment": environment, "severity": severity,
        }
        with st.spinner("Analyzing…"):
            analyzer = DefectAnalyzer(model=model)
            result = analyzer.analyze(payload)
            st.session_state["analysis_result"] = result
            st.session_state["analysis_payload"] = payload
    else:
        result = st.session_state.get("analysis_result")

    if result is None:
        st.info("Fill in the defect on the left and press **Analyze defect** to see the report card.")
    else:
        # -- score header
        sc, gc, vc = st.columns([1, 1, 2])
        with sc:
            st.markdown(f'<div class="bl-score-num">{result.score.total}</div>', unsafe_allow_html=True)
            st.caption("out of 100")
        with gc:
            grade = result.score.grade
            grade_color = {"A": "bl-pill-ok", "B": "bl-pill-ok",
                           "C": "bl-pill-warn", "D": "bl-pill-warn",
                           "F": "bl-pill-err"}[grade]
            st.markdown(f'<span class="bl-pill {grade_color}">Grade {grade}</span>',
                        unsafe_allow_html=True)
            st.markdown(f'<span class="bl-pill bl-pill-info">Mode: {result.rewrite.mode}</span>',
                        unsafe_allow_html=True)
        with vc:
            st.write(result.score.verdict)

        # -- section breakdown chart
        df = pd.DataFrame([{
            "section": s.label,
            "score": s.score,
            "max": s.max_score,
        } for s in result.score.sections])
        fig = px.bar(
            df, x="section", y="score",
            hover_data=["max"],
            color="score", color_continuous_scale="RdYlGn",
            range_y=[0, df["max"].max()],
            title="Section-wise scoring",
        )
        fig.update_layout(height=320, margin=dict(t=40, l=0, r=0, b=0),
                          xaxis_title=None, yaxis_title="Points")
        st.plotly_chart(fig, use_container_width=True)

        # -- issues
        st.markdown("##### 🚨 Issues found")
        if not result.issues:
            st.success("No issues — clean report.")
        else:
            counts = {"error": 0, "warning": 0, "info": 0}
            for issue in result.issues:
                counts[issue.severity] = counts.get(issue.severity, 0) + 1
                icon = {"error": "🔴", "warning": "🟠", "info": "🔵"}[issue.severity]
                with st.expander(f"{icon} {issue.field} — {issue.message}"):
                    st.markdown(f"**Code:** `{issue.code}`")
                    st.markdown(f"**Suggestion:** {issue.suggestion}")
            cc1, cc2, cc3 = st.columns(3)
            cc1.metric("Errors", counts["error"])
            cc2.metric("Warnings", counts["warning"])
            cc3.metric("Info", counts["info"])

        # -- AI suggestions
        st.markdown("##### 💡 AI / rule-based suggestions")
        if not result.rewrite.suggestions:
            st.caption("No additional suggestions.")
        for s in result.rewrite.suggestions:
            st.markdown(f"- {s}")

        # -- grammar notes
        if result.rewrite.grammar_notes:
            with st.expander("📝 Grammar / clarity notes"):
                for n in result.rewrite.grammar_notes:
                    st.markdown(f"- {n}")

        # -- rewritten report
        st.markdown("##### ✨ Rewritten professional report")
        st.text_area(
            "Copy this into your bug tracker",
            value=result.rewrite.rewritten_text,
            height=320,
        )
        st.markdown("##### ✉️ Email this report")
        recipient_email = st.text_input(
            "Recipient email",
            value=st.session_state.get("recipient_email", ""),
            placeholder="qa.lead@example.com",
            key="recipient_email",
        )
        smtp_ok, smtp_missing = smtp_configuration_status()
        send_disabled = not smtp_ok
        if send_disabled:
            st.error(
                "SMTP is not configured. Missing: " + ", ".join(smtp_missing)
            )
        if st.button("Send email now", use_container_width=True, disabled=send_disabled):
            try:
                send_email_report(
                    to_email=recipient_email,
                    subject=title or "BugLens defect report",
                    body=result.rewrite.rewritten_text,
                )
            except Exception as exc:
                st.error(f"Email sending failed: {exc}")
            else:
                st.success(f"Report sent to {recipient_email}.")
        st.download_button(
            "⬇️ Download rewritten report (.md)",
            data=result.rewrite.rewritten_text,
            file_name="buglens_rewrite.md",
            mime="text/markdown",
        )

        with st.expander("🔍 Full JSON output (for debugging / API testing)"):
            st.code(result.to_json(), language="json")
