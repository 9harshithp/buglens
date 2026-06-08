from __future__ import annotations

from html import escape
from typing import Sequence

import streamlit as st


NAV_PAGES = {
    "dashboard": {
        "label": "Dashboard",
        "icon": "◈",
        "subtitle": "Overview and quality trends",
    },
    "analyze": {
        "label": "Analyze Defect",
        "icon": "◎",
        "subtitle": "Score and rewrite a report",
    },
    "history": {
        "label": "History",
        "icon": "◷",
        "subtitle": "Past analyses at a glance",
    },
    "compare": {
        "label": "Compare",
        "icon": "⇄",
        "subtitle": "Side-by-side analysis",
    },
    "settings": {
        "label": "Settings",
        "icon": "⚙",
        "subtitle": "Model and email preferences",
    },
}

# ─────────────────────────────────────────────
#  Design System CSS
# ─────────────────────────────────────────────

APP_CSS = """
<style>

/* ── DESIGN TOKENS ────────────────────────────────────── */
:root {
  /* Surfaces */
  --c-bg:          #f8fafc;
  --c-surface:     #ffffff;
  --c-surface-2:   #f8fafc;

  /* Borders */
  --c-border:      #e2e8f0;
  --c-border-2:    #cbd5e1;

  /* Text */
  --c-text:        #0f172a;
  --c-text-2:      #334155;
  --c-text-3:      #64748b;
  --c-text-4:      #94a3b8;

  /* Brand */
  --c-brand:       #2563eb;
  --c-brand-h:     #1d4ed8;
  --c-brand-a:     #1e40af;
  --c-brand-lt:    #eff6ff;
  --c-brand-ring:  rgba(37,99,235,0.18);

  /* Semantic */
  --c-ok:          #059669;
  --c-ok-lt:       #ecfdf5;
  --c-ok-bd:       #a7f3d0;

  --c-warn:        #d97706;
  --c-warn-lt:     #fffbeb;
  --c-warn-bd:     #fde68a;

  --c-err:         #dc2626;
  --c-err-lt:      #fef2f2;
  --c-err-bd:      #fecaca;

  --c-info:        #0284c7;
  --c-info-lt:     #f0f9ff;
  --c-info-bd:     #bae6fd;

  /* Sidebar */
  --sb-bg:         #0f172a;
  --sb-surface:    #1e293b;
  --sb-border:     rgba(148,163,184,0.12);
  --sb-text:       #f1f5f9;
  --sb-muted:      #94a3b8;
  --sb-hover:      rgba(255,255,255,0.06);
  --sb-act-bg:     rgba(37,99,235,0.22);
  --sb-act-bd:     rgba(59,130,246,0.45);
  --sb-act-text:   #93c5fd;

  /* Shadows */
  --sh-xs: 0 1px 2px rgba(0,0,0,0.04);
  --sh-sm: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
  --sh-md: 0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -1px rgba(0,0,0,0.04);
  --sh-lg: 0 10px 15px -3px rgba(0,0,0,0.07), 0 4px 6px -2px rgba(0,0,0,0.04);
  --sh-xl: 0 20px 25px -5px rgba(0,0,0,0.08), 0 10px 10px -5px rgba(0,0,0,0.03);

  /* Radii */
  --r-sm:   6px;
  --r-md:   8px;
  --r-lg:   12px;
  --r-xl:   16px;
  --r-2xl:  20px;
  --r-pill: 9999px;
}

/* ── GLOBAL ───────────────────────────────────────────── */
* { box-sizing: border-box; }

.stApp {
  background-color: var(--c-bg) !important;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
               'Helvetica Neue', Arial, sans-serif !important;
}

.block-container {
  padding-top: 1.75rem !important;
  padding-bottom: 3rem !important;
  max-width: 1380px !important;
}

/* Hide Streamlit's default top bar decoration */
header[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stDecoration"]   { display: none !important; }

/* ── SIDEBAR ──────────────────────────────────────────── */
section[data-testid="stSidebar"] {
  background-color: var(--sb-bg) !important;
  border-right: 1px solid var(--sb-border) !important;
}

section[data-testid="stSidebar"] > div {
  padding: 1.25rem 1rem !important;
}

/* Force all sidebar text to sidebar palette */
section[data-testid="stSidebar"] *,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] p {
  color: var(--sb-text) !important;
}

/* Sidebar buttons — nav item style */
section[data-testid="stSidebar"] .stButton > button {
  background: transparent !important;
  color: var(--sb-muted) !important;
  border: 1px solid transparent !important;
  border-radius: var(--r-md) !important;
  padding: 0.55rem 0.75rem !important;
  font-size: 0.875rem !important;
  font-weight: 500 !important;
  text-align: left !important;
  box-shadow: none !important;
  letter-spacing: 0 !important;
  line-height: 1.4 !important;
  transition: background 0.15s, color 0.15s, border-color 0.15s !important;
}

section[data-testid="stSidebar"] .stButton > button:hover {
  background: var(--sb-hover) !important;
  color: var(--sb-text) !important;
  border-color: var(--sb-border) !important;
  box-shadow: none !important;
  transform: none !important;
}

/* Sidebar selectbox */
section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
  background: rgba(30,41,59,0.75) !important;
  border-color: var(--sb-border) !important;
  border-radius: var(--r-md) !important;
  color: var(--sb-text) !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] span {
  color: var(--sb-text) !important;
}

/* ── BUTTONS ──────────────────────────────────────────── */
.stButton > button {
  background: var(--c-brand) !important;
  color: #fff !important;
  border: 1px solid var(--c-brand) !important;
  border-radius: var(--r-md) !important;
  padding: 0.55rem 1.1rem !important;
  font-size: 0.875rem !important;
  font-weight: 600 !important;
  letter-spacing: 0 !important;
  box-shadow: 0 1px 2px rgba(37,99,235,0.18) !important;
  transition: background 0.15s, box-shadow 0.15s, transform 0.12s !important;
  line-height: 1.4 !important;
}

.stButton > button:hover {
  background: var(--c-brand-h) !important;
  border-color: var(--c-brand-h) !important;
  box-shadow: 0 4px 10px rgba(37,99,235,0.22) !important;
  transform: translateY(-1px) !important;
}

.stButton > button:active {
  background: var(--c-brand-a) !important;
  transform: translateY(0) !important;
}

.stButton > button:disabled {
  background: #e2e8f0 !important;
  color: #94a3b8 !important;
  border-color: #e2e8f0 !important;
  box-shadow: none !important;
  transform: none !important;
}

/* Secondary button variant (form clear, outline actions) */
[data-testid="stFormSubmitButton"].secondary > button,
.stButton.secondary > button {
  background: transparent !important;
  color: var(--c-text-2) !important;
  border: 1.5px solid var(--c-border-2) !important;
  box-shadow: none !important;
}

[data-testid="stFormSubmitButton"].secondary > button:hover,
.stButton.secondary > button:hover {
  background: var(--c-surface-2) !important;
  box-shadow: none !important;
  transform: none !important;
}

/* Download button */
[data-testid="stDownloadButton"] > button {
  background: transparent !important;
  color: var(--c-brand) !important;
  border: 1.5px solid var(--c-brand) !important;
  box-shadow: none !important;
}

[data-testid="stDownloadButton"] > button:hover {
  background: var(--c-brand-lt) !important;
  box-shadow: none !important;
  transform: none !important;
}

/* ── FORM ELEMENTS ────────────────────────────────────── */
.stTextInput input,
.stTextArea textarea {
  background: var(--c-surface) !important;
  border: 1.5px solid var(--c-border) !important;
  border-radius: var(--r-md) !important;
  color: var(--c-text) !important;
  font-size: 0.875rem !important;
  padding: 0.55rem 0.75rem !important;
  transition: border-color 0.15s, box-shadow 0.15s !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus {
  border-color: var(--c-brand) !important;
  box-shadow: 0 0 0 3px var(--c-brand-ring) !important;
  outline: none !important;
}

.stTextInput label,
.stTextArea label,
.stSelectbox label,
.stCheckbox label {
  color: var(--c-text-2) !important;
  font-size: 0.8125rem !important;
  font-weight: 600 !important;
}

div[data-baseweb="select"] > div:first-child {
  background: var(--c-surface) !important;
  border: 1.5px solid var(--c-border) !important;
  border-radius: var(--r-md) !important;
  font-size: 0.875rem !important;
  transition: border-color 0.15s !important;
}

div[data-baseweb="select"] > div:first-child:focus-within {
  border-color: var(--c-brand) !important;
  box-shadow: 0 0 0 3px var(--c-brand-ring) !important;
}

/* ── METRICS ──────────────────────────────────────────── */
[data-testid="stMetric"] {
  background: var(--c-surface) !important;
  border: 1px solid var(--c-border) !important;
  border-radius: var(--r-xl) !important;
  padding: 1rem 1.25rem !important;
  box-shadow: var(--sh-sm) !important;
}

[data-testid="stMetricValue"] {
  font-size: 1.75rem !important;
  font-weight: 800 !important;
  color: var(--c-text) !important;
  line-height: 1.1 !important;
}

[data-testid="stMetricLabel"] {
  font-size: 0.72rem !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.07em !important;
  color: var(--c-text-3) !important;
}

/* ── EXPANDERS ────────────────────────────────────────── */
.streamlit-expanderHeader {
  background: var(--c-surface-2) !important;
  border: 1px solid var(--c-border) !important;
  border-radius: var(--r-md) !important;
  font-weight: 600 !important;
  font-size: 0.875rem !important;
  color: var(--c-text-2) !important;
  padding: 0.75rem 1rem !important;
}

/* ── BORDERED CONTAINERS ──────────────────────────────── */
[data-testid="stVerticalBlockBorderWrapper"] {
  border: 1px solid var(--c-border) !important;
  border-radius: var(--r-xl) !important;
  box-shadow: var(--sh-sm) !important;
  overflow: hidden !important;
  padding: 1rem !important;
}

/* ── ALERTS ───────────────────────────────────────────── */
[data-testid="stAlert"] {
  border-radius: var(--r-lg) !important;
  font-size: 0.875rem !important;
}

/* ── SPINNER ──────────────────────────────────────────── */
.stSpinner > div { border-top-color: var(--c-brand) !important; }

/* ── PROGRESS ─────────────────────────────────────────── */
.stProgress > div > div > div {
  background: var(--c-brand) !important;
  border-radius: var(--r-pill) !important;
}

/* ─────────────────────────────────────────────────────────
   CUSTOM COMPONENTS
   ───────────────────────────────────────────────────────── */

/* Page header */
.bl-page-header { margin-bottom: 1.5rem; }

.bl-page-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--c-text);
  line-height: 1.2;
  margin: 0;
  letter-spacing: -0.025em;
}

.bl-page-subtitle {
  font-size: 0.9rem;
  color: var(--c-text-3);
  margin: 0.25rem 0 0;
  line-height: 1.5;
}

/* Cards */
.bl-card {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--r-xl);
  padding: 1.25rem;
  box-shadow: var(--sh-sm);
}

/* Metric grid */
.bl-metric-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.bl-metric-card {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--r-xl);
  padding: 1.25rem 1.25rem 1rem;
  box-shadow: var(--sh-sm);
  position: relative;
  overflow: hidden;
}

.bl-metric-card::after {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  border-radius: 3px 3px 0 0;
}

.bl-metric-card.primary::after { background: var(--c-brand); }
.bl-metric-card.success::after { background: var(--c-ok); }
.bl-metric-card.warning::after { background: var(--c-warn); }
.bl-metric-card.danger::after  { background: var(--c-err); }
.bl-metric-card.info::after    { background: var(--c-info); }
.bl-metric-card.neutral::after { background: var(--c-border-2); }

.bl-metric-icon {
  font-size: 1.4rem;
  margin-bottom: 0.65rem;
  display: block;
  line-height: 1;
}

.bl-metric-value {
  font-size: 2rem;
  font-weight: 800;
  color: var(--c-text);
  line-height: 1;
  letter-spacing: -0.025em;
}

.bl-metric-label {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--c-text-4);
  margin-top: 0.45rem;
}

.bl-metric-caption {
  font-size: 0.8125rem;
  color: var(--c-text-3);
  margin-top: 0.2rem;
  line-height: 1.4;
}

/* Score card */
.bl-score-card {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--r-xl);
  padding: 1.5rem;
  box-shadow: var(--sh-sm);
}

.bl-score-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.bl-score-label {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--c-text-4);
}

.bl-score-grade {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: var(--r-md);
  font-size: 1.1rem;
  font-weight: 800;
}

.bl-score-grade.primary { background: var(--c-brand-lt); color: var(--c-brand); }
.bl-score-grade.success { background: var(--c-ok-lt);   color: var(--c-ok); }
.bl-score-grade.warning { background: var(--c-warn-lt); color: var(--c-warn); }
.bl-score-grade.danger  { background: var(--c-err-lt);  color: var(--c-err); }
.bl-score-grade.info    { background: var(--c-info-lt); color: var(--c-info); }
.bl-score-grade.neutral { background: var(--c-border);  color: var(--c-text-2); }

.bl-score-number {
  font-size: 3.75rem;
  font-weight: 900;
  line-height: 1;
  letter-spacing: -0.04em;
  color: var(--c-text);
}

.bl-score-denom {
  font-size: 1.1rem;
  color: var(--c-text-4);
  font-weight: 500;
  margin-left: 0.1em;
}

.bl-score-verdict {
  font-size: 0.875rem;
  color: var(--c-text-3);
  margin-top: 0.4rem;
  line-height: 1.5;
}

.bl-score-bar-track {
  width: 100%;
  height: 6px;
  background: var(--c-border);
  border-radius: var(--r-pill);
  overflow: hidden;
  margin-top: 1rem;
}

.bl-score-bar-fill {
  height: 100%;
  border-radius: var(--r-pill);
}

.bl-score-bar-fill.primary { background: linear-gradient(90deg, #60a5fa, #2563eb); }
.bl-score-bar-fill.success { background: linear-gradient(90deg, #34d399, #059669); }
.bl-score-bar-fill.warning { background: linear-gradient(90deg, #fbbf24, #d97706); }
.bl-score-bar-fill.danger  { background: linear-gradient(90deg, #f87171, #dc2626); }
.bl-score-bar-fill.info    { background: linear-gradient(90deg, #38bdf8, #0284c7); }
.bl-score-bar-fill.neutral { background: var(--c-border-2); }

/* Chips / badges */
.bl-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.25rem 0.65rem;
  border-radius: var(--r-pill);
  font-size: 0.74rem;
  font-weight: 700;
  letter-spacing: 0.01em;
  border: 1px solid transparent;
  white-space: nowrap;
  line-height: 1.4;
}

.bl-chip-neutral { background: #f1f5f9; color: #475569; border-color: #e2e8f0; }
.bl-chip-primary { background: var(--c-brand-lt); color: var(--c-brand); border-color: rgba(37,99,235,0.15); }
.bl-chip-success { background: var(--c-ok-lt);    color: var(--c-ok);    border-color: rgba(5,150,105,0.15); }
.bl-chip-warning { background: var(--c-warn-lt);  color: var(--c-warn);  border-color: rgba(217,119,6,0.15); }
.bl-chip-danger  { background: var(--c-err-lt);   color: var(--c-err);   border-color: rgba(220,38,38,0.15); }
.bl-chip-info    { background: var(--c-info-lt);  color: var(--c-info);  border-color: rgba(2,132,199,0.15); }

/* Inline issue items */
.bl-issue-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  border-radius: var(--r-lg);
  border: 1px solid;
  border-left: 4px solid;
  background: var(--c-surface);
  margin-bottom: 0.5rem;
}

.bl-issue-item.danger  { border-color: var(--c-err-bd); background: var(--c-err-lt); border-left-color: var(--c-err); }
.bl-issue-item.warning { border-color: var(--c-warn-bd); background: var(--c-warn-lt); border-left-color: var(--c-warn); }
.bl-issue-item.info    { border-color: var(--c-info-bd); background: var(--c-info-lt); border-left-color: var(--c-info); }

.bl-issue-badge {
  flex-shrink: 0;
  padding: 0.15rem 0.45rem;
  border-radius: var(--r-sm);
  font-size: 0.62rem;
  font-weight: 800;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  margin-top: 0.1rem;
  color: #fff;
}

.bl-issue-item.danger  .bl-issue-badge { background: var(--c-err); }
.bl-issue-item.warning .bl-issue-badge { background: var(--c-warn); }
.bl-issue-item.info    .bl-issue-badge { background: var(--c-info); }

.bl-issue-body { flex: 1; min-width: 0; }

.bl-issue-field {
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--c-text-2);
  font-family: 'SF Mono', 'Fira Code', monospace;
  margin-bottom: 0.2rem;
  text-transform: lowercase;
}

.bl-issue-message {
  font-size: 0.875rem;
  color: var(--c-text);
  line-height: 1.45;
  margin-bottom: 0.3rem;
}

.bl-issue-suggestion {
  font-size: 0.8rem;
  color: var(--c-text-3);
  line-height: 1.45;
}

/* Quick action cards */
.bl-action-card {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--r-xl);
  padding: 1.25rem;
  box-shadow: var(--sh-sm);
  height: 100%;
  transition: box-shadow 0.15s, transform 0.12s;
}

.bl-action-icon  { font-size: 1.75rem; margin-bottom: 0.75rem; display: block; }
.bl-action-title { font-size: 1rem; font-weight: 700; color: var(--c-text); margin: 0 0 0.3rem; }
.bl-action-desc  { font-size: 0.875rem; color: var(--c-text-3); line-height: 1.5; margin: 0 0 1rem; }

/* Sidebar active nav item */
.bl-nav-active {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  padding: 0.55rem 0.75rem;
  border-radius: var(--r-md);
  background: var(--sb-act-bg);
  border: 1px solid var(--sb-act-bd);
  margin-bottom: 0.25rem;
  cursor: default;
}

.bl-nav-active-icon  { font-size: 0.9rem; color: var(--sb-act-text); flex-shrink: 0; margin-top: 0.1rem; }
.bl-nav-active-label { font-size: 0.875rem; font-weight: 700; color: var(--sb-act-text); line-height: 1.3; display: block; }
.bl-nav-active-sub   { font-size: 0.72rem; color: rgba(147,197,253,0.65); line-height: 1.3; display: block; }

/* Sidebar meta elements */
.bl-sb-wordmark {
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--sb-border);
}

.bl-sb-logo-text {
  font-size: 1.0625rem;
  font-weight: 800;
  color: #f1f5f9;
  letter-spacing: -0.01em;
}

.bl-sb-logo-sub {
  font-size: 0.72rem;
  color: var(--sb-muted);
  margin-top: 1px;
}

.bl-sb-profile {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  padding: 0.7rem 0.75rem;
  background: rgba(30,41,59,0.60);
  border: 1px solid var(--sb-border);
  border-radius: var(--r-md);
  margin-bottom: 0.5rem;
}

.bl-sb-avatar {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #7c3aed);
  color: #fff;
  font-size: 0.85rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.bl-sb-name { font-size: 0.875rem; font-weight: 600; color: var(--sb-text); line-height: 1.3; }
.bl-sb-role { font-size: 0.72rem; color: var(--sb-muted); line-height: 1.3; }

.bl-sb-section {
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.09em;
  color: var(--sb-muted);
  margin: 1rem 0 0.4rem;
  padding: 0 4px;
}

.bl-sb-sep {
  height: 1px;
  background: var(--sb-border);
  margin: 0.85rem 0;
}

.bl-sb-stat {
  background: rgba(30,41,59,0.55);
  border: 1px solid var(--sb-border);
  border-radius: var(--r-md);
  padding: 0.65rem 0.8rem;
  margin-bottom: 0.4rem;
}

.bl-sb-stat-label {
  font-size: 0.62rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--sb-muted);
  margin-bottom: 0.15rem;
}

.bl-sb-stat-value {
  font-size: 1rem;
  font-weight: 800;
  color: var(--sb-text);
  line-height: 1.2;
}

.bl-sb-dot {
  display: inline-block;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  margin-right: 5px;
  vertical-align: middle;
}

.bl-sb-dot.ok   { background: var(--c-ok); }
.bl-sb-dot.warn { background: var(--c-warn); }

/* Empty state */
.bl-empty {
  text-align: center;
  padding: 3rem 1.5rem;
  border: 1.5px dashed var(--c-border);
  border-radius: var(--r-2xl);
  background: rgba(248,250,252,0.55);
}

.bl-empty-icon  { font-size: 2.5rem; margin-bottom: 1rem; display: block; opacity: 0.55; line-height: 1; }
.bl-empty-title { font-size: 1.0625rem; font-weight: 700; color: var(--c-text); margin: 0 0 0.5rem; }
.bl-empty-body  { font-size: 0.875rem; color: var(--c-text-3); max-width: 38rem; margin: 0 auto; line-height: 1.6; }
.bl-empty-hint  { font-size: 0.8125rem; color: var(--c-text-4); margin-top: 0.75rem; }

/* Info card */
.bl-info-card {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--r-xl);
  padding: 1.25rem;
  box-shadow: var(--sh-sm);
}

.bl-info-card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.65rem;
}

.bl-info-card-title { font-size: 0.9375rem; font-weight: 700; color: var(--c-text); margin: 0; }
.bl-info-card-body  { font-size: 0.875rem; color: var(--c-text-3); line-height: 1.6; }

.bl-info-card-footer {
  font-size: 0.8rem;
  color: var(--c-text-4);
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--c-border);
}

/* Auth layout */
.bl-auth-outer {
  display: grid;
  grid-template-columns: minmax(0,1.25fr) minmax(300px,0.75fr);
  gap: 1.5rem;
  align-items: start;
}

.bl-auth-hero {
  background: linear-gradient(135deg,#f8fafc 0%,#eff6ff 55%,#f0f9ff 100%);
  border: 1px solid var(--c-border);
  border-radius: var(--r-2xl);
  padding: 2rem;
  box-shadow: var(--sh-lg);
}

.bl-auth-wordmark {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--c-brand);
  padding: 0.35rem 0.8rem;
  background: var(--c-brand-lt);
  border-radius: var(--r-pill);
  border: 1px solid rgba(37,99,235,0.15);
  margin-bottom: 1.25rem;
}

.bl-auth-headline {
  font-size: 2.25rem;
  font-weight: 900;
  line-height: 1.06;
  letter-spacing: -0.03em;
  color: var(--c-text);
  max-width: 18ch;
  margin: 0 0 0.85rem;
}

.bl-auth-lead {
  font-size: 1rem;
  color: var(--c-text-3);
  line-height: 1.6;
  max-width: 50ch;
  margin: 0;
}

.bl-auth-features {
  display: grid;
  grid-template-columns: repeat(3,1fr);
  gap: 0.75rem;
  margin-top: 1.5rem;
}

.bl-auth-feature {
  background: rgba(255,255,255,0.80);
  border: 1px solid var(--c-border);
  border-radius: var(--r-lg);
  padding: 1rem;
}

.bl-auth-feature-icon  { font-size: 1.25rem; margin-bottom: 0.4rem; display: block; }
.bl-auth-feature-title { font-size: 0.875rem; font-weight: 700; color: var(--c-text); margin: 0 0 0.25rem; }
.bl-auth-feature-body  { font-size: 0.8rem; color: var(--c-text-3); line-height: 1.5; margin: 0; }

.bl-auth-form-panel {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--r-2xl);
  padding: 1.75rem;
  box-shadow: var(--sh-xl);
  position: sticky;
  top: 1rem;
}

.bl-auth-tab-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
  background: var(--c-surface-2);
  border: 1px solid var(--c-border);
  border-radius: var(--r-lg);
  padding: 0.3rem;
  margin-bottom: 1.25rem;
}

.bl-auth-tab {
  padding: 0.5rem;
  border-radius: var(--r-md);
  font-size: 0.875rem;
  font-weight: 600;
  text-align: center;
  cursor: pointer;
  border: none;
  transition: background 0.15s, color 0.15s;
}

.bl-auth-tab.active {
  background: var(--c-surface);
  color: var(--c-text);
  box-shadow: var(--sh-sm);
}

.bl-auth-tab.inactive { background: transparent; color: var(--c-text-3); }

/* Section heading */
.bl-section-heading {
  font-size: 0.9375rem;
  font-weight: 700;
  color: var(--c-text);
  margin: 0 0 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid var(--c-border);
}

/* History item card */
.bl-history-card {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--r-xl);
  padding: 1.125rem 1.25rem;
  box-shadow: var(--sh-xs);
  transition: box-shadow 0.15s;
  margin-bottom: 0.75rem;
}

.bl-history-card:hover { box-shadow: var(--sh-md); }

.bl-history-title {
  font-size: 0.9375rem;
  font-weight: 700;
  color: var(--c-text);
  margin: 0 0 0.2rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.bl-history-meta { font-size: 0.8rem; color: var(--c-text-4); }

.bl-history-score {
  font-size: 1.75rem;
  font-weight: 900;
  color: var(--c-text);
  letter-spacing: -0.025em;
  line-height: 1;
}

.bl-history-denom { font-size: 0.75rem; color: var(--c-text-4); font-weight: 500; }

/* Compare entry card */
.bl-compare-card {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--r-xl);
  padding: 1.25rem;
  box-shadow: var(--sh-sm);
}

.bl-compare-label {
  font-size: 0.7rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.09em;
  color: var(--c-brand);
  margin-bottom: 0.5rem;
}

/* Field diff row */
.bl-field-diff {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--r-lg);
  padding: 0.875rem 1rem;
  margin-bottom: 0.5rem;
}

.bl-field-diff-label {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--c-text-4);
  margin-bottom: 0.5rem;
}

.bl-field-diff-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.bl-field-diff-side {
  font-size: 0.8125rem;
  color: var(--c-text-2);
  line-height: 1.5;
  padding: 0.5rem 0.75rem;
  background: var(--c-surface-2);
  border-radius: var(--r-md);
  border: 1px solid var(--c-border);
}

.bl-field-diff-side-label {
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--c-text-4);
  margin-bottom: 0.25rem;
}

/* Suggestion list */
.bl-suggestion-item {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  padding: 0.65rem 0;
  border-bottom: 1px solid var(--c-border);
  font-size: 0.875rem;
  color: var(--c-text-2);
  line-height: 1.5;
}

.bl-suggestion-item:last-child { border-bottom: none; }

.bl-suggestion-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--c-brand);
  flex-shrink: 0;
  margin-top: 0.45rem;
}

/* Settings section */
.bl-settings-panel {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--r-xl);
  padding: 1.5rem;
  box-shadow: var(--sh-sm);
}

.bl-settings-panel-title {
  font-size: 1rem;
  font-weight: 700;
  color: var(--c-text);
  margin: 0 0 1.25rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid var(--c-border);
}

/* Demo account card */
.bl-demo-card {
  background: var(--c-surface-2);
  border: 1px solid var(--c-border);
  border-radius: var(--r-lg);
  padding: 0.875rem 1rem;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.bl-demo-avatar {
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 50%;
  background: linear-gradient(135deg,#3b82f6,#7c3aed);
  color: #fff;
  font-size: 0.9rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.bl-demo-name { font-size: 0.875rem; font-weight: 700; color: var(--c-text); }
.bl-demo-role { font-size: 0.78rem; color: var(--c-text-3); }

/* ── RESPONSIVE ───────────────────────────────────────── */
@media (max-width: 1200px) {
  .bl-metric-grid { grid-template-columns: repeat(2,minmax(0,1fr)); }
  .bl-auth-features { grid-template-columns: 1fr 1fr; }
}

@media (max-width: 900px) {
  .bl-auth-outer { grid-template-columns: 1fr; }
  .bl-metric-grid { grid-template-columns: repeat(2,minmax(0,1fr)); }
}

@media (max-width: 640px) {
  .bl-metric-grid { grid-template-columns: 1fr 1fr; }
  .bl-auth-headline { font-size: 1.75rem; }
  .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
  .bl-auth-features { grid-template-columns: 1fr; }
}
</style>
"""


