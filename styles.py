"""
MediConnect UI Styling & Shared Component Library
Design system: institutional, wayfinding-first, zero decoration for its own sake.
Reference: hospital signage — clear, color-coded, legible at a glance.

ALL color, spacing, and type tokens are defined here as named constants.
No view file may define its own one-off styling values.
"""

# ─── Design Tokens ────────────────────────────────────────────────────────────

# Surface & layout
COLOR_BG          = "#F4F6F8"   # Page background
COLOR_SURFACE     = "#FFFFFF"   # Card / table row surface
COLOR_BORDER      = "#D8DEE3"   # 1px hairlines, card edges
COLOR_TEXT        = "#1A2733"   # Primary body & heading text
COLOR_TEXT_MUTED  = "#64748B"   # Captions, secondary labels
COLOR_ACCENT      = "#2563EB"   # Interactive elements, Scheduled status

# Status colors — THE ONLY source of status/urgency color in the entire app
COLOR_CONFIRMED   = "#15803D"   # Confirmed, Blood Available
COLOR_MUTED_STATUS= "#64748B"   # Completed, Low urgency (same as muted text)
COLOR_DANGER      = "#B91C1C"   # Cancelled, No-show, High urgency
COLOR_AMBER       = "#B45309"   # Medium urgency, Blood Requested
COLOR_PENDING     = "#B45309"   # Pending / En route (same amber)

# Tint backgrounds for badges (same-hue, light — colored text on tinted bg)
TINT_BLUE   = "#EFF6FF"
TINT_GREEN  = "#F0FDF4"
TINT_RED    = "#FEF2F2"
TINT_AMBER  = "#FFFBEB"
TINT_GRAY   = "#F8FAFC"

# Border radius — flat-institutional, not pill/fully-rounded
RADIUS_CARD  = "5px"
RADIUS_BADGE = "3px"
RADIUS_INPUT = "4px"

# Left-bar width — the one signature visual element
BAR_WIDTH = "4px"

# ─── Status → (text_color, tint_bg, bar_color) mapping ──────────────────────
# Single lookup used by both badges and left-bar coloring.

STATUS_TOKENS = {
    # Appointment statuses
    "Scheduled":  (COLOR_ACCENT,    TINT_BLUE,  COLOR_ACCENT),
    "Confirmed":  (COLOR_CONFIRMED, TINT_GREEN, COLOR_CONFIRMED),
    "Completed":  (COLOR_TEXT_MUTED,TINT_GRAY,  COLOR_TEXT_MUTED),
    "Cancelled":  (COLOR_DANGER,    TINT_RED,   COLOR_DANGER),
    "No-show":    (COLOR_DANGER,    TINT_RED,   COLOR_DANGER),
    # Ambulance statuses
    "Pending":    (COLOR_AMBER,     TINT_AMBER, COLOR_AMBER),
    "Dispatched": (COLOR_ACCENT,    TINT_BLUE,  COLOR_ACCENT),
    "En route":   (COLOR_AMBER,     TINT_AMBER, COLOR_AMBER),
    "Resolved":   (COLOR_CONFIRMED, TINT_GREEN, COLOR_CONFIRMED),
    # Urgency
    "High":       (COLOR_DANGER,    TINT_RED,   COLOR_DANGER),
    "Medium":     (COLOR_AMBER,     TINT_AMBER, COLOR_AMBER),
    "Low":        (COLOR_TEXT_MUTED,TINT_GRAY,  COLOR_TEXT_MUTED),
    # Blood record types
    "Available":  (COLOR_CONFIRMED, TINT_GREEN, COLOR_CONFIRMED),
    "Requested":  (COLOR_AMBER,     TINT_AMBER, COLOR_AMBER),
    # Blood record statuses
    "Open":       (COLOR_ACCENT,    TINT_BLUE,  COLOR_ACCENT),
    "Fulfilled":  (COLOR_CONFIRMED, TINT_GREEN, COLOR_CONFIRMED),
    "Expired":    (COLOR_TEXT_MUTED,TINT_GRAY,  COLOR_TEXT_MUTED),
}

