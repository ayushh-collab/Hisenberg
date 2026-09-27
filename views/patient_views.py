"""
Patient Portal Views
Handles patient registration, appointment booking, status reflection, emergency ambulance requests, and blood directory search.
Zero diagnostic / medical advice logic.
"""
import streamlit as st
from datetime import date, timedelta
import folium
from streamlit_folium import st_folium
from models import (
    Patient,
    Appointment,
    AmbulanceRequest,
    BloodRecord,
    VALID_BLOOD_GROUPS,
    VALID_GENDERS,
    ADMINISTRATIVE_REASONS,
    URGENCY_TAGS,
    BLOOD_RECORD_TYPES
)
import database
from styles import (
    render_patient_card,
    render_appointment_card,
    render_blood_record_card,
    render_ambulance_card,
    render_status_badge,
    render_urgency_badge,
    render_badge,
    clean_html,
    COLOR_CONFIRMED,
    COLOR_TEXT_MUTED,
    COLOR_DANGER,
)

def render_patient_portal():
    # ── 1. Top Section: Emergency Ambulance (Hero Priority) ───────────────────
    render_ambulance_request_section()

    st.markdown("<div style='margin-top: 32px; margin-bottom: 22px;'><hr style='border: none; border-top: 1px solid #E2E8F0; margin: 0;'></div>", unsafe_allow_html=True)

    # ── 2. Underneath: Scheduled Care & Healthcare Services ───────────────────
    st.markdown(
        """
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; margin-bottom: 14px;">
            <div>
                <h3 style="margin: 0; font-size: 1.25rem; font-weight: 700; color: #0F172A;">
                    Clinic Care & Healthcare Services
                </h3>
                <p style="margin: 3px 0 0 0; font-size: 0.85rem; color: #64748B;">
                    Scheduled administrative visits, patient registration, booking lookup, and regional blood bank availability.
                </p>
            </div>
            <div>
                <span class="mc-badge" style="background-color: #EFF6FF; color: #2563EB; font-weight: 600; padding: 4px 12px; border-radius: 6px; font-size: 0.78rem;">
                    Scheduled Operations Hub
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    tab_reg, tab_book, tab_status, tab_blood, tab_facilities = st.tabs([
        "👤 Register New Patient",
        "📅 Book Appointment",
        "🔍 Check Booking Status",
        "🩸 Regional Blood Directory",
        "🏥 Affiliated Facilities"
    ])

    with tab_reg:
        render_registration_section()

    with tab_book:
        render_appointment_booking_section()

    with tab_status:
        render_status_reflection_section()

    with tab_blood:
        render_blood_search_section()

    with tab_facilities:
        render_facility_directory()


def render_ambulance_request_section():
    st.markdown(
        """
        <div class="emergency-hero-box">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 8px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span class="emergency-pulse-dot"></span>
                    <span style="font-weight: 700; font-size: 1.15rem; color: #B91C1C; letter-spacing: -0.01em;">
                        Immediate Emergency Ambulance Dispatch
                    </span>
                </div>
                <span class="mc-badge" style="background-color: #FEF2F2; color: #B91C1C; font-weight: 600; border: 1px solid #FECACA; padding: 4px 10px; border-radius: 5px; font-size: 0.76rem;">
                    🚨 Priority Emergency Triage · 24/7 Desk
                </span>
            </div>
            <p style="font-size: 0.86rem; color: #475569; margin: 0; line-height: 1.45;">
                <strong>Zero Prior Registration Required.</strong> Enter requester name, callback phone, and pickup location to dispatch an emergency response team immediately. Patient linking is completed post-stabilization by hospital coordinators.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


    # ── Post-submission confirmation card ─────────────────────────────────────
    if "last_ambulance_request" in st.session_state and st.session_state["last_ambulance_request"]:
        last_amb = st.session_state["last_ambulance_request"]
        st.success(f"Ambulance Request **{last_amb.id}** submitted successfully! Response team notified.")

        st.markdown(render_ambulance_card(last_amb), unsafe_allow_html=True)

        # Map preview — only when coordinates were captured
        if last_amb.latitude is not None and last_amb.longitude is not None:
            st.markdown("**📍 Pickup Location Map Preview**")
            _urgency_color = {"High": "red", "Medium": "orange"}.get(last_amb.urgency_tag, "blue")
            _m = folium.Map(
                location=[last_amb.latitude, last_amb.longitude],
                zoom_start=15,
                tiles="OpenStreetMap"
            )
            folium.Marker(
                location=[last_amb.latitude, last_amb.longitude],
                popup=folium.Popup(
                    f"<b>{last_amb.id}</b><br>{last_amb.pickup_location}<br>"
                    f"Urgency: {last_amb.urgency_tag}",
                    max_width=220
                ),
                tooltip=f"{last_amb.id} — {last_amb.urgency_tag} Priority",
                icon=folium.Icon(color=_urgency_color, icon="info-sign")
            ).add_to(_m)
            st_folium(_m, width="100%", height=320, returned_objects=[])

        if st.button("Submit Another Emergency Request", key="btn_another_amb"):
            st.session_state["last_ambulance_request"] = None
            st.session_state.pop("amb_geo_lat", None)
            st.session_state.pop("amb_geo_lon", None)
            st.rerun()
        st.divider()

    # ── Geolocation auto-detect (fires on mount, no button needed) ───────────
    # Only call get_geolocation() when we don't already have cached coords —
    # this avoids re-prompting the browser on every Streamlit rerender.
    from streamlit_js_eval import get_geolocation

    cached_lat = st.session_state.get("amb_geo_lat")
    cached_lon = st.session_state.get("amb_geo_lon")

    if cached_lat is None or cached_lon is None:
        # Renders an invisible component that immediately requests browser location.
        # Returns dict with coords, or None if denied / unavailable.
        geo = get_geolocation()
        if geo and isinstance(geo, dict):
            coords = geo.get("coords") or {}
            raw_lat = coords.get("latitude")
            raw_lon = coords.get("longitude")
            if raw_lat is not None and raw_lon is not None:
                st.session_state["amb_geo_lat"] = float(raw_lat)
                st.session_state["amb_geo_lon"] = float(raw_lon)
                # Rerun once to reflect the detected location in the UI
                st.rerun()

    # Refresh after possible rerun
    cached_lat = st.session_state.get("amb_geo_lat")
    cached_lon = st.session_state.get("amb_geo_lon")

    if cached_lat is not None and cached_lon is not None:
        st.markdown(
            f"<p style='font-size:0.85rem; color:{COLOR_CONFIRMED}; margin-top:2px;'>"
            f"✅ <strong>Location detected:</strong> {cached_lat:.5f}, {cached_lon:.5f} &nbsp;·&nbsp; "
            f"GPS coordinates will be attached to your dispatch ticket automatically."
            f"</p>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<p style='font-size:0.82rem; color:{COLOR_TEXT_MUTED}; margin-top:2px;'>"
            "📍 Requesting location… If your browser asks for permission, click <strong>Allow</strong>. "
            "If denied or unavailable, your text address will be used alone — that is always sufficient."
            "</p>",
            unsafe_allow_html=True
        )

    st.markdown(
        """
        <style>
        form[aria-label="ambulance_request_form"] {
            border: 1px solid #FECACA !important;
            border-radius: 10px !important;
            background: #FFFFFF !important;
            box-shadow: 0 4px 16px -2px rgba(239, 68, 68, 0.07), 0 2px 4px -1px rgba(0, 0, 0, 0.02) !important;
            padding: 22px !important;
        }
        form[aria-label="ambulance_request_form"] .stFormSubmitButton > button {
            background: linear-gradient(135deg, #DC2626 0%, #991B1B 100%) !important;
            box-shadow: 0 4px 14px rgba(220, 38, 38, 0.35) !important;
            color: #FFFFFF !important;
            font-size: 0.95rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.02em !important;
            border: none !important;
        }
        form[aria-label="ambulance_request_form"] .stFormSubmitButton > button:hover {
            background: linear-gradient(135deg, #EF4444 0%, #B91C1C 100%) !important;
            box-shadow: 0 6px 18px rgba(220, 38, 38, 0.5) !important;
            transform: translateY(-1px);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # ── Request form ─────────────────────────────────────────────────────────
    with st.form("ambulance_request_form", clear_on_submit=False):

        col1, col2 = st.columns(2)
        with col1:
            req_name = st.text_input(
                "Requester Full Name *",
                placeholder="e.g. Daniel Carter",
                help="Name of caller or contact person."
            )
            phone = st.text_input(
                "Callback Phone Number *",
                placeholder="e.g. +1 555-0301",
                help="Direct line for ambulance crew callback."
            )
        with col2:
            urgency = st.selectbox(
                "Urgency Level *",
                options=URGENCY_TAGS,
                index=0,
                help="High = Severe/Unconscious, Medium = Urgent/Injury, Low = Transport/Non-critical."
            )
            pickup_location = st.text_input(
                "Pickup Location / Street Landmark *",
                placeholder="e.g. Corner of 5th Ave & Pine St, near Pharmacy",
                help="Detailed location or landmark for fast driver navigation."
            )

        notes = st.text_area(
            "Optional Pickup Notes / Room Number",
            placeholder="e.g. 3rd floor, Apt 3B, Gate Code 1234",
            help="Landmark details only. No clinical self-diagnosis required."
        )

        submit_amb = st.form_submit_button("🚨 DISPATCH AMBULANCE IMMEDIATELY", use_container_width=True)

    if submit_amb:
        is_valid, err_msg = AmbulanceRequest.validate(
            name=req_name,
            phone=phone,
            pickup_location=pickup_location,
            urgency_tag=urgency
        )
        if not is_valid:
            st.error(err_msg)
        else:
            fin_lat = st.session_state.get("amb_geo_lat")
            fin_lon = st.session_state.get("amb_geo_lon")
            fin_source = "Auto" if (fin_lat is not None and fin_lon is not None) else "Manual"

            amb_req = database.create_ambulance_request(
                requester_name=req_name,
                phone=phone,
                pickup_location=pickup_location,
                urgency_tag=urgency,
                notes=notes,
                latitude=fin_lat,
                longitude=fin_lon,
                location_source=fin_source
            )
            st.session_state["last_ambulance_request"] = amb_req
            st.toast(f"Ambulance Request {amb_req.id} Dispatched!", icon="🚨")
            st.rerun()

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    with st.expander("🔒 Clinic Staff & Administrator Access", expanded=False):
        st.caption("Are you authorized hospital or triage staff? Enter your staff access key to switch to the internal Clinic Staff Portal.")
        c_key, c_act = st.columns([3, 1])
        with c_key:
            inline_key = st.text_input("Staff Access Key", type="password", key="inline_staff_key", placeholder="e.g. admin")
        with c_act:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Open Staff Portal", key="btn_inline_staff_submit", use_container_width=True):
                if inline_key.strip().lower() in ["admin", "staff", "1234", "mediconnect"]:
                    st.session_state["is_admin"] = True
                    st.toast("Authenticated as Clinic Staff", icon="🔒")
                    st.rerun()
                else:
                    st.error("Invalid key. Use 'admin' for demo.")







def render_registration_section():
    st.subheader("Patient Registration")
    st.caption("Create a new patient record to receive an official Patient ID.")

    if "last_registered_patient" in st.session_state and st.session_state["last_registered_patient"] is not None:
        last_patient = st.session_state["last_registered_patient"]
        st.success(f"Registration confirmed for **{last_patient.name}**. Official Patient ID: **{last_patient.id}**")
        st.markdown(render_patient_card(last_patient), unsafe_allow_html=True)
        
        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            if st.button("Register Another Patient", key="btn_register_another"):
                st.session_state["last_registered_patient"] = None
                st.rerun()
        st.divider()
        return

    with st.form("patient_registration_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("Full Name *", placeholder="e.g. John Doe", help="Required. Legal full name.")
            dob = st.date_input(
                "Date of Birth *",
                value=date(1995, 1, 1),
                min_value=date(1900, 1, 1),
                max_value=date.today(),
                help="Required. Used for identification and demographic records."
            )
            gender = st.selectbox("Gender *", options=VALID_GENDERS, index=0)
            
        with col2:
            phone = st.text_input(
                "Contact Phone Number *",
                placeholder="e.g. +1 555-0199 or 9876543210",
                help="Required. Primary telephone number for clinic notifications."
            )
            blood_group = st.selectbox(
                "Blood Group *",
                options=VALID_BLOOD_GROUPS,
                index=0,
                help="Required administrative record. Select 'Unknown' if not verified."
            )
            address = st.text_input(
                "Residential Address",
                placeholder="e.g. 742 Evergreen Terrace, Springfield",
                help="Optional street address or municipality."
            )
            
        notes = st.text_area(
            "Administrative Notes",
            placeholder="e.g. Preferred language (Spanish), wheelchair accessibility required, secondary contact person.",
            help="Non-clinical administrative remarks only."
        )
        
        st.markdown(
            f"<small style='color:{COLOR_TEXT_MUTED};'>* Required administrative field.</small>",
            unsafe_allow_html=True
        )

        submit_btn = st.form_submit_button("Complete Registration", use_container_width=True)

    if submit_btn:
        is_valid, err_msg = Patient.validate(
            name=full_name,
            dob=dob,
            gender=gender,
            phone=phone,
            blood_group=blood_group,
            address=address,
            notes=notes
        )
        
        if not is_valid:
            st.error(err_msg)
        else:
            created = database.create_patient(
                name=full_name,
                dob=dob.strftime("%Y-%m-%d"),
                gender=gender,
                phone=phone,
                blood_group=blood_group,
                address=address,
                notes=notes
            )
            st.session_state["last_registered_patient"] = created
            st.toast(f"Patient {created.id} registered successfully!", icon="✅")
            st.rerun()


def render_appointment_booking_section():
    st.subheader("Book Clinic Appointment")
    st.caption("Schedule an in-person administrative visit or consultation slot.")

    all_patients = database.get_all_patients()
    if not all_patients:
        st.info("No registered patients found. Please complete **Patient Registration** in the first tab to obtain a Patient ID before booking an appointment.")
        return

    st.markdown("##### 1. Select Patient Profile")
    default_index = 0
    if "last_registered_patient" in st.session_state and st.session_state["last_registered_patient"]:
        last_id = st.session_state["last_registered_patient"].id
        for idx, p in enumerate(all_patients):
            if p.id == last_id:
                default_index = idx
                break

    patient_options = {p.id: f"{p.id} — {p.name} ({p.phone})" for p in all_patients}
    selected_patient_id = st.selectbox(
        "Select your registered profile *",
        options=list(patient_options.keys()),
        index=default_index,
        format_func=lambda pid: patient_options[pid],
        key="booking_patient_selector"
    )

    selected_patient = next((p for p in all_patients if p.id == selected_patient_id), None)
    if selected_patient:
        st.caption(f"Booking appointment for: **{selected_patient.name}** | Phone: {selected_patient.phone} | Blood Group: {selected_patient.blood_group}")

    st.markdown("##### 2. Appointment Details")
    with st.form("appointment_booking_form"):
        col_date, col_time = st.columns(2)
        with col_date:
            min_booking_date = date.today()
            max_booking_date = date.today() + timedelta(days=60)
            appt_date = st.date_input(
                "Appointment Date *",
                value=date.today() + timedelta(days=1),
                min_value=min_booking_date,
                max_value=max_booking_date,
                help="Appointments can be booked up to 60 days in advance."
            )
        with col_time:
            time_slots = [
                "09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM",
                "11:00 AM", "11:30 AM", "01:30 PM", "02:00 PM",
                "02:30 PM", "03:00 PM", "03:30 PM", "04:00 PM", "04:30 PM"
            ]
            appt_time = st.selectbox("Preferred Time Slot *", options=time_slots, index=2)

        category = st.selectbox(
            "Visit Category *",
            options=ADMINISTRATIVE_REASONS,
            help="Administrative category for visit coordination."
        )

        specific_reason = st.text_input(
            "Visit Purpose / Free-Text Remarks *",
            placeholder="e.g. Annual routine physical checkup, employment medical documentation, prescription follow-up",
            help="Administrative purpose only. Zero diagnostic or symptom descriptions."
        )

        st.markdown(
            f"<small style='color:{COLOR_TEXT_MUTED};'>Administrative notice: Visit reason is used exclusively for scheduling and room assignment.</small>",
            unsafe_allow_html=True
        )


        book_btn = st.form_submit_button("Confirm & Book Appointment", use_container_width=True)

    if book_btn:
        combined_reason = f"{category}: {specific_reason.strip()}" if specific_reason.strip() else category
        
        is_valid, err_msg = Appointment.validate(
            patient_id=selected_patient_id,
            appt_date=appt_date,
            appt_time=appt_time,
            reason=combined_reason
        )

        if not is_valid:
            st.error(err_msg)
        else:
            new_apt = database.create_appointment(
                patient_id=selected_patient_id,
                date_str=appt_date.strftime("%Y-%m-%d"),
                time_str=appt_time,
                reason=combined_reason
            )
            st.session_state["latest_booked_appointment"] = new_apt
            st.toast(f"Appointment {new_apt.id} successfully booked!", icon="✅")
            st.rerun()

    if "latest_booked_appointment" in st.session_state and st.session_state["latest_booked_appointment"]:
        latest_apt = st.session_state["latest_booked_appointment"]
        if latest_apt.patient_id == selected_patient_id:
            st.markdown("#### Confirmed Booking Card")
            st.markdown(render_appointment_card(latest_apt, selected_patient.name), unsafe_allow_html=True)


def render_status_reflection_section():
    st.subheader("Appointment Status Lookup")
    st.caption("Check live status updates for your scheduled appointments.")

    all_patients = database.get_all_patients()
    if not all_patients:
        st.info("No patient records exist yet.")
        return

    patient_options = {p.id: f"{p.id} — {p.name} ({p.phone})" for p in all_patients}
    selected_pid = st.selectbox(
        "Select Patient Profile to View Booking Status:",
        options=list(patient_options.keys()),
        format_func=lambda pid: patient_options[pid],
        key="status_lookup_patient_selector"
    )

    if selected_pid:
        patient = database.get_patient_by_id(selected_pid)
        apts = database.get_appointments_by_patient(selected_pid)

        if not apts:
            st.warning(f"No appointment bookings found for **{patient.name}** ({patient.id}). Switch to the **Book Appointment** tab to schedule a visit.")
        else:
            st.markdown(f"**Found {len(apts)} appointment(s) for {patient.name}:**")
            for apt in apts:
                st.markdown(render_appointment_card(apt, patient.name), unsafe_allow_html=True)


def render_blood_search_section():
    """Feature 8: Patient-facing Blood Group & Location Search."""
    st.subheader("🩸 Regional Blood Group Directory & Search")
    st.caption("Search available blood bank stock and open hospital requirements by blood group and location.")

    c_group, c_type, c_loc = st.columns([1, 1, 2])
    with c_group:
        group_filter = st.selectbox(
            "Blood Group",
            options=["All"] + [g for g in VALID_BLOOD_GROUPS if g != "Unknown"],
            index=0,
            key="blood_search_group"
        )
    with c_type:
        type_filter = st.selectbox(
            "Listing Type",
            options=["All", "Available", "Requested"],
            index=0,
            key="blood_search_type"
        )
    with c_loc:
        location_query = st.text_input(
            "Search Facility or City Location",
            placeholder="e.g. Springfield, Metroville, General Hospital...",
            key="blood_search_loc"
        )

    records = database.search_blood_records(
        blood_group=group_filter,
        location_query=location_query,
        record_type=type_filter,
        status_filter="Open"
    )

    st.markdown(f"**Found {len(records)} active listing(s)**" + (f" for group '{group_filter}'" if group_filter != "All" else ""))

    if not records:
        st.info("No active blood stock or requirement listings match your search criteria.")
        return

    for bld in records:
        st.markdown(render_blood_record_card(bld), unsafe_allow_html=True)


def render_facility_directory():
    """Affiliated facility directory — card list for patients."""
    from styles import COLOR_ACCENT, COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_SURFACE, COLOR_BORDER, RADIUS_CARD, BAR_WIDTH, clean_html

    st.markdown(
        """
        <div style="margin-bottom: 18px;">
            <h4 style="margin: 0 0 4px 0; font-size: 1.05rem; font-weight: 700; color: #0F172A;">
                Affiliated Clinics &amp; Healthcare Facilities
            </h4>
            <p style="margin: 0; font-size: 0.84rem; color: #64748B; line-height: 1.5;">
                Locations, contact numbers, and services offered by MediConnect-affiliated facilities.
                Walk-in availability varies — confirm by phone before visiting.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    facilities = database.get_all_facilities()
    if not facilities:
        st.info("No affiliated facilities are currently listed.")
        return

    for fac in facilities:
        # Build specialization tags
        spec_tags = "".join(
            f'<span style="display:inline-block; background:{COLOR_ACCENT}14; color:{COLOR_ACCENT}; '
            f'font-size:0.73rem; font-weight:600; padding:2px 9px; border-radius:4px; margin:2px 4px 2px 0;">'
            f'{s.strip()}</span>'
            for s in fac.specializations.split("·")
            if s.strip()
        )

        card_html = f"""
<div style="display:flex; background:{COLOR_SURFACE}; border:1px solid {COLOR_BORDER};
     border-radius:{RADIUS_CARD}; overflow:hidden; margin-bottom:12px;
     box-shadow:0 1px 4px rgba(0,0,0,0.05);">
  <div style="width:{BAR_WIDTH}; min-width:{BAR_WIDTH}; background:{COLOR_ACCENT}; flex-shrink:0;"></div>
  <div style="padding:14px 18px; flex:1; min-width:0;">
    <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:6px; margin-bottom:8px;">
      <div>
        <div style="font-size:1rem; font-weight:700; color:{COLOR_TEXT}; margin-bottom:1px;">{fac.name}</div>
        <div style="font-size:0.8rem; color:{COLOR_TEXT_MUTED};">{fac.id}</div>
      </div>
      <span style="font-size:0.75rem; font-weight:600; color:{COLOR_ACCENT};
            background:{COLOR_ACCENT}14; padding:3px 10px; border-radius:4px; white-space:nowrap;">
        Affiliated Facility
      </span>
    </div>

    <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px 24px; margin-bottom:10px;">
      <div>
        <span style="font-size:0.72rem; font-weight:600; color:{COLOR_TEXT_MUTED}; text-transform:uppercase; letter-spacing:0.04em;">Address</span>
        <div style="font-size:0.84rem; color:{COLOR_TEXT}; margin-top:1px;">{fac.address}</div>
      </div>
      <div>
        <span style="font-size:0.72rem; font-weight:600; color:{COLOR_TEXT_MUTED}; text-transform:uppercase; letter-spacing:0.04em;">Phone</span>
        <div style="font-size:0.84rem; color:{COLOR_TEXT}; margin-top:1px; font-weight:600;">{fac.phone}</div>
      </div>
      <div style="grid-column:1/-1;">
        <span style="font-size:0.72rem; font-weight:600; color:{COLOR_TEXT_MUTED}; text-transform:uppercase; letter-spacing:0.04em;">Operating Hours</span>
        <div style="font-size:0.83rem; color:{COLOR_TEXT}; margin-top:1px;">{fac.operating_hours}</div>
      </div>
    </div>

    <div>
      <span style="font-size:0.72rem; font-weight:600; color:{COLOR_TEXT_MUTED}; text-transform:uppercase; letter-spacing:0.04em;">Services Offered</span>
      <div style="margin-top:5px;">{spec_tags}</div>
    </div>
  </div>
</div>
"""
        st.markdown(clean_html(card_html), unsafe_allow_html=True)