# ─────────────────────────────────────────────
#  Component helpers
# ─────────────────────────────────────────────

def inject_theme() -> None:
    st.markdown(APP_CSS, unsafe_allow_html=True)


def render_section_header(
    title: str,
    subtitle: str | None = None,
    icon: str | None = None,
) -> None:
    icon_html = f'<span style="margin-right:0.4rem;">{escape(icon)}</span>' if icon else ""
    sub_html = f'<p class="bl-page-subtitle">{escape(subtitle)}</p>' if subtitle else ""
    st.markdown(
        f'<div class="bl-page-header">'
        f'<h2 class="bl-page-title">{icon_html}{escape(title)}</h2>'
        f'{sub_html}</div>',
        unsafe_allow_html=True,
    )


def render_chip(text: str, tone: str = "neutral", icon: str | None = None) -> None:
    prefix = f"{escape(icon)} " if icon else ""
    st.markdown(
        f'<span class="bl-chip bl-chip-{tone}">{prefix}{escape(text)}</span>',
        unsafe_allow_html=True,
    )


def render_metric_cards(metrics: Sequence[dict]) -> None:
    if not metrics:
        return
    cards = []
    for m in metrics:
        tone = m.get("tone", "neutral")
        icon = escape(m.get("icon", ""))
        value = escape(str(m.get("value", "")))
        label = escape(m.get("label", ""))
        caption = escape(m.get("caption", ""))
        cards.append(
            f'<div class="bl-metric-card {tone}">'
            f'<span class="bl-metric-icon">{icon}</span>'
            f'<div class="bl-metric-value">{value}</div>'
            f'<div class="bl-metric-label">{label}</div>'
            f'<div class="bl-metric-caption">{caption}</div>'
            f'</div>'
        )
    st.markdown(
        f'<div class="bl-metric-grid">{"".join(cards)}</div>',
        unsafe_allow_html=True,
    )


