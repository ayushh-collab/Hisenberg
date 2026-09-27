"""
Staff Portal Views
Administrative and clinic staff management interface.
Zero diagnostic / clinical decision logic.
Feature 2: Patient Search & Directory
Feature 4: Appointment Scheduling View
Feature 7: Ambulance Request Management & Patient Record Linking
"""
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
from datetime import date
from models import VALID_BLOOD_GROUPS, APPOINTMENT_STATUSES, AMBULANCE_STATUSES
import database

from styles import (
    render_patient_card,
    render_status_badge,
    render_urgency_badge,
    render_badge,
    render_ambulance_card,
    render_status_table,
    clean_html,
    COLOR_TEXT_MUTED,
    COLOR_CONFIRMED,
    COLOR_DANGER,
    COLOR_ACCENT,
    COLOR_BORDER,
    TINT_GRAY,
)

def render_staff_portal():
    st.markdown("### Clinic Staff Portal")
    st.markdown(
        '<div class="admin-banner">'
        '<strong>Staff Administration:</strong> Manage patient records, review appointment schedules, '
        'dispatch ambulances, and link emergency requests.'
        '</div>',
        unsafe_allow_html=True
    )

    tab_overview, tab_schedule, tab_patients, tab_amb = st.tabs([
        "📊 Operations Overview",
        "Appointment Schedule",
        "Patient Records",
        "🚨 Ambulance Requests"
    ])

    with tab_overview:
        render_clinic_dashboard()

    with tab_schedule:
        render_appointment_schedule()

    with tab_patients:
        render_patient_directory()

    with tab_amb:
        render_ambulance_management()


# ─────────────────────────────────────────────
# Feature: Clinic Operations Dashboard
# ─────────────────────────────────────────────

