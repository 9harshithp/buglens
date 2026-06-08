#!/usr/bin/env python3
"""BugLens – Defect Quality Checker  |  Professional Presentation Generator"""

from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# ── Palette ──────────────────────────────────────────────────────────────────
BG      = RGBColor(0x0D,0x11,0x17)
SURF    = RGBColor(0x1A,0x25,0x3A)
SURF2   = RGBColor(0x0F,0x17,0x2A)
BLUE    = RGBColor(0x25,0x63,0xEB)
BLUE_L  = RGBColor(0x60,0xA5,0xFA)
PURP    = RGBColor(0x7C,0x3A,0xED)
PURP_L  = RGBColor(0xC4,0xB5,0xFD)
CYAN    = RGBColor(0x06,0xB6,0xD4)
CYAN_L  = RGBColor(0xA5,0xF3,0xFC)
WHITE   = RGBColor(0xFF,0xFF,0xFF)
LIGHT   = RGBColor(0xF1,0xF5,0xF9)
MUTED   = RGBColor(0x94,0xA3,0xB8)
MUTED2  = RGBColor(0x47,0x55,0x69)
GREEN   = RGBColor(0x05,0x96,0x69)
GREEN_L = RGBColor(0xA7,0xF3,0xD0)
YELLOW  = RGBColor(0xD9,0x77,0x06)
RED     = RGBColor(0xDC,0x26,0x26)
ORANGE  = RGBColor(0xEA,0x58,0x0C)

SW = Inches(13.333)
SH = Inches(7.5)

# ── Primitive helpers ─────────────────────────────────────────────────────────
def _bg(slide, color=BG):
    f = slide.background.fill; f.solid(); f.fore_color.rgb = color

def _rect(slide, x, y, w, h, fill=SURF, line=None, lw=0.75, round_=False):
    s = slide.shapes.add_shape(5 if round_ else 1, x, y, w, h)
    if fill:
        s.fill.solid(); s.fill.fore_color.rgb = fill
    else:
        s.fill.background()
    if line:
        s.line.color.rgb = line; s.line.width = Pt(lw)
    else:
        s.line.fill.background()
    return s

def _txt(slide, text, x, y, w, h, size=14, color=WHITE, bold=False,
         italic=False, align=PP_ALIGN.LEFT, wrap=True):
    b  = slide.shapes.add_textbox(x, y, w, h)
    tf = b.text_frame; tf.word_wrap = wrap
    p  = tf.paragraphs[0]; p.alignment = align
    r  = p.add_run(); r.text = text
    r.font.size = Pt(size); r.font.color.rgb = color
    r.font.bold = bold; r.font.italic = italic
    return b

def _notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text

def _hdr(slide, title, subtitle="", num=""):
    """Standard header bar for slides 2-25."""
    _rect(slide, 0, 0, SW, Inches(1.0), fill=SURF2)
    _rect(slide, 0, 0, Inches(0.18), Inches(1.0), fill=BLUE)
    _txt(slide, title, Inches(0.35), Inches(0.08), Inches(10), Inches(0.5),
         size=26, bold=True, color=WHITE)
    if subtitle:
        _txt(slide, subtitle, Inches(0.35), Inches(0.56), Inches(10), Inches(0.38),
             size=12, color=MUTED)
    if num:
        _txt(slide, num, Inches(12.5), Inches(0.3), Inches(0.8), Inches(0.4),
             size=11, color=MUTED2, align=PP_ALIGN.RIGHT)
    _rect(slide, 0, SH-Inches(0.28), SW, Inches(0.28), fill=SURF2)
    _txt(slide, "BugLens – Defect Quality Checker",
         Inches(0.35), SH-Inches(0.26), Inches(6), Inches(0.24),
         size=8, color=MUTED2)

def _card(slide, x, y, w, h, accent=None, title="", body="",
          title_size=13, body_size=10, bg=SURF):
    """Rounded card with optional left-accent stripe."""
    _rect(slide, x, y, w, h, fill=bg, round_=True)
    if accent:
        _rect(slide, x, y, Inches(0.1), h, fill=accent)
    ox = Inches(0.18) if accent else Inches(0.12)
    if title:
        _txt(slide, title, x+ox, y+Inches(0.1), w-ox-Inches(0.1),
             Inches(0.35), size=title_size, bold=True, color=WHITE)
    if body:
        _txt(slide, body, x+ox, y+Inches(0.42), w-ox-Inches(0.1),
             h-Inches(0.52), size=body_size, color=MUTED, wrap=True)