def _status_tokens(key: str):
    """Return (text_color, tint_bg, bar_color) for any status/urgency/type key."""
    return STATUS_TOKENS.get(key, (COLOR_TEXT_MUTED, TINT_GRAY, COLOR_TEXT_MUTED))


# ─── Global CSS ───────────────────────────────────────────────────────────────

CUSTOM_CSS = f"""
<style>
    /* IBM Plex Sans — institutional, legible, zero decoration */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&display=swap');

    html, body, [class*="css"] {{
        font-family: 'IBM Plex Sans', system-ui, -apple-system, sans-serif;
        font-size: 15px;
        color: {COLOR_TEXT};
    }}

    /* Ambient background canvas */
    .stApp {{
        background: linear-gradient(180deg, #F8FAFC 0%, #EEF2F6 100%) !important;
    }}

    .block-container {{
        padding-top: 1.2rem;
        padding-bottom: 3rem;
    }}

    /* Top Brand Header */
    .app-brand {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 6px 0 16px 0;
        border-bottom: 1px solid #E2E8F0;
        margin-bottom: 18px;
    }}
    .brand-title {{
        font-size: 1.45rem;
        font-weight: 700;
        color: #0F172A;
        letter-spacing: -0.02em;
        margin: 0;
    }}
    .brand-subtitle {{
        font-size: 0.85rem;
        color: {COLOR_TEXT_MUTED};
        font-weight: 400;
        margin: 2px 0 0 0;
    }}

    /* Headings */
    h1, h2, h3, h4 {{
        font-family: 'IBM Plex Sans', system-ui, -apple-system, sans-serif;
        font-weight: 600;
        color: {COLOR_TEXT};
        letter-spacing: -0.01em;
    }}

    /* Modern Buttons */
    .stButton > button {{
        border-radius: 6px;
        font-weight: 500;
        font-family: 'IBM Plex Sans', system-ui, -apple-system, sans-serif;
        padding: 0.45rem 1.15rem;
        border: 1px solid {COLOR_BORDER};
        background-color: {COLOR_SURFACE};
        color: {COLOR_TEXT};
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        transition: all 0.15s ease-in-out;
    }}
    .stButton > button:hover {{
        background-color: {TINT_BLUE};
        border-color: {COLOR_ACCENT};
        color: {COLOR_ACCENT};
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.1);
    }}
    .stButton > button[kind="primary"] {{
        background-color: {COLOR_ACCENT};
        color: #FFFFFF;
        border-color: {COLOR_ACCENT};
        box-shadow: 0 1px 3px rgba(37, 99, 235, 0.2);
    }}
    .stButton > button[kind="primary"]:hover {{
        background-color: #1D4ED8;
        border-color: #1D4ED8;
        color: #FFFFFF;
        box-shadow: 0 2px 6px rgba(29, 78, 216, 0.3);
    }}

    /* Form submit buttons */
    .stFormSubmitButton > button {{
        border-radius: 6px;
        font-weight: 600;
        font-family: 'IBM Plex Sans', system-ui, -apple-system, sans-serif;
        background-color: {COLOR_ACCENT};
        color: #FFFFFF;
        border: none;
        padding: 0.5rem 1.25rem;
        box-shadow: 0 1px 3px rgba(37, 99, 235, 0.25);
        transition: all 0.15s ease-in-out;
    }}
    .stFormSubmitButton > button:hover {{
        background-color: #1D4ED8;
        box-shadow: 0 2px 6px rgba(29, 78, 216, 0.35);
    }}

    /* Inputs and selects */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {{
        border-radius: 6px !important;
        border-color: {COLOR_BORDER} !important;
        font-family: 'IBM Plex Sans', system-ui, -apple-system, sans-serif !important;
        font-size: 0.92rem !important;
        color: {COLOR_TEXT} !important;
        background-color: #FFFFFF !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
    }}

    /* ── Modern Ambient Segmented Tabs ────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: #E2E8F0;
        padding: 4px;
        border-radius: 8px;
        border-bottom: none !important;
        gap: 3px;
        display: flex;
        flex-wrap: wrap;
        margin-bottom: 20px;
        box-shadow: inset 0 1px 2px rgba(15, 23, 42, 0.05);
    }}
    .stTabs [data-baseweb="tab"] {{
        font-family: 'IBM Plex Sans', system-ui, -apple-system, sans-serif;
        font-weight: 500;
        font-size: 0.86rem;
        color: #475569;
        border-radius: 6px;
        padding: 0.42rem 1rem;
        border: none !important;
        background: transparent;
        transition: all 0.15s ease-in-out;
        white-space: nowrap;
    }}
    .stTabs [data-baseweb="tab"]:hover {{
        color: #0F172A;
        background-color: rgba(255, 255, 255, 0.6);
    }}
    .stTabs [aria-selected="true"] {{
        color: #0F172A !important;
        background-color: #FFFFFF !important;
        font-weight: 600 !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.1), 0 1px 2px rgba(15, 23, 42, 0.06);
    }}
    .stTabs [data-baseweb="tab-highlight"] {{
        display: none !important;
    }}
    .stTabs [data-baseweb="tab-border"] {{
        display: none !important;
    }}

    /* Dividers */
    hr {{
        border: none;
        border-top: 1px solid #E2E8F0;
        margin: 1.25rem 0;
    }}

    /* Dataframe / table overrides */
    .stDataFrame {{
        border: 1px solid {COLOR_BORDER};
        border-radius: 6px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03);
    }}


    /* ── Card component ────────────────────────────────────────────────────── */
    .mc-card {{
        background-color: {COLOR_SURFACE};
        border: 1px solid {COLOR_BORDER};
        border-radius: {RADIUS_CARD};
        border-left-width: {BAR_WIDTH};
        border-left-style: solid;
        box-shadow: 0 2px 6px -1px rgba(15, 23, 42, 0.05), 0 1px 3px -1px rgba(15, 23, 42, 0.03);
        padding: 20px 24px;
        margin: 10px 0 18px 0;
    }}
    .mc-card-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 12px;
        margin-bottom: 14px;
        border-bottom: 1px solid {COLOR_BORDER};
    }}
    .mc-card-title {{
        font-size: 1.05rem;
        font-weight: 600;
        color: {COLOR_TEXT};
        margin: 0;
    }}
    .mc-id-badge {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.82rem;
        font-weight: 600;
        background-color: {TINT_BLUE};
        color: {COLOR_ACCENT};
        padding: 3px 8px;
        border-radius: {RADIUS_BADGE};
        border: 1px solid #BFDBFE;
        letter-spacing: 0.02em;
    }}
    .mc-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 14px;
        margin-bottom: 12px;
    }}
    .mc-label {{
        font-size: 0.75rem;
        font-weight: 600;
        color: {COLOR_TEXT_MUTED};
        margin-bottom: 2px;
        text-transform: none;
        letter-spacing: 0;
    }}
    .mc-value {{
        font-size: 0.92rem;
        font-weight: 400;
        color: {COLOR_TEXT};
    }}
    .mc-notes-box {{
        background-color: {TINT_GRAY};
        border: 1px solid {COLOR_BORDER};
        border-radius: {RADIUS_INPUT};
        padding: 10px 12px;
        font-size: 0.88rem;
        color: {COLOR_TEXT};
        margin-top: 4px;
    }}
    .mc-footer {{
        font-size: 0.8rem;
        color: {COLOR_TEXT_MUTED};
        border-top: 1px solid {COLOR_BORDER};
        padding-top: 10px;
        margin-top: 10px;
    }}

    /* ── Badge component ───────────────────────────────────────────────────── */
    .mc-badge {{
        display: inline-block;
        font-size: 0.73rem;
        font-weight: 600;
        padding: 2px 7px;
        border-radius: {RADIUS_BADGE};
        letter-spacing: 0.01em;
        vertical-align: middle;
    }}

    /* ── Admin info banner ─────────────────────────────────────────────────── */
    .admin-banner {{
        background-color: {TINT_BLUE};
        border-left: {BAR_WIDTH} solid {COLOR_ACCENT};
        border-radius: 0 {RADIUS_CARD} {RADIUS_CARD} 0;
        padding: 10px 16px;
        margin-bottom: 18px;
        font-size: 0.88rem;
        color: {COLOR_TEXT};
    }}

    /* ── Emergency alert banner & pulse animation ────────────────────────── */
    @keyframes pulse-red {{
        0% {{ box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }}
        70% {{ box-shadow: 0 0 0 7px rgba(239, 68, 68, 0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }}
    }}
    .emergency-pulse-dot {{
        display: inline-block;
        width: 8px;
        height: 8px;
        background-color: #EF4444;
        border-radius: 50%;
        animation: pulse-red 1.8s infinite;
        vertical-align: middle;
        margin-right: 6px;
    }}
    .emergency-hero-box {{
        background: #FFFFFF;
        border: 1px solid #FECACA;
        border-left: 5px solid #EF4444;
        border-radius: 10px;
        box-shadow: 0 4px 16px -2px rgba(239, 68, 68, 0.08), 0 2px 4px -1px rgba(15, 23, 42, 0.03);
        padding: 18px 22px;
        margin-bottom: 20px;
    }}
    .emergency-banner {{
        background-color: {TINT_RED};
        border-left: {BAR_WIDTH} solid {COLOR_DANGER};
        border-radius: 0 {RADIUS_CARD} {RADIUS_CARD} 0;
        padding: 10px 16px;
        margin-bottom: 16px;
        font-size: 0.88rem;
        color: {COLOR_DANGER};
    }}


    /* ── HTML table for status-bearing rows ────────────────────────────────── */
    .mc-table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 0.88rem;
        font-family: 'IBM Plex Sans', system-ui, -apple-system, sans-serif;
    }}
    .mc-table th {{
        font-weight: 600;
        font-size: 0.78rem;
        color: {COLOR_TEXT_MUTED};
        border-bottom: 2px solid {COLOR_BORDER};
        padding: 8px 12px;
        text-align: left;
        background-color: {TINT_GRAY};
    }}
    .mc-table td {{
        padding: 9px 12px;
        border-bottom: 1px solid {COLOR_BORDER};
        color: {COLOR_TEXT};
        vertical-align: middle;
    }}
    .mc-table tr:last-child td {{
        border-bottom: none;
    }}
    .mc-table tr:hover td {{
        background-color: {TINT_GRAY};
    }}
    /* Left bar on table rows — applied via inline style on <tr> */
    .mc-row-bar {{
        border-left-width: {BAR_WIDTH};
        border-left-style: solid;
    }}
</style>
"""