def render_clinic_dashboard():
    # ── 1. Layered Hero Overview Band (Subtle depth) ──────────────────────
    st.markdown(
        f"""
        <div style="background: #FFFFFF; border: 1px solid {COLOR_BORDER}; border-radius: 8px; padding: 18px 24px; box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.05), 0 2px 4px -1px rgba(15, 23, 42, 0.03); margin-bottom: 18px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                <div>
                    <h3 style="margin: 0; font-size: 1.25rem; font-weight: 700; color: #0F172A; letter-spacing: -0.01em;">
                        Clinic Operations &amp; Triage Overview
                    </h3>
                    <p style="margin: 3px 0 0 0; font-size: 0.85rem; color: {COLOR_TEXT_MUTED};">
                        Central operational intelligence, triage activity, visit load, and regional inventory.
                    </p>
                </div>
                <div>
                    <span class="mc-badge" style="background-color: #EFF6FF; color: {COLOR_ACCENT}; font-weight: 600; padding: 4px 12px; border-radius: 6px; font-size: 0.78rem;">
                        Real-Time Operational Telemetry
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ── 2. Data Gathering ─────────────────────────────────────────────────
    all_patients = database.get_all_patients()
    total_patients_cnt = len(all_patients)

    all_appts = database.get_all_appointments()
    today_str = date.today().strftime("%Y-%m-%d")
    today_appts_cnt = sum(1 for a in all_appts if a.date == today_str)

    all_ambs = database.get_all_ambulance_requests()
    active_ambs_cnt = sum(1 for a in all_ambs if a.status != "Resolved")

    blood_records = database.search_blood_records(status_filter="Open", record_type="Available")
    total_blood_units = sum(b.units for b in blood_records)

    # ── 3. Typographic Scale Hero Stat Cards with Count-Up ─────────────────
    countup_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'IBM Plex Sans', system-ui, sans-serif; }}
    body {{ background: transparent; }}
    .stats-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 14px;
    }}
    .stat-card {{
        background: #FFFFFF;
        border: 1px solid #D8DEE3;
        border-radius: 8px;
        padding: 16px 20px;
        box-shadow: 0 3px 12px -2px rgba(15, 23, 42, 0.05), 0 1px 3px -1px rgba(15, 23, 42, 0.03);
    }}
    .stat-num {{
        font-size: 2.5rem;
        font-weight: 700;
        color: #0F172A;
        line-height: 1.1;
        letter-spacing: -0.03em;
        margin-bottom: 4px;
    }}
    .stat-label {{
        font-size: 0.76rem;
        font-weight: 600;
        color: #64748B;
        text-transform: none;
        letter-spacing: 0;
    }}
    </style>
    </head>
    <body>
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-num" id="stat_today">0</div>
            <div class="stat-label">Appointments Today</div>
        </div>
        <div class="stat-card">
            <div class="stat-num" id="stat_amb">0</div>
            <div class="stat-label">Active Triage Ambulances</div>
        </div>
        <div class="stat-card">
            <div class="stat-num" id="stat_patients">0</div>
            <div class="stat-label">Registered Patients</div>
        </div>
        <div class="stat-card">
            <div class="stat-num" id="stat_blood">0</div>
            <div class="stat-label">Available Blood Units</div>
        </div>
    </div>
    <script>
    function countUp(id, target, duration) {{
        const el = document.getElementById(id);
        if (!el) return;
        if (target === 0) {{ el.innerText = "0"; return; }}
        let start = 0;
        const stepTime = 16;
        const steps = Math.max(1, Math.floor(duration / stepTime));
        const increment = target / steps;
        const timer = setInterval(() => {{
            start += increment;
            if (start >= target) {{
                el.innerText = target;
                clearInterval(timer);
            }} else {{
                el.innerText = Math.floor(start);
            }}
        }}, stepTime);
    }}
    countUp("stat_today", {today_appts_cnt}, 700);
    countUp("stat_amb", {active_ambs_cnt}, 700);
    countUp("stat_patients", {total_patients_cnt}, 700);
    countUp("stat_blood", {total_blood_units}, 700);
    </script>
    </body>
    </html>
    """
    components.html(countup_html, height=108)

    st.markdown("<div style='margin-bottom: 18px;'></div>", unsafe_allow_html=True)

    # ── 4. Minimal Visualization & Triage Stream ──────────────────────────
    c_chart, c_stream = st.columns([3, 2])

    with c_chart:
        st.markdown("##### Scheduled Visits by Visit Category")
        st.caption("Distribution across administrative care categories. Minimalist single-accent telemetry.")

        cat_counts = {}
        for a in all_appts:
            main_cat = a.reason.split(":")[0].strip() if ":" in a.reason else a.reason[:24].strip()
            cat_counts[main_cat] = cat_counts.get(main_cat, 0) + 1

        if not cat_counts:
            cat_counts = {"No Bookings": 0}

        categories = list(cat_counts.keys())
        counts = list(cat_counts.values())

        fig = go.Figure(
            go.Bar(
                x=categories,
                y=counts,
                marker_color="#2563EB",  # STRICTLY single accent color only!
                marker_line_width=0,
                hoverinfo="x+y",
            )
        )
        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=30),
            height=260,
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            font=dict(family="IBM Plex Sans, system-ui, sans-serif", size=12, color="#475569"),
            xaxis=dict(
                showgrid=False,
                linecolor="#D8DEE3",
                tickfont=dict(size=11, color="#64748B"),
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="#F1F5F9",
                linecolor="#D8DEE3",
                tickfont=dict(size=11, color="#64748B"),
                dtick=1,
            ),
            bargap=0.35,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with c_stream:
        st.markdown("##### Emergency Triage Load")
        st.caption("Active incident status across response units.")

        if not all_ambs:
            st.info("No emergency ambulance requests logged.")
        else:
            amb_summary_rows = []
            amb_summary_keys = []
            for a in all_ambs[:5]:
                amb_summary_keys.append(a.urgency_tag)
                amb_summary_rows.append([
                    a.id,
                    a.requester_name,
                    f"{a.urgency_tag} Urgency",
                    render_status_badge(a.status)
                ])

            st.markdown(
                render_status_table(
                    headers=["Ticket ID", "Caller", "Urgency", "Status"],
                    rows=amb_summary_rows,
                    row_bar_keys=amb_summary_keys
                ),
                unsafe_allow_html=True
            )