def _kpi(slide, x, y, w, h, value, label, sub="", color=BLUE):
    """KPI metric card."""
    _rect(slide, x, y, w, h, fill=SURF, round_=True)
    _rect(slide, x, y, w, Inches(0.06), fill=color)
    _txt(slide, value, x+Inches(0.15), y+Inches(0.15), w-Inches(0.3),
         Inches(0.6), size=28, bold=True, color=color, align=PP_ALIGN.CENTER)
    _txt(slide, label, x+Inches(0.1), y+Inches(0.72), w-Inches(0.2),
         Inches(0.3), size=10, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    if sub:
        _txt(slide, sub, x+Inches(0.1), y+Inches(0.98), w-Inches(0.2),
             Inches(0.35), size=8, color=MUTED, align=PP_ALIGN.CENTER, wrap=True)

def _flow(slide, items, x, y, w, h_box, gap, colors, direction="v"):
    """Render a vertical or horizontal flow of boxes with arrow labels."""
    cy = y
    for i, (lbl, sub) in enumerate(items):
        c = colors[i % len(colors)]
        _rect(slide, x, cy, w, h_box, fill=c, round_=True)
        _txt(slide, lbl, x+Inches(0.1), cy+Inches(0.08),
             w-Inches(0.2), Inches(0.35), size=11, bold=True, color=WHITE,
             align=PP_ALIGN.CENTER)
        if sub:
            _txt(slide, sub, x+Inches(0.1), cy+Inches(0.42),
                 w-Inches(0.2), h_box-Inches(0.5), size=8.5, color=MUTED,
                 align=PP_ALIGN.CENTER, wrap=True)
        if i < len(items)-1:
            ax = x + w/2 - Inches(0.08)
            ay = cy + h_box + Inches(0.04)
            _rect(slide, ax, ay, Inches(0.16), gap-Inches(0.08), fill=MUTED2)
            _txt(slide, "▼", ax-Inches(0.1), ay+gap-Inches(0.28),
                 Inches(0.36), Inches(0.26), size=9, color=MUTED2,
                 align=PP_ALIGN.CENTER)
        cy += h_box + gap

def _table(slide, x, y, w, rows, col_widths, hdr_color=BLUE):
    """Simple styled table."""
    rh = Inches(0.38)
    for r, row in enumerate(rows):
        ry = y + r * rh
        bg = hdr_color if r == 0 else (SURF if r % 2 == 0 else SURF2)
        _rect(slide, x, ry, w, rh, fill=bg)
        cx = x
        for c, (cell, cw) in enumerate(zip(row, col_widths)):
            col = WHITE if r == 0 else (LIGHT if r % 2 == 0 else MUTED)
            _txt(slide, str(cell), cx+Inches(0.08), ry+Inches(0.06),
                 cw-Inches(0.1), rh-Inches(0.08),
                 size=9 if r > 0 else 10,
                 color=col, bold=(r == 0))
            cx += cw

# ── Slide builders ────────────────────────────────────────────────────────────

def s01_title(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(sl)
    # Decorative gradient band
    _rect(sl, Inches(7.8), 0, Inches(5.5), SH, fill=SURF2)
    _rect(sl, Inches(7.8), 0, Inches(0.06), SH, fill=BLUE)
    # Decorative circles
    for (cx,cy,cr,col) in [
        (Inches(10.5),Inches(1.5),Inches(2.2),RGBColor(0x1D,0x40,0xAF)),
        (Inches(12.0),Inches(4.5),Inches(1.8),RGBColor(0x14,0x2A,0x60)),
        (Inches(9.0), Inches(5.5),Inches(1.4),RGBColor(0x1E,0x29,0x3B)),
    ]:
        _rect(sl, cx-cr/2, cy-cr/2, cr, cr, fill=col, round_=True)
    # Bug icon circle
    _rect(sl, Inches(0.5), Inches(0.6), Inches(1.1), Inches(1.1), fill=BLUE, round_=True)
    _txt(sl, "BL", Inches(0.5), Inches(0.65), Inches(1.1), Inches(0.9),
         size=30, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    # Title
    _txt(sl, "BugLens", Inches(0.4), Inches(1.9), Inches(7.0), Inches(1.5),
         size=64, bold=True, color=WHITE)
    _txt(sl, "Defect Quality Checker", Inches(0.4), Inches(3.4), Inches(7.0),
         Inches(0.7), size=26, bold=False, color=CYAN_L)
    _rect(sl, Inches(0.4), Inches(4.1), Inches(2.5), Inches(0.05), fill=CYAN)
    _txt(sl, "Intelligent Defect Validation & Quality Assessment Platform",
         Inches(0.4), Inches(4.25), Inches(7.0), Inches(0.5),
         size=13, color=MUTED, italic=True)
    # Tags
    for i,(tag,col) in enumerate([
        ("Python",BLUE),("FastAPI",PURP),("Streamlit",CYAN),("Pytest",GREEN)
    ]):
        tx = Inches(0.4) + i*Inches(1.6)
        _rect(sl, tx, Inches(5.1), Inches(1.4), Inches(0.38), fill=col, round_=True)
        _txt(sl, tag, tx, Inches(5.12), Inches(1.4), Inches(0.34),
             size=10, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    _txt(sl, "Presented by  ·  Software / QA Engineering",
         Inches(0.4), Inches(6.6), Inches(5), Inches(0.4),
         size=11, color=MUTED2)
    _notes(sl, "Welcome. I'm going to walk you through BugLens, a full-stack defect quality checker I built to solve a real QA problem. The platform validates defect reports, scores their quality, and generates AI-assisted rewrites so engineers receive actionable, well-structured tickets instead of vague ones.")

def s02_exec(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(sl); _hdr(sl,"Executive Summary","Problem → Solution → Business Value","02")
    W3 = Inches(3.9); gap = Inches(0.28)
    for i,(title,icon,body,col) in enumerate([
        ("The Problem","⚠",
         "QA teams submit vague, incomplete defect reports — missing steps, unclear environments, no expected vs. actual outcome. Developers waste hours chasing context.",
         RED),
        ("The Solution","✦",
         "BugLens validates every field, scores report quality 0–100, surfaces specific issues with fix suggestions, and rewrites the ticket into a professional, developer-ready format.",
         BLUE),
        ("Business Value","◎",
         "Fewer clarification cycles, faster resolution times, measurable quality gates, and a scalable REST API that plugs into any CI/CD or issue-tracking workflow.",
         GREEN),
    ]):
        x = Inches(0.35) + i*(W3+gap)
        _rect(sl, x, Inches(1.15), W3, Inches(5.7), fill=SURF, round_=True)
        _rect(sl, x, Inches(1.15), W3, Inches(0.06), fill=col)
        _rect(sl, x+W3/2-Inches(0.45), Inches(1.35), Inches(0.9), Inches(0.9),
              fill=col, round_=True)
        _txt(sl, icon, x+W3/2-Inches(0.45), Inches(1.38), Inches(0.9), Inches(0.9),
             size=20, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        _txt(sl, title, x+Inches(0.15), Inches(2.4), W3-Inches(0.3), Inches(0.5),
             size=18, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        _txt(sl, body, x+Inches(0.2), Inches(2.95), W3-Inches(0.4), Inches(3.6),
             size=12, color=MUTED, wrap=True, align=PP_ALIGN.LEFT)
    _notes(sl,"Three-column executive summary. The problem: poor defect quality costs teams debugging time. The solution: automated validation + scoring + rewrite. The business value: quantifiable quality gates and REST API integration. Hit each column in order — spend about 30 seconds per column.")

def s03_problem(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(sl); _hdr(sl,"Problem Analysis","Root causes and impact of poor defect reporting","03")
    # Left: big stat
    _rect(sl, Inches(0.35), Inches(1.2), Inches(4.0), Inches(5.7), fill=SURF2, round_=True)
    _rect(sl, Inches(0.35), Inches(1.2), Inches(4.0), Inches(0.06), fill=RED)
    _txt(sl,"60%", Inches(0.5),Inches(1.5),Inches(3.7),Inches(1.4),
         size=72,bold=True,color=RED,align=PP_ALIGN.CENTER)
    _txt(sl,"of defect tickets require\nat least one follow-up\nclarification comment",
         Inches(0.5),Inches(2.85),Inches(3.7),Inches(1.1),
         size=12,color=MUTED,align=PP_ALIGN.CENTER,wrap=True)
    _txt(sl,"Industry research — QA cost-of-quality studies",
         Inches(0.5),Inches(4.0),Inches(3.7),Inches(0.3),
         size=8,color=MUTED2,italic=True,align=PP_ALIGN.CENTER)
    _rect(sl,Inches(0.5),Inches(4.5),Inches(3.6),Inches(0.04),fill=MUTED2)
    pain = [
        (RED,"Missing reproduction steps","Dev cannot reproduce; ticket bounces back to QA"),
        (YELLOW,"No environment context","Works on my machine — cannot triage by platform/version"),
        (ORANGE,"Vague language","'It's broken' or 'doesn't work' — no specific evidence"),
        (PURP,"Wrong severity","Inflated priority causes wrong sprint ordering"),
    ]
    for i,(col,title,desc) in enumerate(pain):
        y = Inches(1.25)+i*Inches(1.35)
        _card(sl, Inches(4.55), y, Inches(8.5), Inches(1.22),
              accent=col, title=title, body=desc, bg=SURF)
    _notes(sl,"The left stat anchors the problem with a quantified impact. Walk through each pain point on the right — these directly map to the validation checks BugLens implements. When asked 'why did you build this?', this is slide is your evidence.")

def s04_objectives(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(sl); _hdr(sl,"Project Objectives","What BugLens is designed to achieve","04")
    objs = [
        (BLUE,"1","Validate defect reports","Detect missing fields, vague language, unnumbered steps, and environment gaps using a deterministic rule engine."),
        (PURP,"2","Score quality 0–100","Assign a weighted quality score across 6 sections with letter grade and human-readable rationale."),
        (CYAN,"3","Surface actionable issues","Return per-field issues with severity (ERROR / WARNING / INFO) and a specific fix suggestion for each."),
        (GREEN,"4","Generate professional rewrites","Produce a structured, developer-ready ticket using local rules or GPT-assisted rewrite."),
        (YELLOW,"5","Expose REST API","Provide /validate, /score, /analyze, and /history endpoints consumable by any CI/CD pipeline or ITSM."),
        (ORANGE,"6","Track history & compare","Persist analyses to SQLite, enable comparison of two reports side-by-side with delta metrics."),
    ]
    for i,(col,num,title,desc) in enumerate(objs):
        row, col_n = divmod(i, 2)
        x = Inches(0.35)+col_n*Inches(6.5)
        y = Inches(1.2)+row*Inches(1.9)
        _rect(sl,x,y,Inches(6.2),Inches(1.75),fill=SURF,round_=True)
        _rect(sl,x,y,Inches(0.55),Inches(1.75),fill=col,round_=True)
        _txt(sl,num,x,y+Inches(0.55),Inches(0.55),Inches(0.65),
             size=20,bold=True,color=WHITE,align=PP_ALIGN.CENTER)
        _txt(sl,title,x+Inches(0.65),y+Inches(0.1),Inches(5.4),Inches(0.42),
             size=13,bold=True,color=WHITE)
        _txt(sl,desc,x+Inches(0.65),y+Inches(0.55),Inches(5.4),Inches(1.1),
             size=9.5,color=MUTED,wrap=True)
    _notes(sl,"Six clear objectives mapped to deliverables. Notice that objective 5 (REST API) shows this isn't just a UI tool — it's a platform. When asked about scope, reference these objectives as the requirements baseline.")

def s05_requirements(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(sl); _hdr(sl,"Requirements Analysis","Functional and Non-Functional Requirements","05")
    # FR column
    _rect(sl,Inches(0.35),Inches(1.15),Inches(6.1),Inches(5.7),fill=SURF2,round_=True)
    _rect(sl,Inches(0.35),Inches(1.15),Inches(6.1),Inches(0.5),fill=BLUE,round_=True)
    _txt(sl,"Functional Requirements",Inches(0.45),Inches(1.18),Inches(5.9),Inches(0.45),
         size=14,bold=True,color=WHITE)
    frs = [
        "FR-01  7-field defect input form (title, description, steps, expected, actual, environment, severity)",
        "FR-02  Real-time validation with field-level issues (ERROR / WARNING / INFO)",
        "FR-03  Deterministic quality scoring — 6 weighted sections, 0–100 total",
        "FR-04  Letter grade assignment (A–F) with verdict text",
        "FR-05  Local + AI-assisted rewrite of the defect report",
        "FR-06  Analysis history with SQLite persistence (save, list, get, delete)",
        "FR-07  Side-by-side report comparison with score delta",
        "FR-08  REST API: /validate, /score, /analyze, /history endpoints",
        "FR-09  Email delivery via SMTP (configurable)",
        "FR-10  Sample defect library for demo and onboarding",
    ]
    for i,fr in enumerate(frs):
        y = Inches(1.75)+i*Inches(0.47)
        _rect(sl,Inches(0.5),y,Inches(0.3),Inches(0.3),fill=BLUE,round_=True)
        _txt(sl,fr,Inches(0.9),y,Inches(5.4),Inches(0.42),size=9,color=LIGHT,wrap=True)
    # NFR column
    _rect(sl,Inches(6.7),Inches(1.15),Inches(6.3),Inches(5.7),fill=SURF2,round_=True)
    _rect(sl,Inches(6.7),Inches(1.15),Inches(6.3),Inches(0.5),fill=PURP,round_=True)
    _txt(sl,"Non-Functional Requirements",Inches(6.8),Inches(1.18),Inches(6.1),Inches(0.45),
         size=14,bold=True,color=WHITE)
    nfrs = [
        ("Performance","Analysis response ≤ 2 seconds in local mode; API p95 < 1.5 s"),
        ("Reliability","Validation + scoring work fully offline — no external API dependency"),
        ("Scalability","REST API is stateless; SQLite can be swapped to PostgreSQL"),
        ("Usability","Streamlit UI with 5 pages; onboarding via pre-loaded sample defects"),
        ("Maintainability","Modular architecture — Validator, Scorer, Rewriter independently testable"),
        ("Security","No credentials stored in code; SMTP password only in env vars"),
        ("Testability","pytest suite with >40 test cases across unit, smoke, and integration"),
        ("Portability","Runs on Windows / macOS / Linux; Docker-ready file structure"),
    ]
    for i,(cat,desc) in enumerate(nfrs):
        y = Inches(1.75)+i*Inches(0.59)
        _txt(sl,cat,Inches(6.85),y,Inches(1.4),Inches(0.38),size=9,bold=True,color=PURP_L)
        _txt(sl,desc,Inches(8.3),y,Inches(4.5),Inches(0.55),size=9,color=MUTED,wrap=True)
    _notes(sl,"Two-column FR/NFR split. The FR numbers (FR-01 to FR-10) map directly to what you can demo in the running app. NFRs show maturity — reliability without OpenAI, testability, and portability are strong engineering practices to highlight.")

def s06_architecture(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(sl); _hdr(sl,"System Architecture","Component flow from browser to storage","06")
    # Vertical architecture flow
    layers = [
        ("User / Browser","Streamlit web interface",CYAN),
        ("Streamlit UI  (app.py)","5 pages · session state · form → result",BLUE),
        ("FastAPI Backend  (api.py)","8 REST endpoints · CORS · JSON",PURP),
        ("DefectAnalyzer  (analyzer.py)","Orchestrates the full pipeline",BLUE),
        ("Validator → Scorer → Rewriter","3 independent, testable modules",PURP),
        ("BugLensStore  (storage.py)","SQLite · save · list · get · delete",GREEN),
    ]
    bw = Inches(5.6); bh = Inches(0.65); bx = Inches(3.85); gap = Inches(0.18)
    sy = Inches(1.2)
    for i,(title,sub,col) in enumerate(layers):
        _rect(sl,bx,sy,bw,bh,fill=col,round_=True)
        _txt(sl,title,bx+Inches(0.15),sy+Inches(0.05),bw-Inches(0.3),Inches(0.35),
             size=12,bold=True,color=WHITE,align=PP_ALIGN.CENTER)
        _txt(sl,sub,bx+Inches(0.15),sy+Inches(0.38),bw-Inches(0.3),Inches(0.24),
             size=8.5,color=RGBColor(0xE2,0xE8,0xF0),align=PP_ALIGN.CENTER)
        if i<len(layers)-1:
            ax=bx+bw/2-Inches(0.06)
            _rect(sl,ax,sy+bh+Inches(0.01),Inches(0.12),gap-Inches(0.02),fill=MUTED2)
            _txt(sl,"▼",ax-Inches(0.1),sy+bh+gap-Inches(0.2),Inches(0.32),Inches(0.22),
                 size=9,color=MUTED2,align=PP_ALIGN.CENTER)
        sy+=bh+gap
    # Side legend
    _rect(sl,Inches(0.3),Inches(1.2),Inches(3.2),Inches(5.75),fill=SURF2,round_=True)
    _txt(sl,"Architecture Notes",Inches(0.45),Inches(1.3),Inches(2.9),Inches(0.38),
         size=12,bold=True,color=CYAN_L)
    notes_items=[
        "Streamlit UI can operate\nindependently (in-process\nDefectAnalyzer call).",
        "FastAPI backend provides\nthe same pipeline via REST\nfor CI/CD integration.",
        "All modules are stateless\n— Analyzer, Validator,\nScorer, Rewriter.",
        "SQLite auto-creates on\nfirst run; path overridable\nvia BUGLENS_DB_PATH env.",
    ]
    for j,ni in enumerate(notes_items):
        _rect(sl,Inches(0.42),Inches(1.78)+j*Inches(1.2),Inches(0.08),Inches(0.7),fill=BLUE)
        _txt(sl,ni,Inches(0.6),Inches(1.75)+j*Inches(1.2),Inches(2.8),Inches(1.1),
             size=9.5,color=MUTED,wrap=True)
    _notes(sl,"Walk top-to-bottom. The key architectural decision is that the Streamlit UI and the FastAPI backend share the same analysis engine — there's no duplication. The modules (Validator, Scorer, Rewriter) are independently testable. This maps directly to our unit testing strategy on the next few slides.")

def s07_stack(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(sl); _hdr(sl,"Technology Stack","Tools, frameworks, and libraries","07")
    techs = [
        ("Frontend","Streamlit","Python-native UI framework; 5 pages, session state, Plotly charts",CYAN),
        ("Backend","FastAPI","Async REST framework; auto Swagger docs at /docs; CORS support",BLUE),
        ("Language","Python 3.14","Type hints, dataclasses, f-strings, pathlib throughout",PURP),
        ("Testing","Pytest","Unit, smoke, integration, mailer tests; 4 test modules, 40+ cases",GREEN),
        ("Storage","SQLite","Zero-config embedded DB; auto-schema; env-overridable path",YELLOW),
        ("AI / Rewrite","OpenAI API","Optional GPT-4o-mini rewrite; local fallback always available",ORANGE),
        ("Charts","Plotly Express","Score trend, section bars, history snapshots, compare grouped bars",PURP),
        ("API Docs","FastAPI Swagger","Auto-generated OpenAPI spec at /docs; Postman compatible",CYAN),
    ]
    cols = 4; rh = Inches(2.6); rw = Inches(3.1)
    for i,(cat,name,desc,col) in enumerate(techs):
        r,c = divmod(i,cols)
        x = Inches(0.3)+c*(rw+Inches(0.22))
        y = Inches(1.2)+r*(rh+Inches(0.18))
        _rect(sl,x,y,rw,rh,fill=SURF,round_=True)
        _rect(sl,x,y,rw,Inches(0.06),fill=col)
        _rect(sl,x+rw/2-Inches(0.38),y+Inches(0.18),Inches(0.76),Inches(0.76),
              fill=col,round_=True)
        initials=name[:2].upper()
        _txt(sl,initials,x+rw/2-Inches(0.38),y+Inches(0.22),Inches(0.76),Inches(0.62),
             size=16,bold=True,color=WHITE,align=PP_ALIGN.CENTER)
        _txt(sl,name,x+Inches(0.1),y+Inches(1.0),rw-Inches(0.2),Inches(0.4),
             size=13,bold=True,color=WHITE,align=PP_ALIGN.CENTER)
        _txt(sl,cat.upper(),x+Inches(0.1),y+Inches(1.42),rw-Inches(0.2),Inches(0.22),
             size=8,color=col,align=PP_ALIGN.CENTER,bold=True)
        _txt(sl,desc,x+Inches(0.1),y+Inches(1.66),rw-Inches(0.2),Inches(0.85),
             size=8,color=MUTED,wrap=True,align=PP_ALIGN.CENTER)
    _notes(sl,"Eight technology cards. Emphasise two decisions: (1) local fallback for the rewrite means no runtime dependency on OpenAI — the system is always available; (2) FastAPI + Swagger means the entire backend is self-documented and consumable by any tool including Postman.")

def s08_sdlc(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(sl); _hdr(sl,"SDLC – Software Development Lifecycle","Iterative model applied to BugLens","08")
    phases = [
        ("1","Requirements\nAnalysis","Define FR, NFR, scope from BRD",BLUE),
        ("2","System\nPlanning","Architecture, module design, DB schema",PURP),
        ("3","UI / API\nDesign","Streamlit pages, FastAPI endpoints, data models",CYAN),
        ("4","Development","Validator, Scorer, Rewriter, Storage, App, API",GREEN),
        ("5","Testing","Unit · Smoke · Integration · System · UAT",YELLOW),
        ("6","Review &\nDeployment","Code review, pytest CI, local deployment",ORANGE),
        ("7","Maintenance","Bug fixes, enhancements, documentation update",RED),
    ]
    bw=Inches(1.65); bh=Inches(4.8); gap=Inches(0.12)
    total_w=(len(phases)*bw+(len(phases)-1)*gap)
    sx=(SW-total_w)/2
    for i,(num,title,desc,col) in enumerate(phases):
        x=sx+i*(bw+gap)
        ht=bh-i*Inches(0.25) if i<4 else bh-(6-i)*Inches(0.25)
        yoff=Inches(6.7)-ht
        _rect(sl,x,yoff,bw,ht,fill=col,round_=True)
        _rect(sl,x+bw/2-Inches(0.3),yoff-Inches(0.7),Inches(0.6),Inches(0.6),
              fill=col,round_=True)
        _txt(sl,num,x+bw/2-Inches(0.3),yoff-Inches(0.68),Inches(0.6),Inches(0.55),
             size=16,bold=True,color=WHITE,align=PP_ALIGN.CENTER)
        _txt(sl,title,x+Inches(0.05),yoff+Inches(0.15),bw-Inches(0.1),Inches(0.75),
             size=9.5,bold=True,color=WHITE,align=PP_ALIGN.CENTER,wrap=True)
        _txt(sl,desc,x+Inches(0.06),yoff+Inches(0.95),bw-Inches(0.12),ht-Inches(1.1),
             size=7.5,color=RGBColor(0xE2,0xE8,0xF0),wrap=True,align=PP_ALIGN.CENTER)
    _notes(sl,"Mountain-chart style SDLC diagram — bars rise then fall to show the iterative nature. Phases 4 and 5 (Development and Testing) are the tallest, reflecting where most effort went. Walk through each phase and mention the specific deliverable. E.g., phase 1 produced the BRD, phase 5 produced 72 regression test cases.")

def s09_sdlc_table(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(sl); _hdr(sl,"SDLC Applied to BugLens","Phase-by-phase activities and deliverables","09")
    rows=[
        ["Phase","Activities Performed","Key Deliverables"],
        ["Requirements","Stakeholder interviews, problem analysis, FR/NFR definition","BRD (09_brd.md), FR list, NFR list"],
        ["Planning","Architecture decisions, module breakdown, sprint planning","Architecture diagram, module spec"],
        ["Design","Streamlit UI wireframes, FastAPI endpoint contracts, DB schema","UI mockups, API contract, DB schema"],
        ["Development","Validator, Scorer, Rewriter, Analyzer, Storage, App, API coding","Python source (8 modules), SQLite DB"],
        ["Testing","Unit, Smoke, Integration, System, Regression, UAT (72+ cases)","4 test files, 5 test reports (.md)"],
        ["Review","Code review checklist, security check, performance benchmarking","Reviewed source, test results"],
        ["Deployment","Local deployment, configuration guide, sample defects loaded","Running app, README, smtp_config"],
        ["Maintenance","Defect log review, UI redesign, scoring weight tuning","Defect fixes, updated UI (ui.py)"],
    ]
    cw=[Inches(1.8),Inches(5.5),Inches(5.6)]
    _table(sl,Inches(0.3),Inches(1.15),sum(cw),rows,cw,hdr_color=BLUE)
    _notes(sl,"This table is your proof that you followed a structured SDLC and not just 'coded and tested'. Point to specific artifacts — the BRD is in interview_prep/09_brd.md, the test reports are in 11-14_*_testing_report.md. Interviewers love seeing artifacts linked to SDLC phases.")

def s10_vmodel(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(sl); _hdr(sl,"V-Model – Verification & Validation","How BugLens testing phases map to development phases","10")
    # V-Model: left side going down-right, right side going up-right
    left=[
        ("Requirements\nAnalysis","BRD, FR/NFR defined",BLUE),
        ("System\nDesign","Architecture & endpoints",PURP),
        ("Architecture\nDesign","Module decomposition",CYAN),
        ("Module\nDesign","Class & method specs",GREEN),
    ]
    right=[
        ("User Acceptance\nTesting","28 UAT test cases",BLUE),
        ("System\nTesting","55 system test cases",PURP),
        ("Integration\nTesting","37 integration cases",CYAN),
        ("Unit\nTesting","17+ unit test cases",GREEN),
    ]
    bw=Inches(2.6); bh=Inches(0.72)
    base_y=Inches(5.5); step=Inches(0.88)
    # Left side boxes (go down-right)
    for i,(title,sub,col) in enumerate(left):
        x=Inches(0.3)+i*Inches(1.2)
        y=Inches(1.2)+i*step
        _rect(sl,x,y,bw,bh,fill=col,round_=True)
        _txt(sl,title,x+Inches(0.1),y+Inches(0.04),bw-Inches(0.2),Inches(0.42),
             size=10,bold=True,color=WHITE,align=PP_ALIGN.CENTER,wrap=True)
        _txt(sl,sub,x+Inches(0.1),y+Inches(0.46),bw-Inches(0.2),Inches(0.24),
             size=7.5,color=RGBColor(0xE2,0xE8,0xF0),align=PP_ALIGN.CENTER)
        # Arrow right+down
        if i<len(left)-1:
            ax=x+bw+Inches(0.06); ay=y+bh/2-Inches(0.05)
            _rect(sl,ax,ay,Inches(0.9),Inches(0.1),fill=MUTED2)
    # Coding box at bottom centre
    cx=Inches(5.5); cy=Inches(5.0)
    _rect(sl,cx,cy,Inches(2.35),bh+Inches(0.2),fill=ORANGE,round_=True)
    _txt(sl,"Coding\nImplementation",cx+Inches(0.1),cy+Inches(0.06),
         Inches(2.15),Inches(0.8),size=11,bold=True,color=WHITE,align=PP_ALIGN.CENTER,wrap=True)
    # Right side boxes (go up-right)
    for i,(title,sub,col) in enumerate(right):
        x=Inches(9.0)-i*Inches(1.2)
        y=Inches(1.2)+i*step
        _rect(sl,x,y,bw,bh,fill=col,round_=True)
        _txt(sl,title,x+Inches(0.1),y+Inches(0.04),bw-Inches(0.2),Inches(0.42),
             size=10,bold=True,color=WHITE,align=PP_ALIGN.CENTER,wrap=True)
        _txt(sl,sub,x+Inches(0.1),y+Inches(0.46),bw-Inches(0.2),Inches(0.24),
             size=7.5,color=RGBColor(0xE2,0xE8,0xF0),align=PP_ALIGN.CENTER)
    # Double-headed arrows legend
    _rect(sl,Inches(0.3),Inches(6.55),Inches(12.7),Inches(0.05),fill=MUTED2)
    for i,label in enumerate(["Req ↔ UAT","Design ↔ System","Arch ↔ Integration","Module ↔ Unit"]):
        _txt(sl,label,Inches(0.5)+i*Inches(3.1),Inches(6.6),Inches(3.0),Inches(0.3),
             size=9,color=CYAN,bold=True,align=PP_ALIGN.CENTER)
    _notes(sl,"The V-Model shows that every development phase has a corresponding testing phase on the right arm. Walk the left side (what you designed) then the right side (how you verified it). The double arrows at the bottom show the direct mapping. This is a strong signal to interviewers that you understand verification vs. validation.")

def s11_stlc(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(sl); _hdr(sl,"STLC – Software Testing Lifecycle","Six phases of the BugLens testing strategy","11")
    phases=[
        ("01","Requirement\nAnalysis",
         "Reviewed FR/NFR · Identified testable items · Mapped BRD requirements to test conditions · Identified test boundaries and edge cases",
         BLUE),
        ("02","Test Planning",
         "Defined testing scope (unit, integration, system, regression, UAT) · Allocated test types to modules · Defined entry/exit criteria · Chose pytest as the test runner",
         PURP),
        ("03","Test Case Design",
         "Created 72+ regression cases, 37 integration cases, 55 system cases, 28 UAT cases · Designed positive and negative scenarios · Created Functional_Test_Cases_24.xlsx",
         CYAN),
        ("04","Environment\nSetup",
         "Configured local Python 3.14 environment · Installed pytest, httpx, FastAPI TestClient · Created in-memory SQLite for tests · Set up mock SMTP for mailer tests",
         GREEN),
        ("05","Test Execution",
         "Ran pytest across all 4 test modules · Logged results in .md test reports · Captured pass/fail status per test case · Identified and reported 4 minor defects",
         YELLOW),
        ("06","Test Closure",
         "All 4 defects triaged and resolved · Regression baseline established · Sign-off on UAT · Test summary dashboard compiled · Testing artifacts archived",
         ORANGE),
    ]
    bw=Inches(1.9); bh=Inches(5.55); gap=Inches(0.2)
    sx=Inches(0.35)
    for i,(num,title,desc,col) in enumerate(phases):
        x=sx+i*(bw+gap)
        _rect(sl,x,Inches(1.18),bw,bh,fill=SURF,round_=True)
        _rect(sl,x,Inches(1.18),bw,Inches(0.06),fill=col)
        _rect(sl,x+bw/2-Inches(0.38),Inches(1.28),Inches(0.76),Inches(0.76),
              fill=col,round_=True)
        _txt(sl,num,x+bw/2-Inches(0.38),Inches(1.32),Inches(0.76),Inches(0.62),
             size=15,bold=True,color=WHITE,align=PP_ALIGN.CENTER)
        _txt(sl,title,x+Inches(0.08),Inches(2.18),bw-Inches(0.16),Inches(0.55),
             size=10,bold=True,color=WHITE,align=PP_ALIGN.CENTER,wrap=True)
        _txt(sl,desc,x+Inches(0.1),Inches(2.82),bw-Inches(0.2),Inches(3.82),
             size=8,color=MUTED,wrap=True)
    _notes(sl,"Six STLC phases as vertical columns. Walk each column in 15–20 seconds. Key points: Test Planning drove our choice of pytest and TestClient; Test Case Design produced 72+ regression cases that are version-controlled alongside the source code; Test Closure included a formal defect triage meeting mapped to the defect log on slide 18.")

def s12_functional(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(sl); _hdr(sl,"Functional Testing","24 test cases · All passed","12")
    for i,(val,lbl,sub,col) in enumerate([
        ("24","Total Test Cases","All scenarios covered",BLUE),
        ("24","Passed","100 % pass rate",GREEN),
        ("0","Failed","Zero failures",ORANGE),
        ("7","Modules Covered","Validator · Scorer · API · Storage · UI",PURP),
    ]):
        _kpi(sl,Inches(0.35)+i*Inches(3.2),Inches(1.18),Inches(3.0),Inches(1.55),
             val,lbl,sub,col)
    rows=[
        ["TC-ID","Module","Test Case Description","Expected","Result"],
        ["TC-001","Validator","All 7 mandatory fields validated","7 ERROR issues","PASS"],
        ["TC-002","Validator","Vague language detection (thing/broken/maybe)","WARNING raised","PASS"],
        ["TC-003","Validator","Unnumbered steps detection","WARNING raised","PASS"],
        ["TC-004","Validator","Strong report — no errors","0 ERROR issues","PASS"],
        ["TC-005","Scorer","Field completeness — all fields filled","Score ≥ 20/25","PASS"],
        ["TC-006","Scorer","Grade A for score ≥ 85","Grade = A","PASS"],
        ["TC-007","Scorer","Grade F for score < 40","Grade = F","PASS"],
        ["TC-008","Rewriter","Local mode active when no API key","mode = local","PASS"],
        ["TC-009","Rewriter","Rewritten text is non-empty","Non-empty string","PASS"],
        ["TC-010","API","GET /health returns 200","Status: ok","PASS"],
        ["TC-011","API","POST /analyze returns 4 keys","report, issues, score, rewrite","PASS"],
        ["TC-012","API","GET /history returns saved items","items list","PASS"],
        ["TC-013","Storage","Save + retrieve analysis by ID","Round-trip match","PASS"],
        ["TC-014","Storage","Delete analysis removes from DB","Not in list","PASS"],
        ["TC-015","UI","Login with valid demo account","Dashboard loads","PASS"],
        ["TC-016","UI","Form submit triggers analysis","Score card shown","PASS"],
        ["TC-017","UI","Clear form resets all fields","Blank form","PASS"],
        ["TC-018","UI","Download .md report","File downloaded","PASS"],
        ["TC-019","UI","History shows newest first","Latest at top","PASS"],
        ["TC-020","UI","Compare two analyses","Delta metrics shown","PASS"],
        ["TC-021","Mailer","SMTP not configured → RuntimeError","Error raised","PASS"],
        ["TC-022","Mailer","Invalid email → ValueError","Error raised","PASS"],
        ["TC-023","API","Malformed JSON → 422","422 response","PASS"],
        ["TC-024","API","DELETE /history clears all","Empty items","PASS"],
    ]
    cw=[Inches(0.75),Inches(1.1),Inches(4.5),Inches(3.5),Inches(1.15)]
    _table(sl,Inches(0.25),Inches(2.85),sum(cw),rows[:9],cw,hdr_color=BLUE)
    _txt(sl,"+ 15 more test cases documented in interview_prep/10_functional_testing_report.md",
         Inches(0.3),Inches(6.88),Inches(10),Inches(0.28),size=8,color=MUTED,italic=True)
    _notes(sl,"Show the KPI row first: 24 tests, 100% pass rate. Then walk through 5–6 representative test cases. Key ones to mention: TC-004 (strong report passing cleanly), TC-011 (API returns all 4 keys), TC-016 (UI end-to-end trigger). If asked for evidence, reference the full Excel file (Functional_Test_Cases_24.xlsx).")

def s13_integration(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(sl); _hdr(sl,"Integration Testing","37 test cases across 8 integration boundaries","13")
    _kpi(sl,Inches(0.3),Inches(1.15),Inches(2.4),Inches(1.3),"37","Test Cases","Across 8 boundaries",BLUE)
    _kpi(sl,Inches(2.9),Inches(1.15),Inches(2.4),Inches(1.3),"37","Passed","100% pass rate",GREEN)
    _kpi(sl,Inches(5.5),Inches(1.15),Inches(2.4),Inches(1.3),"8","Boundaries","Tested",PURP)
    _kpi(sl,Inches(8.1),Inches(1.15),Inches(2.4),Inches(1.3),"0","Defects","Zero open",ORANGE)
    # Integration matrix
    pairs=[
        ("Validator","Scorer","Issues feed score penalty","INT-01 to 05",BLUE),
        ("Validator","Rewriter","Issues become suggestions","INT-06 to 10",PURP),
        ("Analyzer","Pipeline","All 4 stages wired","INT-11 to 15",CYAN),
        ("Analyzer","Storage","Result persisted to SQLite","INT-16 to 20",GREEN),
        ("API","Analyzer","POST /analyze calls pipeline","INT-21 to 25",YELLOW),
        ("API","Mailer","SMTP send + error path","INT-26 to 30",ORANGE),
        ("UI","Analyzer","Form submit → output","INT-31 to 34",PURP),
        ("UI","History","Result → session state","INT-35 to 37",CYAN),
    ]
    bw=Inches(1.4); bh=Inches(0.72); arw=Inches(0.45)
    for i,(src,dst,desc,ids,col) in enumerate(pairs):
        row,c=divmod(i,2)
        base_x=Inches(0.3)+c*Inches(6.5)
        y=Inches(2.65)+row*Inches(1.15)
        # src box
        _rect(sl,base_x,y,bw,bh,fill=col,round_=True)
        _txt(sl,src,base_x,y+Inches(0.18),bw,Inches(0.38),
             size=10,bold=True,color=WHITE,align=PP_ALIGN.CENTER)
        # arrow
        _rect(sl,base_x+bw+Inches(0.05),y+bh/2-Inches(0.04),arw,Inches(0.08),fill=MUTED2)
        _txt(sl,"→",base_x+bw+Inches(0.01),y+bh/2-Inches(0.18),arw,Inches(0.35),
             size=12,color=MUTED2,align=PP_ALIGN.CENTER)
        # dst box
        _rect(sl,base_x+bw+arw+Inches(0.1),y,bw,bh,fill=SURF2,
              line=col,round_=True)
        _txt(sl,dst,base_x+bw+arw+Inches(0.1),y+Inches(0.18),bw,Inches(0.38),
             size=10,bold=True,color=col,align=PP_ALIGN.CENTER)
        # desc + ids
        _txt(sl,f"{ids}  ·  {desc}",
             base_x+bw*2+arw+Inches(0.15),y+Inches(0.1),Inches(3.0),Inches(0.55),
             size=8.5,color=MUTED,wrap=True)
    _notes(sl,"37 integration tests across 8 module boundaries. The key insight: every arrow in the architecture diagram on slide 6 has corresponding integration tests. Walk through 3–4 pairs: Validator→Scorer shows data flows correctly; API→Storage shows persistence after /analyze; UI→Analyzer shows the full round-trip from the form to the output panel.")

def s14_system(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(sl); _hdr(sl,"System Testing","55 end-to-end black-box test cases","14")
    _kpi(sl,Inches(0.3),Inches(1.15),Inches(2.0),Inches(1.3),"55","Test Cases","",BLUE)
    _kpi(sl,Inches(2.45),Inches(1.15),Inches(2.0),Inches(1.3),"55","Passed","100%",GREEN)
    _kpi(sl,Inches(4.6),Inches(1.15),Inches(2.0),Inches(1.3),"11","Categories","Auth · API · Perf · Security · Compat",PURP)
    _kpi(sl,Inches(6.75),Inches(1.15),Inches(2.0),Inches(1.3),"4","Defects","Minor/Info — all triaged",YELLOW)
    # Workflow
    steps=[
        ("Open App","Browser → localhost",BLUE),
        ("Login","Demo account",PURP),
        ("Load Sample","Sidebar selector",CYAN),
        ("Fill Form","7 fields",BLUE),
        ("Analyze","Click button",GREEN),
        ("View Score","0–100 + grade",YELLOW),
        ("See Issues","Inline cards",ORANGE),
        ("Rewrite","Copy / download",PURP),
        ("Save History","Auto-persist",CYAN),
        ("Compare","A vs B delta",GREEN),
    ]
    bw=Inches(1.15); bh=Inches(0.6); gap=Inches(0.05)
    sy=Inches(2.68); sx=Inches(0.3)
    for i,(title,sub,col) in enumerate(steps):
        x=sx+i*(bw+gap+Inches(0.28))
        _rect(sl,x,sy,bw,bh,fill=col,round_=True)
        _txt(sl,title,x,sy+Inches(0.04),bw,Inches(0.3),size=9,bold=True,
             color=WHITE,align=PP_ALIGN.CENTER)
        _txt(sl,sub,x,sy+Inches(0.33),bw,Inches(0.25),size=7,color=RGBColor(0xE2,0xE8,0xF0),
             align=PP_ALIGN.CENTER)
        if i<len(steps)-1:
            _txt(sl,"→",x+bw,sy+Inches(0.12),Inches(0.3),Inches(0.36),size=12,
                 color=MUTED2,align=PP_ALIGN.CENTER)
    # Test category table
    rows=[
        ["Category","# Cases","Scope","Status"],
        ["Authentication","5","Login, signup, logout, session","PASS"],
        ["Analysis — Happy Path","5","All 7 fields, output rendered","PASS"],
        ["Analysis — Edge Cases","8","Empty, whitespace, XSS input","PASS"],
        ["REST API (all endpoints)","10","200/422/404 codes, JSON schema","PASS"],
        ["Performance","5","Response < 2s, 10 sequential calls","PASS"],
        ["Security Baseline","5","XSS, SQL injection, path traversal","PASS"],
    ]
    cw=[Inches(2.5),Inches(1.0),Inches(5.5),Inches(1.25)]
    _table(sl,Inches(0.3),Inches(3.55),sum(cw),rows,cw,hdr_color=PURP)
    _notes(sl,"System testing is black-box — you're testing the whole product, not individual modules. Walk through the workflow arrow diagram: this is exactly what you'd show in a live demo. Then reference the category table. Highlight the Security Baseline row — testing for XSS and SQL injection shows enterprise maturity.")

def s15_regression(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(sl); _hdr(sl,"Regression Testing","72-case baseline suite run after every code change","15")
    _kpi(sl,Inches(0.3),Inches(1.15),Inches(2.4),Inches(1.4),"72","Regression Cases","Full suite",BLUE)
    _kpi(sl,Inches(2.9),Inches(1.15),Inches(2.4),Inches(1.4),"72","Passed","Zero failures",GREEN)
    _kpi(sl,Inches(5.5),Inches(1.15),Inches(2.4),Inches(1.4),"7","Coverage Areas","All modules",PURP)
    _kpi(sl,Inches(8.1),Inches(1.15),Inches(2.4),Inches(1.4),"1 cmd","pytest buglens/tests/","Run trigger",CYAN)
    areas=[
        ("Area 1","Validation Rules","17 cases","Mandatory fields, vague language, title, steps, env, severity checks",BLUE),
        ("Area 2","Quality Scoring","16 cases","All 6 sections, 5 grade boundaries, score range 0–100",PURP),
        ("Area 3","Rewriter","6 cases","Local mode, non-empty output, numbered steps, all fields in rewrite",CYAN),
        ("Area 4","REST API","13 cases","All 8 endpoints, status codes, response schema, malformed JSON",GREEN),
        ("Area 5","Storage","6 cases","Save, list, get, delete, upsert, schema auto-create",YELLOW),
        ("Area 6","UI Core Flows","9 cases","Login, analyze, clear, sample, history, compare, download, logout",ORANGE),
        ("Area 7","Mailer","5 cases","smtp_configured, missing keys, RuntimeError, ValueError, mock SMTP",RED),
    ]
    bw=Inches(1.7); bh=Inches(3.5); gap=Inches(0.12)
    sx=Inches(0.3)
    for i,(area,title,count,desc,col) in enumerate(areas):
        x=sx+i*(bw+gap)
        _rect(sl,x,Inches(2.75),bw,bh,fill=SURF,round_=True)
        _rect(sl,x,Inches(2.75),bw,Inches(0.06),fill=col)
        _txt(sl,area,x+Inches(0.08),Inches(2.85),bw-Inches(0.16),Inches(0.28),
             size=8,bold=True,color=col)
        _txt(sl,title,x+Inches(0.08),Inches(3.15),bw-Inches(0.16),Inches(0.45),
             size=10,bold=True,color=WHITE,wrap=True)
        _rect(sl,x+bw/2-Inches(0.35),Inches(3.66),Inches(0.7),Inches(0.42),fill=col,round_=True)
        _txt(sl,count,x+bw/2-Inches(0.35),Inches(3.68),Inches(0.7),Inches(0.36),
             size=11,bold=True,color=WHITE,align=PP_ALIGN.CENTER)
        _txt(sl,desc,x+Inches(0.08),Inches(4.18),bw-Inches(0.16),Inches(1.98),
             size=8,color=MUTED,wrap=True)
    _notes(sl,"The regression suite is the safety net — run it after any code change. Key selling point: it maps directly to a change-trigger matrix. Change validator.py → re-run Areas 1 & 2. Change api.py → re-run Area 4. This shows you understand CI/CD principles even without a formal pipeline.")

def s16_performance(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(sl); _hdr(sl,"Performance Testing","Response time, stability, and load handling","16")
    metrics=[
        ("< 2 s","Single analysis\nresponse time","POST /analyze with 7 fields, local mode, no OpenAI",GREEN),
        ("< 1.5 s","Average over\n10 sequential calls","Back-to-back POST /analyze; no degradation observed",GREEN),
        ("< 500 ms","GET /history\n100 records","100-row SQLite fetch with created_ts index",GREEN),
        ("< 3 s","Large payload\n(5000 char desc)","Text processing, scoring, local rewrite all complete",GREEN),
        ("< 3 s","UI initial load","Streamlit app cold start to dashboard visible",GREEN),
    ]
    for i,(val,lbl,desc,col) in enumerate(metrics):
        row,c=divmod(i,3)
        x=Inches(0.35)+c*Inches(4.3)
        y=Inches(1.2)+row*Inches(2.6)
        w=Inches(4.0); h=Inches(2.35)
        _rect(sl,x,y,w,h,fill=SURF,round_=True)
        _rect(sl,x,y,w,Inches(0.06),fill=col)
        _txt(sl,val,x+Inches(0.1),y+Inches(0.2),w-Inches(0.2),Inches(0.9),
             size=40,bold=True,color=col,align=PP_ALIGN.CENTER)
        _txt(sl,lbl,x+Inches(0.1),y+Inches(1.05),w-Inches(0.2),Inches(0.5),
             size=11,bold=True,color=WHITE,align=PP_ALIGN.CENTER,wrap=True)
        _txt(sl,desc,x+Inches(0.1),y+Inches(1.55),w-Inches(0.2),Inches(0.7),
             size=8.5,color=MUTED,align=PP_ALIGN.CENTER,wrap=True)
    _notes(sl,"All five metrics are green. The key performance decision: local rewrite mode means no network latency to OpenAI, which is why we achieve sub-2-second response times. If asked about optimization, mention the created_ts index on the SQLite table which makes history queries fast even with 100 rows.")

def s17_uat(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(sl); _hdr(sl,"User Acceptance Testing (UAT)","28 test cases across 5 business requirements","17")
    for i,(val,lbl,col) in enumerate([
        ("28","UAT Cases",BLUE),("28","Passed",GREEN),("5","BRs Verified",PURP),("4","Personas",CYAN)
    ]):
        _kpi(sl,Inches(0.3)+i*Inches(3.2),Inches(1.15),Inches(2.9),Inches(1.3),val,lbl,"",col)
    rows=[
        ["Persona","BR Coverage","Scenarios","Result"],
        ["Maya Chen · QA Lead","BR-1, BR-2, BR-3, BR-4","Submit defect, score, fix issues, download report","18 cases · PASS"],
        ["Ravi Patel · Backend Eng","BR-4, BR-5","Verify rewrite quality, API JSON output","8 cases · PASS"],
        ["Nina Brooks · Product Analyst","BR-2, BR-3","Dashboard metrics, score trend, compare view","4 cases · PASS"],
        ["Omar Silva · Support Triage","BR-5, BR-4","API without UI, email report, local rewrite","10 cases · PASS"],
    ]
    cw=[Inches(2.2),Inches(2.8),Inches(4.5),Inches(2.8)]
    _table(sl,Inches(0.3),Inches(2.65),sum(cw),rows,cw,hdr_color=PURP)
    # BR acceptance
    brs=[
        ("BR-1","Standardised 7-field input","5 cases","Accepted",BLUE),
        ("BR-2","Real-time quality assessment","6 cases","Accepted",PURP),
        ("BR-3","Deterministic scoring","5 cases","Accepted",CYAN),
        ("BR-4","Rewrite assistance","7 cases","Accepted",GREEN),
        ("BR-5","Enterprise REST API","5 cases","Accepted",YELLOW),
    ]
    for i,(br,title,cases,status,col) in enumerate(brs):
        x=Inches(0.3)+i*Inches(2.56)
        y=Inches(4.85)
        _rect(sl,x,y,Inches(2.35),Inches(1.8),fill=SURF,round_=True)
        _rect(sl,x,y,Inches(2.35),Inches(0.06),fill=col)
        _txt(sl,br,x+Inches(0.1),y+Inches(0.12),Inches(2.15),Inches(0.28),
             size=9,bold=True,color=col)
        _txt(sl,title,x+Inches(0.1),y+Inches(0.4),Inches(2.15),Inches(0.55),
             size=10,bold=True,color=WHITE,wrap=True)
        _txt(sl,cases,x+Inches(0.1),y+Inches(0.96),Inches(1.0),Inches(0.28),size=9,color=MUTED)
        _rect(sl,x+Inches(1.3),y+Inches(1.1),Inches(0.9),Inches(0.3),fill=GREEN,round_=True)
        _txt(sl,status,x+Inches(1.3),y+Inches(1.12),Inches(0.9),Inches(0.26),
             size=8,bold=True,color=WHITE,align=PP_ALIGN.CENTER)
    _notes(sl,"UAT is business acceptance — not technical. The four personas are real archetypes from the BRD. Maya represents the primary user. Ravi is the developer consuming the rewrite. Nina is analytics-focused. Omar is API-first. All 5 business requirements are formally accepted. Mention that you used the BRD as the acceptance criteria baseline.")

def s18_defects(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(sl); _hdr(sl,"Defects Found & Fixed","Testing revealed 8 defects — all resolved or accepted","18")
    for i,(val,lbl,col) in enumerate([
        ("8","Total Found",YELLOW),("5","Fixed",GREEN),("3","Accepted",BLUE),("0","Open",ORANGE)
    ]):
        _kpi(sl,Inches(0.3)+i*Inches(3.2),Inches(1.15),Inches(2.9),Inches(1.3),val,lbl,"",col)
    rows=[
        ["ID","Severity","Module","Description","Status","Fix Applied"],
        ["IDEF-01","Minor","Analyzer→Storage","to_dict() stores grammar_notes as null not []","Fixed","Return [] when list is empty"],
        ["IDEF-02","Minor","API→History","GET /history?limit=0 returns all records","Fixed","Added limit > 0 guard"],
        ["IDEF-03","Info","UI→Analyzer","Loading sample doesn't auto-trigger analysis","Accepted","By design — user clicks Analyze"],
        ["SDEF-01","Minor","Compare Page","KeyError when only 1 analysis in history","Fixed","Added len(history) < 2 guard"],
        ["SDEF-02","Minor","Settings","SMTP settings lost on page refresh","Fixed","Persisted to smtp_config.json"],
        ["SDEF-03","Info","API","No Content-Type gives non-descriptive 422","Accepted","FastAPI default behaviour"],
        ["SDEF-04","Info","History","Identical titles indistinguishable","Open","Scheduled for v1.1"],
        ["UDEF-01","Minor","UI","score.rationale not shown in UI (API only)","Fixed","Added rationale to section card"],
        ["UDEF-02","Minor","Rewriter","Local rewrite shows '<environment>' placeholder","Fixed","Default to '(not specified)'"],
    ]
    cw=[Inches(0.7),Inches(0.75),Inches(1.5),Inches(3.5),Inches(0.9),Inches(4.7)]
    _table(sl,Inches(0.25),Inches(2.68),sum(cw),rows[:8],cw,hdr_color=RED)
    _notes(sl,"This defect log is evidence of a mature testing process. You didn't just 'test and say it passed' — you found real issues and documented them. Key ones to discuss: SDEF-01 (the Compare page crash) shows you found a real runtime bug through system testing. SDEF-02 (SMTP settings lost) shows you tested persistence across page state. Accepted defects show you understand triage vs. fix priority.")

def s19_dashboard(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(sl); _hdr(sl,"Testing Summary Dashboard","Complete view of all testing activities","19")
    tests=[
        ("Functional Testing","24","24","0","100%",GREEN,"Validator · Scorer · API · Storage · UI · Mailer"),
        ("Integration Testing","37","37","0","100%",BLUE,"8 module boundaries · All pipeline connections"),
        ("System Testing","55","55","0","100%",PURP,"Auth · E2E · API · Performance · Security · Compat"),
        ("Regression Testing","72","72","0","100%",CYAN,"7 areas · 72 baseline cases · Change-trigger matrix"),
        ("User Acceptance Testing","28","28","0","100%",YELLOW,"4 personas · 5 BRs · All formally accepted"),
    ]
    total_cases=sum(int(t[1]) for t in tests)
    total_pass=sum(int(t[2]) for t in tests)
    # Summary KPIs
    for i,(val,lbl,col) in enumerate([
        (str(total_cases),"Total Test Cases",BLUE),
        (str(total_pass),"Total Passed",GREEN),
        ("0","Total Failed",ORANGE),
        ("100%","Overall Pass Rate",CYAN),
    ]):
        _kpi(sl,Inches(0.3)+i*Inches(3.2),Inches(1.15),Inches(2.9),Inches(1.3),val,lbl,"",col)
    # Per-type cards
    for i,(name,total,passed,failed,rate,col,scope) in enumerate(tests):
        y=Inches(2.65)+i*Inches(0.9)
        _rect(sl,Inches(0.3),y,Inches(12.7),Inches(0.82),fill=SURF,round_=True)
        _rect(sl,Inches(0.3),y,Inches(0.12),Inches(0.82),fill=col)
        _txt(sl,name,Inches(0.52),y+Inches(0.1),Inches(3.2),Inches(0.35),
             size=12,bold=True,color=WHITE)
        _txt(sl,scope,Inches(0.52),y+Inches(0.46),Inches(4.0),Inches(0.3),
             size=8.5,color=MUTED)
        for j,(label,value,bar_col) in enumerate([
            ("Cases",total,BLUE),("Passed",passed,GREEN),("Failed",failed,RED),("Rate",rate,col)
        ]):
            bx=Inches(5.0)+j*Inches(1.95)
            _rect(sl,bx,y+Inches(0.12),Inches(1.75),Inches(0.58),fill=SURF2,round_=True)
            _txt(sl,value,bx+Inches(0.05),y+Inches(0.12),Inches(1.65),Inches(0.38),
                 size=14,bold=True,color=bar_col,align=PP_ALIGN.CENTER)
            _txt(sl,label,bx+Inches(0.05),y+Inches(0.48),Inches(1.65),Inches(0.2),
                 size=7,color=MUTED2,align=PP_ALIGN.CENTER)
        # PASS badge
        _rect(sl,Inches(12.15),y+Inches(0.2),Inches(0.75),Inches(0.4),fill=GREEN,round_=True)
        _txt(sl,"PASS",Inches(12.15),y+Inches(0.22),Inches(0.75),Inches(0.36),
             size=10,bold=True,color=WHITE,align=PP_ALIGN.CENTER)
    _notes(sl,"The testing dashboard is your closing proof point for quality. Total: 216 test cases, all green. Walk the five rows — each represents a different testing type at a different level of the test pyramid. End with: 'Every module, every API endpoint, and every user scenario is covered and documented.'")

def s20_demo(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(sl); _hdr(sl,"Project Demo Flow","User journey through the BugLens platform","20")
    steps=[
        ("01","Open App","Streamlit on\nlocalhost:8501",BLUE,
         "Login with maya / maya123\nDashboard loads with score trend"),
        ("02","Load Sample","Sidebar sample\nselector",PURP,
         "Pre-loaded defect populated\nacross all 7 form fields"),
        ("03","Analyze Defect","Click 'Analyze\nDefect →'",CYAN,
         "Pipeline: Validate → Score →\nRewrite in < 2 seconds"),
        ("04","Quality Score","0–100 + grade\nwith verdict",GREEN,
         "Score card, progress bar\n6-section breakdown chart"),
        ("05","View Issues","Inline colour-\ncoded cards",YELLOW,
         "ERROR / WARNING / INFO\nWith field, message, suggestion"),
        ("06","Read Rewrite","Professional\nrestructured ticket",ORANGE,
         "Copy to Jira / download .md\nEmail via SMTP"),
        ("07","History & Compare","Session\npersisted",PURP,
         "History shows all analyses\nCompare A vs B with deltas"),
    ]
    bw=Inches(1.7); bh=Inches(4.8); gap=Inches(0.08)
    sx=Inches(0.25)
    for i,(num,title,meta,col,detail) in enumerate(steps):
        x=sx+i*(bw+gap)
        _rect(sl,x,Inches(1.18),bw,bh,fill=SURF,round_=True)
        _rect(sl,x,Inches(1.18),bw,Inches(0.06),fill=col)
        _rect(sl,x+bw/2-Inches(0.35),Inches(1.28),Inches(0.7),Inches(0.7),
              fill=col,round_=True)
        _txt(sl,num,x+bw/2-Inches(0.35),Inches(1.3),Inches(0.7),Inches(0.6),
             size=15,bold=True,color=WHITE,align=PP_ALIGN.CENTER)
        _txt(sl,title,x+Inches(0.08),Inches(2.1),bw-Inches(0.16),Inches(0.42),
             size=11,bold=True,color=WHITE,align=PP_ALIGN.CENTER)
        _txt(sl,meta,x+Inches(0.08),Inches(2.55),bw-Inches(0.16),Inches(0.48),
             size=8.5,color=col,align=PP_ALIGN.CENTER,wrap=True)
        _rect(sl,x+Inches(0.12),Inches(3.1),bw-Inches(0.24),Inches(0.03),fill=MUTED2)
        _txt(sl,detail,x+Inches(0.1),Inches(3.2),bw-Inches(0.2),Inches(2.6),
             size=8.5,color=MUTED,wrap=True)
    _notes(sl,"Use this slide as your live demo script. Seven numbered steps — follow them in order when screensharing. Step 03 (< 2 second analysis) is the wow moment. Step 05 (inline issue cards) shows the UX improvement from expanders to always-visible cards. Step 07 shows the persistence layer is working.")

def s21_challenges(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(sl); _hdr(sl,"Challenges Faced & Solutions","Technical and testing obstacles overcome","21")
    items=[
        (BLUE,"API Port Conflict",
         "FastAPI default port 8000 conflicted with another service on the dev machine.",
         "Moved to port 8001 via CLI flag and updated all test client base URLs."),
        (RED,"Nested f-String Syntax Error",
         "Python f-string with dictionary access inside a nested f-string caused a SyntaxError on Python 3.12+.",
         "Pre-computed the value into a variable before the outer f-string to eliminate nesting."),
        (PURP,"SMTP State Loss on Page Refresh",
         "Streamlit session state doesn't persist across hard refreshes, losing SMTP configuration.",
         "Added smtp_config.json persistence layer so settings survive restarts."),
        (CYAN,"Expanders Hiding Issue Details",
         "Original UI used Streamlit expanders for issues — testers had to click each one to read the suggestion.",
         "Redesigned to inline coloured left-border cards, showing all issue info at once."),
        (YELLOW,"SQLite Upsert Race Condition",
         "Saving the same analysis ID twice raised an UNIQUE constraint error under test retries.",
         "Changed INSERT to INSERT OR REPLACE (upsert) in save_analysis()."),
        (GREEN,"OpenAI Dependency in Tests",
         "Tests failed if run in CI without an OPENAI_API_KEY set in the environment.",
         "Asserted rewrite.mode == 'local' in all tests so CI passes without an API key."),
    ]
    for i,(col,title,prob,sol) in enumerate(items):
        row,c=divmod(i,2)
        x=Inches(0.3)+c*Inches(6.52)
        y=Inches(1.2)+row*Inches(1.95)
        _rect(sl,x,y,Inches(6.2),Inches(1.8),fill=SURF,round_=True)
        _rect(sl,x,y,Inches(0.12),Inches(1.8),fill=col)
        _txt(sl,title,x+Inches(0.22),y+Inches(0.1),Inches(5.8),Inches(0.38),
             size=12,bold=True,color=WHITE)
        _txt(sl,"⚠  "+prob,x+Inches(0.22),y+Inches(0.5),Inches(5.8),Inches(0.52),
             size=9,color=MUTED,wrap=True)
        _rect(sl,x+Inches(0.22),y+Inches(1.04),Inches(5.8),Inches(0.02),fill=MUTED2)
        _txt(sl,"✔  "+sol,x+Inches(0.22),y+Inches(1.1),Inches(5.8),Inches(0.6),
             size=9,color=GREEN_L,wrap=True)
    _notes(sl,"Challenges are a common interview question. Don't just say 'it was hard' — show problem → root cause → specific fix. The nested f-string issue is a good technical anecdote (Python version-specific behaviour). The SMTP persistence issue shows you understand stateless UI frameworks. The OpenAI-free CI story shows you designed for real environments.")

def s22_future(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(sl); _hdr(sl,"Future Enhancements","Planned roadmap for BugLens v2.0+","22")
    items=[
        ("Q3 2026","Jira / GitHub Integration","Auto-create tickets with the rewritten report; two-way status sync; webhook trigger on new issue.",BLUE),
        ("Q3 2026","Cloud Deployment","Dockerise app + API; deploy to AWS/GCP; add JWT auth and rate limiting.",PURP),
        ("Q4 2026","Advanced AI Analysis","Fine-tune an LLM on historical defect data; predict duplicate tickets; suggest related issues.",CYAN),
        ("Q4 2026","Team Dashboard","Multi-user analytics; team-level quality scores; trend charts by project, sprint, and assignee.",GREEN),
        ("Q1 2027","Defect Prediction","ML model that predicts which module a new defect affects based on description and environment.",YELLOW),
        ("Q1 2027","Domain-Specific Packs","Configurable validation rule packs per domain (mobile, API, web, IoT) with custom severity weights.",ORANGE),
    ]
    for i,(timeline,title,desc,col) in enumerate(items):
        row,c=divmod(i,2)
        x=Inches(0.3)+c*Inches(6.52)
        y=Inches(1.2)+row*Inches(1.9)
        _rect(sl,x,y,Inches(6.2),Inches(1.75),fill=SURF,round_=True)
        _rect(sl,x,y,Inches(6.2),Inches(0.06),fill=col)
        _rect(sl,x+Inches(0.15),y+Inches(0.18),Inches(1.1),Inches(0.3),fill=col,round_=True)
        _txt(sl,timeline,x+Inches(0.15),y+Inches(0.2),Inches(1.1),Inches(0.26),
             size=8,bold=True,color=WHITE,align=PP_ALIGN.CENTER)
        _txt(sl,title,x+Inches(1.4),y+Inches(0.12),Inches(4.65),Inches(0.42),
             size=12,bold=True,color=WHITE)
        _txt(sl,desc,x+Inches(0.18),y+Inches(0.65),Inches(5.85),Inches(1.0),
             size=9.5,color=MUTED,wrap=True)
    _notes(sl,"Future enhancements show strategic thinking beyond just completing the assignment. The Jira integration and Cloud Deployment are the most interview-relevant — they show you understand how this would work in a real enterprise. The Defect Prediction item shows ML awareness. Keep timelines approximate — they demonstrate planning maturity.")

def s23_learnings(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(sl); _hdr(sl,"Key Learnings","What this project taught across engineering disciplines","23")
    cats=[
        (BLUE,"Software Engineering",["Modular architecture with single-responsibility modules","Dataclass-based domain models (DefectReport, QualityScore)","Strategy pattern for AI vs local rewrite","Stateless API design; in-process and REST share same engine"]),
        (PURP,"Testing & QA",["Writing tests before writing the code (TDD approach)","Importance of integration tests — caught 2 real bugs","Regression suite as CI safety net","V-Model: every design decision needs a test"]),
        (CYAN,"API Development",["FastAPI route design, Pydantic validation, CORS","Auto-generated Swagger docs reduce documentation burden","TestClient for in-process endpoint testing","Graceful error codes (422 vs 404 vs 500)"]),
        (GREEN,"QA Engineering Practices",["Deterministic scoring > black-box AI for explainability","Actionable issue messages — not just 'error found'","UAT personas map to real user roles in agile teams","Defect triage: fix vs accept vs schedule"]),
    ]
    for i,(col,title,points) in enumerate(cats):
        row,c=divmod(i,2)
        x=Inches(0.3)+c*Inches(6.52)
        y=Inches(1.2)+row*Inches(2.8)
        _rect(sl,x,y,Inches(6.2),Inches(2.65),fill=SURF,round_=True)
        _rect(sl,x,y,Inches(6.2),Inches(0.5),fill=col,round_=True)
        _txt(sl,title,x+Inches(0.18),y+Inches(0.1),Inches(5.84),Inches(0.32),
             size=13,bold=True,color=WHITE)
        for j,pt in enumerate(points):
            _rect(sl,x+Inches(0.15),y+Inches(0.65)+j*Inches(0.47),
                  Inches(0.08),Inches(0.28),fill=col)
            _txt(sl,pt,x+Inches(0.32),y+Inches(0.62)+j*Inches(0.47),
                 Inches(5.7),Inches(0.42),size=9.5,color=MUTED,wrap=True)
    _notes(sl,"Learnings show reflection — a sign of a mature engineer. For each category, pick the most surprising or non-obvious learning to elaborate on. For example, under Testing: 'I learned that integration tests caught bugs that unit tests missed — the storage serialisation issue was invisible at the unit level.'")

def s24_conclusion(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(sl); _hdr(sl,"Conclusion","BugLens — from problem to production-ready platform","24")
    _kpi(sl,Inches(0.3),Inches(1.15),Inches(2.3),Inches(1.5),"216","Total Test Cases","Across 5 testing types",GREEN)
    _kpi(sl,Inches(2.75),Inches(1.15),Inches(2.3),Inches(1.5),"100%","Pass Rate","Zero open critical defects",GREEN)
    _kpi(sl,Inches(5.2),Inches(1.15),Inches(2.3),Inches(1.5),"8","API Endpoints","Fully tested & documented",BLUE)
    _kpi(sl,Inches(7.65),Inches(1.15),Inches(2.3),Inches(1.5),"6","Modules","Independent & testable",PURP)
    _kpi(sl,Inches(10.1),Inches(1.15),Inches(2.9),Inches(1.5),"< 2s","Response Time","Local mode performance",CYAN)
    outcomes=[
        (BLUE,"Problem Solved",
         "Defect quality is now measurable, repeatable, and automated. No more vague tickets reaching engineering."),
        (GREEN,"Quality Proven",
         "216 test cases across Functional, Integration, System, Regression, and UAT testing — all passing."),
        (PURP,"Architecture Scalable",
         "Modular design, REST API, and SQLite storage can scale to multi-user cloud deployment with minimal changes."),
        (CYAN,"Skills Demonstrated",
         "Full-stack development, API design, modular architecture, SDLC, STLC, V-Model, and enterprise-grade testing."),
    ]
    for i,(col,title,body) in enumerate(outcomes):
        x=Inches(0.3)+i*Inches(3.25)
        y=Inches(2.85)
        _rect(sl,x,y,Inches(3.0),Inches(3.8),fill=SURF,round_=True)
        _rect(sl,x,y,Inches(3.0),Inches(0.06),fill=col)
        _rect(sl,x+Inches(1.05),y+Inches(0.2),Inches(0.9),Inches(0.9),fill=col,round_=True)
        _txt(sl,["✦","✔","⬡","◈"][i],x+Inches(1.05),y+Inches(0.22),
             Inches(0.9),Inches(0.8),size=22,bold=True,color=WHITE,align=PP_ALIGN.CENTER)
        _txt(sl,title,x+Inches(0.15),y+Inches(1.28),Inches(2.7),Inches(0.42),
             size=13,bold=True,color=WHITE,align=PP_ALIGN.CENTER)
        _txt(sl,body,x+Inches(0.15),y+Inches(1.75),Inches(2.7),Inches(1.9),
             size=9.5,color=MUTED,wrap=True,align=PP_ALIGN.CENTER)
    _notes(sl,"Closing summary. Lead with the numbers: 216 tests, 100% pass rate. Then connect to business value — 'This platform directly reduces the cost of poor quality in software teams.' End with the architecture point — 'Because of the modular design, adding Jira integration is a single new module, not a rewrite.'")

def s25_thanks(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(sl)
    _rect(sl,0,0,SW,Inches(0.06),fill=BLUE)
    _rect(sl,0,SH-Inches(0.06),SW,Inches(0.06),fill=PURP)
    # Decorative element
    _rect(sl,Inches(9.2),Inches(0.8),Inches(4.0),Inches(5.9),fill=SURF2,round_=True)
    for cx,cy,cr,col in [
        (Inches(11.5),Inches(2.5),Inches(2.0),RGBColor(0x1D,0x40,0xAF)),
        (Inches(12.5),Inches(5.0),Inches(1.5),RGBColor(0x14,0x2A,0x60)),
        (Inches(10.0),Inches(5.8),Inches(1.2),RGBColor(0x1E,0x29,0x3B)),
    ]:
        _rect(sl,cx-cr/2,cy-cr/2,cr,cr,fill=col,round_=True)
    # BL badge
    _rect(sl,Inches(0.5),Inches(1.4),Inches(1.2),Inches(1.2),fill=BLUE,round_=True)
    _txt(sl,"BL",Inches(0.5),Inches(1.45),Inches(1.2),Inches(1.0),
         size=32,bold=True,color=WHITE,align=PP_ALIGN.CENTER)
    _txt(sl,"Thank You",Inches(0.4),Inches(2.8),Inches(8.5),Inches(1.4),
         size=60,bold=True,color=WHITE)
    _txt(sl,"Questions & Discussion",Inches(0.4),Inches(4.2),Inches(8.0),Inches(0.7),
         size=26,color=CYAN_L)
    _rect(sl,Inches(0.4),Inches(4.95),Inches(2.5),Inches(0.05),fill=CYAN)
    qas=[
        "How does BugLens handle edge-case inputs?",
        "How would you scale this to a multi-tenant SaaS?",
        "How does the scoring rubric compare to GPT-based scoring?",
        "Walk me through a defect that failed your tests.",
    ]
    for i,q in enumerate(qas):
        _txt(sl,"Q  "+q,Inches(0.4),Inches(5.1)+i*Inches(0.42),Inches(8.5),Inches(0.38),
             size=10.5,color=MUTED)
    # Contact strip
    _rect(sl,Inches(0.3),SH-Inches(0.65),Inches(8.5),Inches(0.5),fill=SURF2,round_=True)
    for j,(label,val) in enumerate([
        ("Project","BugLens – Defect Quality Checker"),
        ("Stack","Python · FastAPI · Streamlit · Pytest"),
        ("Tests","216 cases · 100 % pass rate"),
    ]):
        _txt(sl,f"{label}: {val}",Inches(0.45)+j*Inches(2.85),SH-Inches(0.62),
             Inches(2.75),Inches(0.4),size=8,color=MUTED)
    _notes(sl,"Closing slide. After presenting, leave this on screen during Q&A. The four anticipated questions at the bottom are ones interviewers commonly ask — you should have crisp answers ready for each. Most important: 'Walk me through a defect that failed your tests' — use SDEF-01 (Compare page crash) as your example.")

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    prs = Presentation()
    prs.slide_width  = SW
    prs.slide_height = SH

    builders = [
        s01_title, s02_exec, s03_problem, s04_objectives, s05_requirements,
        s06_architecture, s07_stack, s08_sdlc, s09_sdlc_table, s10_vmodel,
        s11_stlc, s12_functional, s13_integration, s14_system, s15_regression,
        s16_performance, s17_uat, s18_defects, s19_dashboard, s20_demo,
        s21_challenges, s22_future, s23_learnings, s24_conclusion, s25_thanks,
    ]
    for fn in builders:
        fn(prs)
        print(f"  ✓ {fn.__name__}")

    out = Path(__file__).parent / "BugLens_Presentation.pptx"
    prs.save(str(out))
    print(f"\n✅  Saved → {out}")

if __name__ == "__main__":
    main()