# ─── Utility ──────────────────────────────────────────────────────────────────

def clean_html(html_str: str) -> str:
    """Strip leading/trailing whitespace per line and remove blank lines.
    Prevents CommonMark from treating indented HTML as a code block."""
    return "\n".join(line.strip() for line in html_str.splitlines() if line.strip())


# ─── Shared Badge Renderer ────────────────────────────────────────────────────

def render_badge(label: str, key: str = None) -> str:
    """Render a rectangular status/urgency/type badge.

    Uses the STATUS_TOKENS lookup. Falls back gracefully for unknown keys.
    ``key`` is used for token lookup when the label text differs from the token
    key (e.g. passing label='O+' with key=None uses label as-is in gray).
    """
    lookup = key if key is not None else label
    text_color, tint_bg, _ = _status_tokens(lookup)
    return (
        f'<span class="mc-badge" '
        f'style="color:{text_color}; background-color:{tint_bg};">'
        f'{label}</span>'
    )


# ── Convenience wrappers (keep old names so existing call sites work) ──────────

def render_status_badge(status: str) -> str:
    """Badge for appointment or ambulance status."""
    return render_badge(status)

def render_urgency_badge(urgency: str) -> str:
    """Badge for ambulance request urgency level."""
    return render_badge(urgency)

def render_patient_badge(blood_group: str) -> str:
    """Blood-group tag — uses accent blue as a neutral identifier."""
    return (
        f'<span class="mc-badge" '
        f'style="color:{COLOR_ACCENT}; background-color:{TINT_BLUE};">'
        f'{blood_group}</span>'
    )