# ─────────────────────────────────────────────
# Feature 4: Appointment Scheduling View
# ─────────────────────────────────────────────

def render_appointment_schedule():
    st.subheader("Appointment Schedule")
    st.caption("View, filter, and manage all booked clinic appointments.")

    col_date_f, col_status_f, col_refresh = st.columns([2, 2, 1])
    with col_date_f:
        date_filter = st.selectbox(
            "Filter by Date",
            options=["Upcoming", "Today", "Tomorrow", "All", "Past"],
            index=0,
            key="sched_date_filter"
        )
    with col_status_f:
        status_filter = st.selectbox(
            "Filter by Status",
            options=["All"] + APPOINTMENT_STATUSES,
            index=0,
            key="sched_status_filter"
        )
    with col_refresh:
        st.markdown("<div style='margin-top:27px'></div>", unsafe_allow_html=True)
        if st.button("Refresh", key="sched_refresh", use_container_width=True):
            st.rerun()

    rows = database.get_appointments_with_patient_details(
        date_filter=date_filter,
        status_filter=status_filter
    )

    today_str = date.today().strftime("%Y-%m-%d")
    today_count = len([r for r in rows if r["date"] == today_str])
    total_count = len(rows)

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Showing", total_count, label_visibility="visible")
    with m2:
        st.metric("Today's Appointments", today_count)
    with m3:
        pending = sum(1 for r in rows if r["status"] == "Scheduled")
        st.metric("Awaiting Confirmation", pending)

    if not rows:
        st.info(
            f"No appointments found for the selected filters — "
            f"**Date:** {date_filter} | **Status:** {status_filter}."
        )
        return

    def _date_label(d: str) -> str:
        if d == today_str:
            return f"{d} (Today)"
        return d

    headers = ["Appt. ID", "Date", "Time", "Patient Name", "Patient ID", "Phone", "Blood Group", "Purpose", "Status"]
    table_rows = []
    status_keys = []
    for r in rows:
        status_keys.append(r["status"])
        table_rows.append([
            r["apt_id"],
            _date_label(r["date"]),
            r["time"],
            r["patient_name"] or "—",
            r["patient_id"],
            r["patient_phone"] or "—",
            r["blood_group"] or "—",
            r["reason"],
            render_status_badge(r["status"])
        ])

    st.markdown(render_status_table(headers, table_rows, status_keys), unsafe_allow_html=True)


    st.divider()

    st.markdown("#### Update Appointment Status")
    st.caption("Select an appointment to change its administrative status.")

    apt_options = {r["apt_id"]: f"{r['apt_id']} — {r.get('patient_name') or r['patient_id']} · {r['date']} {r['time']}" for r in rows}

    col_sel, col_new_status, col_apply = st.columns([3, 2, 1])
    with col_sel:
        selected_apt_id = st.selectbox(
            "Select Appointment",
            options=list(apt_options.keys()),
            format_func=lambda k: apt_options[k],
            key="sched_selected_apt"
        )
    with col_new_status:
        selected_row = next((r for r in rows if r["apt_id"] == selected_apt_id), None)
        current_status = selected_row["status"] if selected_row else "Scheduled"
        current_idx = APPOINTMENT_STATUSES.index(current_status) if current_status in APPOINTMENT_STATUSES else 0
        new_status = st.selectbox(
            "New Status",
            options=APPOINTMENT_STATUSES,
            index=current_idx,
            key="sched_new_status"
        )
    with col_apply:
        st.markdown("<div style='margin-top:27px'></div>", unsafe_allow_html=True)
        update_btn = st.button("Apply", key="sched_update_btn", use_container_width=True)

    if update_btn:
        if new_status == current_status:
            st.warning(f"Appointment **{selected_apt_id}** is already **{current_status}**. No change applied.")
        else:
            success = database.update_appointment_status(selected_apt_id, new_status)
            if success:
                st.success(
                    f"Appointment **{selected_apt_id}** status updated: "
                    f"**{current_status}** → **{new_status}**"
                )
                st.rerun()
            else:
                st.error("Status update failed. Please try again.")

    if selected_row:
        with st.expander(f"Detail: {selected_apt_id}", expanded=False):
            cols = st.columns(2)
            fields = [
                ("Appointment ID", selected_row["apt_id"]),
                ("Date", _date_label(selected_row["date"])),
                ("Time Slot", selected_row["time"]),
                ("Patient ID", selected_row["patient_id"]),
                ("Patient Name", selected_row.get("patient_name") or "—"),
                ("Phone", selected_row.get("patient_phone") or "—"),
                ("Blood Group", selected_row.get("blood_group") or "—"),
                ("Purpose / Remarks", selected_row["reason"]),
                ("Status", render_status_badge(selected_row["status"])),
                ("Booking Created", selected_row.get("apt_created_at", "—")),

            ]
            for i, (label, value) in enumerate(fields):
                with cols[i % 2]:
                    st.markdown(
                        f'<div class="mc-label">{label}</div>'
                        f'<div class="mc-value">{value}</div>',
                        unsafe_allow_html=True
                    )

    # ── Feature B: Administrative Follow-up Worklist (Staff side) ─────────────
    st.divider()
    st.markdown("#### 📋 Administrative Follow-up Worklist")
    st.caption("Patients with completed appointments and no subsequent follow-up booked. Purely informational worklist for clinic staff.")

    col_thresh, col_summary = st.columns([1, 2])
    with col_thresh:
        days_thresh = st.slider(
            "Completed More Than [N] Days Ago",
            min_value=7,
            max_value=120,
            value=30,
            step=1,
            key="followup_days_threshold"
        )

    due_patients = database.get_patients_due_for_followup(days_threshold=days_thresh)

    with col_summary:
        st.markdown(
            f"<div style='margin-top: 26px; font-size: 0.9rem; color: #475569;'>"
            f"Found <strong>{len(due_patients)}</strong> patient(s) due for follow-up coordination "
            f"(> {days_thresh} days elapsed since completed visit with zero subsequent booking)."
            f"</div>",
            unsafe_allow_html=True
        )

    if not due_patients:
        st.info(f"No patients found with completed visits older than {days_thresh} days without a subsequent appointment.")
    else:
        fu_headers = ["Patient ID", "Patient Name", "Phone", "Blood Group", "Completed Visit Date", "Elapsed", "Prior Visit Purpose / Reason"]
        fu_rows = []
        fu_keys = []
        for p in due_patients:
            fu_keys.append("Requested")  # Amber wayfinding indicator for follow-up attention
            fu_rows.append([
                p["patient_id"],
                p["patient_name"],
                p["patient_phone"],
                p["blood_group"],
                p["completed_date"],
                f"{p['days_elapsed']} days ago",
                p["reason"]
            ])

        st.markdown(
            render_status_table(fu_headers, fu_rows, fu_keys),
            unsafe_allow_html=True
        )



