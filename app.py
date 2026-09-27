"""
MediConnect — Healthcare Management & Coordination Platform
Strictly administrative & operational platform. Zero clinical or diagnostic decision logic.
"""
import streamlit as st
import database
from styles import CUSTOM_CSS, COLOR_TEXT_MUTED
from views.patient_views import render_patient_portal
from views.staff_views import render_staff_portal

# Ensure database tables and demo seed data exist
database.init_db()
database.seed_demo_data()

# Streamlit Page Setup
st.set_page_config(
    page_title="MediConnect | Healthcare Coordination",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Inject Custom Administrative Styles & Ambient Theme
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Session state initialization: default is Patient View
if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False

# Top Brand Header with Ambient Styling & Staff Access Gateway
col_brand, col_auth = st.columns([3, 1])

with col_brand:
    st.markdown(
        """
        <div style="padding: 6px 0 12px 0;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <h1 style="font-size: 1.5rem; font-weight: 700; color: #0F172A; margin: 0; letter-spacing: -0.02em;">
                    MediConnect
                </h1>
                <span style="font-size: 0.72rem; font-weight: 600; background-color: #EFF6FF; color: #2563EB; padding: 2px 8px; border-radius: 4px; border: 1px solid #BFDBFE;">
                    COORDINATION PLATFORM
                </span>
            </div>
            <p style="font-size: 0.85rem; color: #64748B; margin: 3px 0 0 0;">
                Healthcare Operations, Emergency Dispatch &amp; Patient Administration
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_auth:
    st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
    if st.session_state["is_admin"]:
        c_badge, c_btn = st.columns([1, 1])
        with c_badge:
            st.markdown(
                "<div style='padding-top: 8px; text-align: right;'>"
                "<span style='font-size: 0.76rem; font-weight: 600; background: #DCFCE7; color: #166534; padding: 4px 8px; border-radius: 4px;'>Staff Active</span>"
                "</div>",
                unsafe_allow_html=True
            )
        with c_btn:
            if st.button("Exit Staff Mode", key="btn_exit_staff", use_container_width=True):
                st.session_state["is_admin"] = False
                st.rerun()
    else:
        with st.popover("🔒 Staff / Admin Login", use_container_width=True):
            st.markdown("##### Clinic Staff Authentication")
            st.caption("Restricted to authorized clinic & dispatch coordination staff.")
            access_key = st.text_input(
                "Access Key / Password",
                type="password",
                placeholder="Enter access key (default: admin)",
                key="top_admin_key"
            )
            if st.button("Login to Staff Portal", key="btn_top_admin_login", use_container_width=True):
                if access_key.strip().lower() in ["admin", "staff", "1234", "mediconnect"]:
                    st.session_state["is_admin"] = True
                    st.toast("Authenticated as Clinic Staff", icon="🔒")
                    st.rerun()
                else:
                    st.error("Invalid access key. Use 'admin' for hackathon evaluation.")

st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

# Portal Dispatcher: Default is Patient View
if st.session_state["is_admin"]:
    render_staff_portal()
else:
    render_patient_portal()