# ─── Shared Card Renderer ─────────────────────────────────────────────────────

def render_card(
    title: str,
    record_id: str,
    fields: list,          # list of (label, value_html) tuples
    bar_key: str = None,   # looked up in STATUS_TOKENS for left-bar color
    bar_color: str = None, # explicit override — use one or the other, not both
    badges: list = None,   # list of badge HTML strings shown next to record_id
    notes_label: str = None,
    notes_value: str = None,
    footer: str = None,
) -> str:
    """Universal card renderer — single template for all record types.

    The colored left-bar is the ONE signature visual element of the app.
    Every card MUST pass either ``bar_key`` (looked up in STATUS_TOKENS)
    or an explicit ``bar_color``. If neither is provided the accent color
    is used as a safe fallback.

    Parameters
    ----------
    title       : Card heading text
    record_id   : Displayed in the ID badge (monospace, top-right)
    fields      : Ordered list of (label, value_html) pairs for the data grid
    bar_key     : Status/urgency/type token key → resolves bar color automatically
    bar_color   : Explicit hex color for the left bar (overrides bar_key)
    badges      : Pre-rendered badge HTML strings shown in the card header
    notes_label : Optional label above a full-width notes block
    notes_value : Content of the notes block (plain text)
    footer      : Optional small-print footer line
    """
    # Resolve bar color
    if bar_color:
        left_color = bar_color
    elif bar_key:
        _, _, left_color = _status_tokens(bar_key)
    else:
        left_color = COLOR_ACCENT

    # Badge cluster in header
    badge_html = ""
    if badges:
        badge_html = "&nbsp;" + "&nbsp;".join(badges)

    # Data grid
    grid_cells = ""
    for label, value_html in fields:
        grid_cells += (
            f'<div>'
            f'<div class="mc-label">{label}</div>'
            f'<div class="mc-value">{value_html}</div>'
            f'</div>'
        )

    # Optional notes block
    notes_block = ""
    if notes_label and notes_value:
        notes_block = (
            f'<div style="margin-top:10px;">'
            f'<div class="mc-label">{notes_label}</div>'
            f'<div class="mc-notes-box">{notes_value}</div>'
            f'</div>'
        )

    # Optional footer
    footer_block = ""
    if footer:
        footer_block = f'<div class="mc-footer">{footer}</div>'

    raw = f"""
    <div class="mc-card" style="border-left-color:{left_color};">
        <div class="mc-card-header">
            <span class="mc-card-title">{title}</span>
            <div>
                <span class="mc-id-badge">{record_id}</span>
                {badge_html}
            </div>
        </div>
        <div class="mc-grid">
            {grid_cells}
        </div>
        {notes_block}
        {footer_block}
    </div>
    """
    return clean_html(raw)