# ─────────────────────────────────────────────
# Feature 2: Patient Records & Directory
# ─────────────────────────────────────────────


def render_patient_directory():
    st.subheader("Patient Records & Directory")
    st.caption("Search, filter, and inspect registered patient administrative records.")

    total_patients = database.count_patients()

    col_stat1, _ = st.columns([1, 3])
    with col_stat1:
        st.metric(label="Total Registered Patients", value=total_patients)

    if total_patients == 0:
        st.info("No patient records exist yet. Switch to the **Patient** role above to register your first patient.")
        return

    search_col, filter_col = st.columns([3, 1])
    with search_col:
        search_query = st.text_input(
            "Search Records",
            placeholder="Search by Patient ID (e.g. PAT-1001), Name, or Phone...",
            key="staff_search_input",
        )
    with filter_col:
        selected_bg = st.selectbox(
            "Filter Blood Group",
            options=["All"] + VALID_BLOOD_GROUPS,
            index=0,
            key="staff_bg_filter"
        )

    patients = database.search_patients(search_query)
    if selected_bg != "All":
        patients = [p for p in patients if p.blood_group == selected_bg]

    st.markdown(f"**Found {len(patients)} record(s)**" + (f" matching '{search_query}'" if search_query.strip() else ""))

    if not patients:
        st.warning("No patient records match the specified search or filter criteria.")
        return

    table_data = [
        {
            "Patient ID":      p.id,
            "Full Name":       p.name,
            "DOB":             p.dob,
            "Gender":          p.gender,
            "Phone":           p.phone,
            "Blood Group":     p.blood_group,
            "Registered Date": p.created_at
        }
        for p in patients
    ]
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("#### Patient Record Inspector")
    patient_options = {p.id: f"{p.id} — {p.name} ({p.phone})" for p in patients}
    selected_patient_id = st.selectbox(
        "Select a patient to view full administrative details:",
        options=list(patient_options.keys()),
        format_func=lambda pid: patient_options[pid],
        key="staff_selected_patient_inspector"
    )

    if selected_patient_id:
        selected_patient = next((p for p in patients if p.id == selected_patient_id), None)
        if selected_patient:
            st.markdown(render_patient_card(selected_patient), unsafe_allow_html=True)

            # ── Feature A: Basic Visit History (Staff side) ───────────────
            st.markdown("<div style='margin-top: 18px;'></div>", unsafe_allow_html=True)
            st.markdown("##### Administrative Visit History")
            st.caption("Chronological record of clinic appointments and visits for this patient.")

            patient_apts = database.get_appointments_by_patient(selected_patient.id)

            if not patient_apts:
                st.info(f"No prior appointment or visit records logged for {selected_patient.name} ({selected_patient.id}).")
            else:
                hist_headers = ["Appt ID", "Date", "Time Slot", "Administrative Purpose / Reason", "Status"]
                hist_rows = []
                hist_keys = []
                for apt in patient_apts:
                    hist_keys.append(apt.status)
                    hist_rows.append([
                        apt.id,
                        apt.date,
                        apt.time,
                        apt.reason,
                        render_status_badge(apt.status)
                    ])

                st.markdown(
                    render_status_table(hist_headers, hist_rows, hist_keys),
                    unsafe_allow_html=True
                )



