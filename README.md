# MediConnect — Healthcare Administration & Coordination Platform

An administrative and operational coordination platform for clinics, patients, emergency ambulance dispatch, and blood stock management.

> **Scope Fence Note:** MediConnect is strictly an administrative management system. It contains zero diagnosis logic, symptom checkers, treatment suggestions, or medical advice.

---

## 🚀 Quick Start

### 1. Launch the Application
```powershell
.\.venv\Scripts\streamlit run app.py
```
Or run with `run.bat`.

---

## 📋 Feature Progress Tracker

### Tier 1 — Core Demo Path
- [x] **Feature 1: Patient Registration** (Patient side: input validation, auto-generated Patient ID, persistent SQLite storage, patient card view)
- [x] **Feature 2: Patient Search & Directory** (Staff side: scannable table, filter/search by Name / Phone / ID, detail card view)
- [x] **Feature 3: Appointment Booking** (Patient side: select profile, date/time slot, administrative visit reason)
- [x] **Feature 4: Appointment Scheduling View** (Staff side: upcoming schedule list, date/status filtering, inline status update)
- [x] **Feature 5: Appointment Status Reflection** (Patient side: live status badge lookup and booking history reflection)
- [x] **Feature 6: Frictionless Ambulance Request** (Patient side: minimal 4-field emergency form, zero pre-registration needed, instant submission)
- [x] **Feature 7: Ambulance Request Management & Linking** (Staff side: urgent queue, dispatch status updates, post-stabilization patient linking)

### Tier 2 — Strong Differentiators
- [x] **Feature 8: Blood Group Search** (Patient side: search available/requested blood by group + location)
- [ ] **Feature 9: Blood Bank Stock Management** (Staff side: add/update units and donor/request listings)
- [ ] **Feature 10: Ambulance Fleet Availability** (Staff side: status tracking per ambulance unit)
- [ ] **Feature 11: Clinic Administrative Dashboard** (Staff side: high-level metrics — today's appointments, active ambulance dispatches, blood request tallies)

### Tier 3 — Nice to Have / Polish
- [x] **Feature A (13): Patient Visit History** (Staff side: historical appointment records integrated into Patient Record Inspector with status wayfinding)
- [x] **Feature B (12): Follow-up Reminders** (Staff side: configurable N-day overdue worklist for completed appointments with no subsequent bookings)
- [ ] **Feature C (14): Facility Directory**
- [ ] **Feature D (15): Unified Emergency Queue**
- [ ] **Feature E (16): Administrative Summary Statistics**



---

## 📂 Architecture
- `app.py`: Top-level role router (Patient vs. Clinic Staff)
- `database.py`: SQLite persistence layer (`mediconnect.db`)
- `models.py`: Administrative data models & field validation
- `styles.py`: Clean administrative UI styling, badge helpers, patient card components
- `views/`:
  - `views/patient_views.py`: Patient portal flows
  - `views/staff_views.py`: Clinic staff management flows