# ─── Domain-specific Card Renderers (thin wrappers around render_card) ────────

def render_patient_card(patient) -> str:
    """Administrative record card for a patient."""
    fields = [
        ("Date of Birth",  patient.dob),
        ("Gender",         patient.gender),
        ("Phone Contact",  patient.phone),
        ("Blood Group",    render_patient_badge(patient.blood_group)),
        ("Registered On",  patient.created_at),
        ("Address",        patient.address if patient.address else "Not provided"),
    ]
    return render_card(
        title=patient.name,
        record_id=patient.id,
        fields=fields,
        bar_color=COLOR_ACCENT,
        notes_label="Administrative Notes" if patient.notes else None,
        notes_value=patient.notes if patient.notes else None,
    )


def render_appointment_card(appointment, patient_name: str = "") -> str:
    """Booking confirmation card for an appointment."""
    patient_display = (
        f"{patient_name} ({appointment.patient_id})"
        if patient_name else appointment.patient_id
    )
    fields = [
        ("Date",                  appointment.date),
        ("Time Slot",             appointment.time),
        ("Patient Record",        patient_display),
        ("Administrative Purpose", appointment.reason),
    ]
    return render_card(
        title="Appointment Booking",
        record_id=appointment.id,
        fields=fields,
        bar_key=appointment.status,
        badges=[render_status_badge(appointment.status)],
        footer=f"Booking created: {appointment.created_at} &nbsp;·&nbsp; Please arrive 10 minutes prior to your scheduled slot.",
    )