def render_score_card(
    score: int,
    grade: str,
    verdict: str,
    mode: str,
    tone: str,
) -> None:
    st.markdown(
        f'<div class="bl-score-card">'
        f'  <div class="bl-score-header">'
        f'    <span class="bl-score-label">Quality Score</span>'
        f'    <span class="bl-score-grade {tone}">{escape(grade)}</span>'
        f'  </div>'
        f'  <div>'
        f'    <span class="bl-score-number">{score}</span>'
        f'    <span class="bl-score-denom">/100</span>'
        f'  </div>'
        f'  <div class="bl-score-verdict">{escape(verdict)}</div>'
        f'  <div class="bl-score-bar-track">'
        f'    <div class="bl-score-bar-fill {tone}" style="width:{score}%"></div>'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    if mode == "local":
        st.markdown(
            '<span class="bl-chip bl-chip-neutral" style="margin-top:0.5rem; display:inline-flex;">'
            '◌ Local rewrite mode</span>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<span class="bl-chip bl-chip-success" style="margin-top:0.5rem; display:inline-flex;">'
            f'✦ AI rewrite — {escape(mode)}</span>',
            unsafe_allow_html=True,
        )


def render_issue_item(
    field: str,
    severity: str,
    code: str,
    message: str,
    suggestion: str,
    tone: str,
) -> None:
    st.markdown(
        f'<div class="bl-issue-item {tone}">'
        f'  <span class="bl-issue-badge">{escape(severity)}</span>'
        f'  <div class="bl-issue-body">'
        f'    <div class="bl-issue-field">{escape(field)}</div>'
        f'    <div class="bl-issue-message">{escape(message)}</div>'
        f'    <div class="bl-issue-suggestion">💡 {escape(suggestion)}</div>'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_nav_item_active(icon: str, label: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="bl-nav-active">'
        f'  <span class="bl-nav-active-icon">{escape(icon)}</span>'
        f'  <div>'
        f'    <span class="bl-nav-active-label">{escape(label)}</span>'
        f'    <span class="bl-nav-active-sub">{escape(subtitle)}</span>'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_info_card(
    title: str,
    body: str,
    *,
    tone: str = "neutral",
    footer: str | None = None,
) -> None:
    footer_html = (
        f'<div class="bl-info-card-footer">{escape(footer)}</div>'
        if footer else ""
    )
    chip_html = f'<span class="bl-chip bl-chip-{tone}">Insight</span>'
    st.markdown(
        f'<div class="bl-info-card">'
        f'  <div class="bl-info-card-header">'
        f'    <span class="bl-info-card-title">{escape(title)}</span>'
        f'    {chip_html}'
        f'  </div>'
        f'  <div class="bl-info-card-body">{escape(body)}</div>'
        f'  {footer_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_empty_state(
    title: str,
    body: str,
    action_hint: str | None = None,
    icon: str = "◌",
) -> None:
    hint_html = (
        f'<p class="bl-empty-hint">{escape(action_hint)}</p>'
        if action_hint else ""
    )
    st.markdown(
        f'<div class="bl-empty">'
        f'  <span class="bl-empty-icon">{escape(icon)}</span>'
        f'  <h3 class="bl-empty-title">{escape(title)}</h3>'
        f'  <p class="bl-empty-body">{escape(body)}</p>'
        f'  {hint_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_auth_hero(
    title: str,
    body: str,
    features: Sequence[dict],
) -> None:
    feat_html = []
    for f in features:
        feat_html.append(
            f'<div class="bl-auth-feature">'
            f'  <span class="bl-auth-feature-icon">{escape(f.get("icon","✦"))}</span>'
            f'  <div class="bl-auth-feature-title">{escape(f.get("title",""))}</div>'
            f'  <p class="bl-auth-feature-body">{escape(f.get("body",""))}</p>'
            f'</div>'
        )
    st.markdown(
        f'<div class="bl-auth-hero">'
        f'  <div class="bl-auth-wordmark">🪲 BugLens</div>'
        f'  <h1 class="bl-auth-headline">{escape(title)}</h1>'
        f'  <p class="bl-auth-lead">{escape(body)}</p>'
        f'  <div class="bl-auth-features">{"".join(feat_html)}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_nav_card(label: str, subtitle: str, icon: str, active: bool = False) -> None:
    """Legacy compat shim — delegates to render_nav_item_active when active."""
    if active:
        render_nav_item_active(icon, label, subtitle)