# ─────────────────────────────────────────────
# Feature 7: Ambulance Request Management & Linking
# ─────────────────────────────────────────────

def render_ambulance_management():
    st.subheader("🚨 Emergency Ambulance Dispatch & Record Linking")
    st.caption("Manage active ambulance requests, dispatch response units, and link requests to patient records post-stabilization.")

    # Status filter
    col_f, col_ref = st.columns([3, 1])
    with col_f:
        status_filter = st.selectbox(
            "Filter Dispatch Queue by Status",
            options=["All"] + AMBULANCE_STATUSES,
            index=0,
            key="amb_status_filter"
        )
    with col_ref:
        st.markdown("<div style='margin-top:27px'></div>", unsafe_allow_html=True)
        if st.button("Refresh Queue", key="amb_refresh", use_container_width=True):
            st.rerun()

    requests = database.get_all_ambulance_requests(status_filter=status_filter)
    pending_count = database.count_pending_ambulance_requests()

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Total Requests", len(requests))
    with m2:
        st.metric("Active / Pending Queue", pending_count)
    with m3:
        resolved = len([r for r in requests if r.status == "Resolved"])
        st.metric("Resolved Incidents", resolved)

    if not requests:
        st.info(f"No ambulance requests found matching status filter: **{status_filter}**.")
        return

    # Scannable Table
    table_data = []
    for r in requests:
        linked_str = r.patient_id if r.patient_id else "Unlinked (Post-Call)"
        table_data.append({
            "Request ID": r.id,
            "Urgency": r.urgency_tag,
            "Requester": r.requester_name,
            "Callback Phone": r.phone,
            "Pickup Location": r.pickup_location,
            "Status": r.status,
            "Linked Patient": linked_str,
            "Submitted Time": r.created_at
        })

    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()

    # Dispatch & Linker Controls
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### 1. Update Dispatch Status")
        amb_options = {r.id: f"{r.id} — {r.requester_name} ({r.urgency_tag} Urgency)" for r in requests}
        selected_amb_id = st.selectbox(
            "Select Request to Update Status",
            options=list(amb_options.keys()),
            format_func=lambda k: amb_options[k],
            key="amb_status_selected_id"
        )

        selected_amb = next((r for r in requests if r.id == selected_amb_id), None)
        curr_status = selected_amb.status if selected_amb else "Pending"
        curr_idx = AMBULANCE_STATUSES.index(curr_status) if curr_status in AMBULANCE_STATUSES else 0

        new_amb_status = st.selectbox(
            "New Dispatch Status",
            options=AMBULANCE_STATUSES,
            index=curr_idx,
            key="amb_new_status_select"
        )

        if st.button("Apply Dispatch Update", key="btn_apply_amb_status", use_container_width=True):
            if new_amb_status == curr_status:
                st.warning(f"Request **{selected_amb_id}** is already **{curr_status}**.")
            else:
                ok = database.update_ambulance_status(selected_amb_id, new_amb_status)
                if ok:
                    st.success(f"Ambulance **{selected_amb_id}** status updated to **{new_amb_status}**!")
                    st.rerun()

    with col_right:
        st.markdown("#### 2. Link Request to Patient Record")
        st.caption("Assign an emergency request to an existing patient record post-stabilization.")

        all_patients = database.get_all_patients()
        if not all_patients:
            st.warning("No patients registered. Complete patient registration to enable record linking.")
        else:
            pat_options = {p.id: f"{p.id} — {p.name} ({p.phone})" for p in all_patients}
            selected_pat_id = st.selectbox(
                "Select Patient Record to Link",
                options=list(pat_options.keys()),
                format_func=lambda k: pat_options[k],
                key="amb_link_patient_select"
            )

            link_notes = st.text_input(
                "Post-Emergency Stabilization Notes",
                placeholder="e.g. Admitted to ER Ward B, unit 7 transport complete",
                key="amb_link_notes_input"
            )

            if st.button("Link Patient Record", key="btn_link_patient_record", use_container_width=True):
                ok = database.link_ambulance_to_patient(selected_amb_id, selected_pat_id, notes=link_notes)
                if ok:
                    st.success(f"Request **{selected_amb_id}** successfully linked to patient record **{selected_pat_id}**!")
                    st.rerun()

    # Detailed Inspector Card
    if selected_amb:
        with st.expander(f"Emergency Ticket Detail: {selected_amb.id}", expanded=True):
            linked_patient_info = "Unlinked (Pending Post-Emergency Assignment)"
            if selected_amb.patient_id:
                pat_obj = database.get_patient_by_id(selected_amb.patient_id)
                if pat_obj:
                    linked_patient_info = f"{pat_obj.name} ({pat_obj.id}) | Phone: {pat_obj.phone}"
                else:
                    linked_patient_info = selected_amb.patient_id

            urg_badge = render_urgency_badge(selected_amb.urgency_tag)
            stat_badge = render_status_badge(selected_amb.status)

            notes_section = f"""
            <div style="margin-top: 10px;">
                <div class="patient-label">Staff Dispatch / Stabilization Notes</div>
                <div class="patient-notes-box" style="background: #EFF6FF;">{selected_amb.notes}</div>
            </div>
            """ if selected_amb.notes else ""

            card_html = f"""
            <div class="patient-card" style="border-left: 4px solid #2563EB;">
                <div class="patient-card-header">
                    <span class="patient-card-title">Emergency Request Ticket</span>
                    <div>
                        <span class="patient-id-badge">{selected_amb.id}</span>
                        &nbsp;{urg_badge}
                        &nbsp;{stat_badge}
                    </div>
                </div>
                <div class="patient-grid">
                    <div>
                        <div class="patient-label">Requester Name</div>
                        <div class="patient-value">{selected_amb.requester_name}</div>
                    </div>
                    <div>
                        <div class="patient-label">Callback Phone</div>
                        <div class="patient-value">{selected_amb.phone}</div>
                    </div>
                    <div>
                        <div class="patient-label">Urgency Level</div>
                        <div class="patient-value">{selected_amb.urgency_tag}</div>
                    </div>
                    <div>
                        <div class="patient-label">Linked Patient Record</div>
                        <div class="patient-value">{linked_patient_info}</div>
                    </div>
                </div>
                <div style="margin-top: 10px;">
                    <div class="patient-label">Pickup Location</div>
                    <div class="patient-notes-box">{selected_amb.pickup_location}</div>
                </div>
                {notes_section}
            </div>
            """
            st.markdown(clean_html(card_html), unsafe_allow_html=True)

            # ── Single-request map (only if coordinates present) ───────────
            if selected_amb.latitude is not None and selected_amb.longitude is not None:
                st.markdown("**📍 Pickup Location Map**")
                _color = {"High": "red", "Medium": "orange"}.get(selected_amb.urgency_tag, "blue")
                _m = folium.Map(
                    location=[selected_amb.latitude, selected_amb.longitude],
                    zoom_start=15,
                    tiles="OpenStreetMap"
                )
                folium.Marker(
                    location=[selected_amb.latitude, selected_amb.longitude],
                    popup=folium.Popup(
                        f"<b>{selected_amb.id}</b><br>"
                        f"{selected_amb.requester_name}<br>"
                        f"{selected_amb.pickup_location}<br>"
                        f"Urgency: {selected_amb.urgency_tag} | Status: {selected_amb.status}",
                        max_width=260
                    ),
                    tooltip=f"{selected_amb.id} — {selected_amb.urgency_tag} ({selected_amb.status})",
                    icon=folium.Icon(color=_color, icon="info-sign")
                ).add_to(_m)
                st_folium(_m, width="100%", height=340, returned_objects=[], key=f"staff_map_{selected_amb.id}")
            else:
                st.caption(
                    "🗺️ No map available — this request was submitted without GPS coordinates "
                    "(manual address only)."
                )
            # ──────────────────────────────────────────────────────────────

    # ── Combined Live Dispatch Map (all active geolocated requests) ───────────
    st.divider()
    st.markdown("#### 🗺️ Live Dispatch Map — All Active Requests")
    st.caption("Shows all non-Resolved ambulance requests that have GPS coordinates. Red = High, Orange = Medium, Blue = Low urgency.")

    all_requests = database.get_all_ambulance_requests()
    mapped_requests = [
        r for r in all_requests
        if r.status != "Resolved" and r.latitude is not None and r.longitude is not None
    ]

    if not mapped_requests:
        st.info(
            "No active requests with GPS coordinates to display. "
            "Requests submitted with auto-detect location will appear here."
        )
    else:
        # Center map on average of all points
        avg_lat = sum(r.latitude for r in mapped_requests) / len(mapped_requests)
        avg_lon = sum(r.longitude for r in mapped_requests) / len(mapped_requests)

        dispatch_map = folium.Map(
            location=[avg_lat, avg_lon],
            zoom_start=13,
            tiles="OpenStreetMap"
        )

        _urgency_colors = {"High": "red", "Medium": "orange", "Low": "blue"}
        for req in mapped_requests:
            _mc = _urgency_colors.get(req.urgency_tag, "blue")
            folium.Marker(
                location=[req.latitude, req.longitude],
                popup=folium.Popup(
                    f"<b>{req.id}</b><br>"
                    f"{req.requester_name}<br>"
                    f"{req.pickup_location}<br>"
                    f"Urgency: {req.urgency_tag} | Status: {req.status}",
                    max_width=260
                ),
                tooltip=f"{req.id} — {req.urgency_tag} ({req.status})",
                icon=folium.Icon(color=_mc, icon="info-sign")
            ).add_to(dispatch_map)

        st_folium(dispatch_map, width="100%", height=420, returned_objects=[], key="staff_all_dispatch_map")

        st.caption(
            f"Showing **{len(mapped_requests)}** active request(s) on map · "
            f"{len(all_requests) - len(mapped_requests)} request(s) have no GPS data (manual address only)"
        )