def render_blood_record_card(bld) -> str:
    """Patient-facing card for a blood availability or requirement record."""
    type_badge   = render_badge(bld.type)
    group_badge  = render_patient_badge(bld.blood_group)
    status_badge = render_badge(bld.status) if bld.status != "Open" else ""

    badges = [group_badge, type_badge]
    if status_badge:
        badges.append(status_badge)

    fields = [
        ("Facility Location",       bld.location),
        ("Listing Type",            f"{bld.type} ({bld.units} Units)"),
        ("Contact / Coordinator",   bld.contact_info),
        ("Listed Timestamp",        bld.created_at),
    ]
    return render_card(
        title=f"{bld.blood_group} Blood Stock Record",
        record_id=bld.id,
        fields=fields,
        bar_key=bld.type,   # "Available" → green bar, "Requested" → amber bar
        badges=badges,
    )


def render_ambulance_card(amb, linked_patient_info: str = "") -> str:
    """Detail card for an ambulance request (used in both patient + staff views)."""
    fields = [
        ("Requester Name",    amb.requester_name),
        ("Callback Phone",    amb.phone),
        ("Urgency Level",     f"{amb.urgency_tag} Priority"),
        ("Submitted At",      amb.created_at),
    ]
    if linked_patient_info:
        fields.append(("Linked Patient Record", linked_patient_info))

    notes_label = "Pickup Notes" if amb.notes else None
    notes_value = amb.notes if amb.notes else None

    return render_card(
        title="Emergency Response Dispatch Ticket",
        record_id=amb.id,
        fields=fields,
        bar_key=amb.urgency_tag,
        badges=[render_urgency_badge(amb.urgency_tag), render_status_badge(amb.status)],
        notes_label="Pickup Location",
        notes_value=amb.pickup_location,
        footer=notes_value if notes_label else None,
    )


def render_status_table(headers: list, rows: list, row_bar_keys: list) -> str:
    """Render an administrative table where each row has a colored left bar based on row_bar_keys.

    headers: list of column header strings
    rows: list of row lists (each cell can be text or pre-formatted HTML like badges)
    row_bar_keys: list of status/urgency keys matching rows (one per row)
    """
    th_html = "".join(f"<th>{h}</th>" for h in headers)
    tr_html = []
    for row, bar_key in zip(rows, row_bar_keys):
        _, _, bar_color = _status_tokens(bar_key) if bar_key else (None, None, COLOR_BORDER)
        cells = []
        for idx, cell in enumerate(row):
            if idx == 0:
                cells.append(f'<td style="border-left: {BAR_WIDTH} solid {bar_color}; font-weight: 500;">{cell}</td>')
            else:
                cells.append(f"<td>{cell}</td>")
        tr_html.append(f"<tr>{''.join(cells)}</tr>")

    table_content = f"""
    <div style="border: 1px solid {COLOR_BORDER}; border-radius: {RADIUS_CARD}; overflow-x: auto; margin: 12px 0;">
        <table class="mc-table">
            <thead><tr>{th_html}</tr></thead>
            <tbody>{''.join(tr_html)}</tbody>
        </table>
    </div>
    """
    return clean_html(table_content)

