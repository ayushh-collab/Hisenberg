"""
MediConnect SQLite Database Layer
Persistent storage for administrative healthcare records.
"""
import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from models import Patient, Appointment, AmbulanceRequest, BloodRecord, Facility

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mediconnect.db")


def init_db():
    """Initialize database tables if they do not exist."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                dob TEXT NOT NULL,
                gender TEXT NOT NULL,
                phone TEXT NOT NULL,
                blood_group TEXT NOT NULL,
                address TEXT,
                notes TEXT,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_patients_phone ON patients(phone)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_patients_name ON patients(name)")

        conn.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                reason TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Scheduled',
                created_at TEXT NOT NULL,
                FOREIGN KEY (patient_id) REFERENCES patients(id)
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_appointments_patient ON appointments(patient_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status)")

        conn.execute("""
            CREATE TABLE IF NOT EXISTS ambulance_requests (
                id TEXT PRIMARY KEY,
                requester_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                pickup_location TEXT NOT NULL,
                urgency_tag TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending',
                patient_id TEXT,
                notes TEXT,
                latitude REAL,
                longitude REAL,
                location_source TEXT NOT NULL DEFAULT 'Manual',
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_amb_status ON ambulance_requests(status)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_amb_patient ON ambulance_requests(patient_id)")

        # Migration: add columns to existing ambulance_requests tables that predate this schema
        existing_cols = {row[1] for row in conn.execute("PRAGMA table_info(ambulance_requests)")}
        if "latitude" not in existing_cols:
            conn.execute("ALTER TABLE ambulance_requests ADD COLUMN latitude REAL")
        if "longitude" not in existing_cols:
            conn.execute("ALTER TABLE ambulance_requests ADD COLUMN longitude REAL")
        if "location_source" not in existing_cols:
            conn.execute("ALTER TABLE ambulance_requests ADD COLUMN location_source TEXT NOT NULL DEFAULT 'Manual'")

        conn.execute("""
            CREATE TABLE IF NOT EXISTS blood_records (
                id TEXT PRIMARY KEY,
                blood_group TEXT NOT NULL,
                location TEXT NOT NULL,
                type TEXT NOT NULL,
                units INTEGER NOT NULL,
                contact_info TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Open',
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_blood_group ON blood_records(blood_group)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_blood_location ON blood_records(location)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_blood_type ON blood_records(type)")

        conn.execute("""
            CREATE TABLE IF NOT EXISTS facilities (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                phone TEXT NOT NULL,
                specializations TEXT NOT NULL,
                operating_hours TEXT NOT NULL
            )
        """)
    conn.close()


def get_connection() -> sqlite3.Connection:
    """Return an active SQLite connection, guaranteeing schema existence."""
    init_db()
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def generate_patient_id() -> str:
    """Generate next formatted Patient ID like PAT-1001."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM patients ORDER BY rowid DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    
    if not row or not row["id"]:
        return "PAT-1001"
    
    last_id = row["id"]
    try:
        if last_id.startswith("PAT-"):
            num = int(last_id.split("-")[1])
            return f"PAT-{num + 1}"
    except (IndexError, ValueError):
        pass
    
    # Fallback based on total count
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM patients")
    count = cursor.fetchone()["count"]
    conn.close()
    return f"PAT-{1001 + count}"

def create_patient(
    name: str,
    dob: str,
    gender: str,
    phone: str,
    blood_group: str,
    address: str = "",
    notes: str = ""
) -> Patient:
    """Insert a new patient and return the Patient object."""
    patient_id = generate_patient_id()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = get_connection()
    with conn:
        conn.execute("""
            INSERT INTO patients (id, name, dob, gender, phone, blood_group, address, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (patient_id, name.strip(), dob, gender, phone.strip(), blood_group, address.strip(), notes.strip(), created_at))
    conn.close()
    
    return Patient(
        id=patient_id,
        name=name.strip(),
        dob=dob,
        gender=gender,
        phone=phone.strip(),
        blood_group=blood_group,
        address=address.strip(),
        notes=notes.strip(),
        created_at=created_at
    )

def get_patient_by_id(patient_id: str) -> Optional[Patient]:
    """Retrieve a single patient by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id.strip(),))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return Patient(
        id=row["id"],
        name=row["name"],
        dob=row["dob"],
        gender=row["gender"],
        phone=row["phone"],
        blood_group=row["blood_group"],
        address=row["address"] or "",
        notes=row["notes"] or "",
        created_at=row["created_at"]
    )

def get_all_patients() -> List[Patient]:
    """Retrieve all registered patients ordered by creation date descending."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [
        Patient(
            id=r["id"],
            name=r["name"],
            dob=r["dob"],
            gender=r["gender"],
            phone=r["phone"],
            blood_group=r["blood_group"],
            address=r["address"] or "",
            notes=r["notes"] or "",
            created_at=r["created_at"]
        )
        for r in rows
    ]

def count_patients() -> int:
    """Return total count of registered patients."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM patients")
    count = cursor.fetchone()["count"]
    conn.close()
    return count

def search_patients(query: str = "") -> List[Patient]:
    """Search patients by ID, Name, or Phone (case-insensitive substring match)."""
    clean_query = query.strip()
    conn = get_connection()
    cursor = conn.cursor()
    
    if not clean_query:
        cursor.execute("SELECT * FROM patients ORDER BY created_at DESC")
    else:
        search_pattern = f"%{clean_query}%"
        cursor.execute("""
            SELECT * FROM patients 
            WHERE id LIKE ? OR name LIKE ? OR phone LIKE ?
            ORDER BY created_at DESC
        """, (search_pattern, search_pattern, search_pattern))
    
    rows = cursor.fetchall()
    conn.close()
    return [
        Patient(
            id=r["id"],
            name=r["name"],
            dob=r["dob"],
            gender=r["gender"],
            phone=r["phone"],
            blood_group=r["blood_group"],
            address=r["address"] or "",
            notes=r["notes"] or "",
            created_at=r["created_at"]
        )
        for r in rows
    ]

def generate_appointment_id() -> str:
    """Generate next formatted Appointment ID like APT-1001."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM appointments ORDER BY rowid DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    
    if not row or not row["id"]:
        return "APT-1001"
    
    last_id = row["id"]
    try:
        if last_id.startswith("APT-"):
            num = int(last_id.split("-")[1])
            return f"APT-{num + 1}"
    except (IndexError, ValueError):
        pass
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM appointments")
    count = cursor.fetchone()["count"]
    conn.close()
    return f"APT-{1001 + count}"

def create_appointment(patient_id: str, date_str: str, time_str: str, reason: str) -> Appointment:
    """Insert a new appointment record."""
    apt_id = generate_appointment_id()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = get_connection()
    with conn:
        conn.execute("""
            INSERT INTO appointments (id, patient_id, date, time, reason, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'Scheduled', ?)
        """, (apt_id, patient_id.strip(), date_str.strip(), time_str.strip(), reason.strip(), created_at))
    conn.close()
    
    return Appointment(
        id=apt_id,
        patient_id=patient_id.strip(),
        date=date_str.strip(),
        time=time_str.strip(),
        reason=reason.strip(),
        status="Scheduled",
        created_at=created_at
    )

def get_appointment_by_id(apt_id: str) -> Optional[Appointment]:
    """Retrieve an appointment by its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments WHERE id = ?", (apt_id.strip(),))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return Appointment(
        id=row["id"],
        patient_id=row["patient_id"],
        date=row["date"],
        time=row["time"],
        reason=row["reason"],
        status=row["status"],
        created_at=row["created_at"]
    )

def get_appointments_by_patient(patient_id: str) -> List[Appointment]:
    """Retrieve all appointments for a given patient, ordered by date and time."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM appointments 
        WHERE patient_id = ? 
        ORDER BY date DESC, time DESC
    """, (patient_id.strip(),))
    rows = cursor.fetchall()
    conn.close()
    return [
        Appointment(
            id=r["id"],
            patient_id=r["patient_id"],
            date=r["date"],
            time=r["time"],
            reason=r["reason"],
            status=r["status"],
            created_at=r["created_at"]
        )
        for r in rows
    ]

def get_all_appointments() -> List[Appointment]:
    """Retrieve all appointments ordered by date and time."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments ORDER BY date ASC, time ASC")
    rows = cursor.fetchall()
    conn.close()
    return [
        Appointment(
            id=r["id"],
            patient_id=r["patient_id"],
            date=r["date"],
            time=r["time"],
            reason=r["reason"],
            status=r["status"],
            created_at=r["created_at"]
        )
        for r in rows
    ]

def get_appointments_with_patient_details(
    date_filter: str = "All",
    status_filter: str = "All"
) -> List[dict]:
    """
    Return appointments joined with patient details.
    date_filter: 'All' | 'Today' | 'Tomorrow' | 'Upcoming' | 'Past'
    status_filter: 'All' | specific status string
    Returns list of dicts with appointment + patient fields.
    """
    from datetime import date as date_cls
    today = date_cls.today().strftime("%Y-%m-%d")
    tomorrow = (date_cls.today() + __import__("datetime").timedelta(days=1)).strftime("%Y-%m-%d")

    conn = get_connection()
    cursor = conn.cursor()

    sql = """
        SELECT
            a.id as apt_id,
            a.patient_id,
            a.date,
            a.time,
            a.reason,
            a.status,
            a.created_at as apt_created_at,
            p.name as patient_name,
            p.phone as patient_phone,
            p.blood_group
        FROM appointments a
        LEFT JOIN patients p ON a.patient_id = p.id
        WHERE 1=1
    """
    params = []

    if date_filter == "Today":
        sql += " AND a.date = ?"
        params.append(today)
    elif date_filter == "Tomorrow":
        sql += " AND a.date = ?"
        params.append(tomorrow)
    elif date_filter == "Upcoming":
        sql += " AND a.date >= ?"
        params.append(today)
    elif date_filter == "Past":
        sql += " AND a.date < ?"
        params.append(today)

    if status_filter != "All":
        sql += " AND a.status = ?"
        params.append(status_filter)

    sql += " ORDER BY a.date ASC, a.time ASC"

    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_appointment_status(apt_id: str, new_status: str) -> bool:
    """Update a single appointment's status. Returns True on success."""
    conn = get_connection()
    try:
        with conn:
            conn.execute(
                "UPDATE appointments SET status = ? WHERE id = ?",
                (new_status, apt_id.strip())
            )
        return True
    except Exception:
        return False
    finally:
        conn.close()

def get_patients_due_for_followup(days_threshold: int = 30) -> List[dict]:
    """
    Return list of patients whose completed appointment was >= days_threshold days ago
    and who have no subsequent appointments (scheduled or completed) booked since.
    """
    from datetime import date as date_cls, datetime as dt_cls, timedelta
    today = date_cls.today()
    cutoff_date = (today - timedelta(days=days_threshold)).strftime("%Y-%m-%d")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            a.id as completed_apt_id,
            a.patient_id,
            a.date as completed_date,
            a.time as completed_time,
            a.reason,
            p.name as patient_name,
            p.phone as patient_phone,
            p.blood_group
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        WHERE a.status = 'Completed'
          AND a.date <= ?
        ORDER BY a.date ASC
    """, (cutoff_date,))
    rows = cursor.fetchall()

    results = []
    for r in rows:
        pid = r["patient_id"]
        c_date = r["completed_date"]

        # Check if patient has any appointment with date > c_date
        cursor.execute("""
            SELECT COUNT(*) as cnt
            FROM appointments
            WHERE patient_id = ?
              AND date > ?
        """, (pid, c_date))
        has_subsequent = cursor.fetchone()["cnt"] > 0

        if not has_subsequent:
            try:
                comp_dt = dt_cls.strptime(c_date, "%Y-%m-%d").date()
                days_elapsed = (today - comp_dt).days
            except Exception:
                days_elapsed = days_threshold

            results.append({
                "patient_id": pid,
                "patient_name": r["patient_name"],
                "patient_phone": r["patient_phone"],
                "blood_group": r["blood_group"],
                "completed_apt_id": r["completed_apt_id"],
                "completed_date": c_date,
                "completed_time": r["completed_time"],
                "reason": r["reason"],
                "days_elapsed": days_elapsed
            })

    conn.close()
    # Sort by days elapsed descending (most overdue first)
    results.sort(key=lambda x: x["days_elapsed"], reverse=True)
    return results

# ─── Ambulance Request functions ────────────────────────────────────────────


def _row_to_ambulance(r) -> AmbulanceRequest:
    return AmbulanceRequest(
        id=r["id"],
        requester_name=r["requester_name"],
        phone=r["phone"],
        pickup_location=r["pickup_location"],
        urgency_tag=r["urgency_tag"],
        status=r["status"],
        patient_id=r["patient_id"],
        notes=r["notes"] or "",
        latitude=r["latitude"],
        longitude=r["longitude"],
        location_source=r["location_source"] or "Manual",
        created_at=r["created_at"]
    )

def generate_ambulance_id() -> str:
    """Generate next formatted Ambulance Request ID like AMB-1001."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM ambulance_requests ORDER BY rowid DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if not row or not row["id"]:
        return "AMB-1001"
    try:
        if row["id"].startswith("AMB-"):
            num = int(row["id"].split("-")[1])
            return f"AMB-{num + 1}"
    except (IndexError, ValueError):
        pass
    conn2 = get_connection()
    c2 = conn2.cursor()
    c2.execute("SELECT COUNT(*) as cnt FROM ambulance_requests")
    cnt = c2.fetchone()["cnt"]
    conn2.close()
    return f"AMB-{1001 + cnt}"

def create_ambulance_request(
    requester_name: str,
    phone: str,
    pickup_location: str,
    urgency_tag: str,
    patient_id: str = None,
    notes: str = "",
    latitude: float = None,
    longitude: float = None,
    location_source: str = "Manual"
) -> AmbulanceRequest:
    """Insert a new ambulance request. patient_id and coordinates are nullable."""
    amb_id = generate_ambulance_id()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    with conn:
        conn.execute("""
            INSERT INTO ambulance_requests
                (id, requester_name, phone, pickup_location, urgency_tag, status,
                 patient_id, notes, latitude, longitude, location_source, created_at)
            VALUES (?, ?, ?, ?, ?, 'Pending', ?, ?, ?, ?, ?, ?)
        """, (
            amb_id,
            requester_name.strip(),
            phone.strip(),
            pickup_location.strip(),
            urgency_tag,
            patient_id,
            notes.strip(),
            latitude,
            longitude,
            location_source,
            created_at
        ))
    conn.close()
    return AmbulanceRequest(
        id=amb_id,
        requester_name=requester_name.strip(),
        phone=phone.strip(),
        pickup_location=pickup_location.strip(),
        urgency_tag=urgency_tag,
        status="Pending",
        patient_id=patient_id,
        notes=notes.strip(),
        latitude=latitude,
        longitude=longitude,
        location_source=location_source,
        created_at=created_at
    )

def get_all_ambulance_requests(status_filter: str = "All") -> List[AmbulanceRequest]:
    """Retrieve all ambulance requests, optionally filtered by status, newest first."""
    conn = get_connection()
    cursor = conn.cursor()
    if status_filter == "All":
        cursor.execute("SELECT * FROM ambulance_requests ORDER BY created_at DESC")
    else:
        cursor.execute(
            "SELECT * FROM ambulance_requests WHERE status = ? ORDER BY created_at DESC",
            (status_filter,)
        )
    rows = cursor.fetchall()
    conn.close()
    return [_row_to_ambulance(r) for r in rows]

def update_ambulance_status(amb_id: str, new_status: str) -> bool:
    """Update an ambulance request's dispatch status."""
    conn = get_connection()
    try:
        with conn:
            conn.execute(
                "UPDATE ambulance_requests SET status = ? WHERE id = ?",
                (new_status, amb_id.strip())
            )
        return True
    except Exception:
        return False
    finally:
        conn.close()

def link_ambulance_to_patient(amb_id: str, patient_id: str, notes: str = "") -> bool:
    """Link an ambulance request to a patient record post-stabilisation."""
    conn = get_connection()
    try:
        with conn:
            conn.execute(
                "UPDATE ambulance_requests SET patient_id = ?, notes = ? WHERE id = ?",
                (patient_id.strip(), notes.strip(), amb_id.strip())
            )
        return True
    except Exception:
        return False
    finally:
        conn.close()

def count_pending_ambulance_requests() -> int:
    """Return count of ambulance requests not yet Resolved."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) as cnt FROM ambulance_requests WHERE status != 'Resolved'"
    )
    cnt = cursor.fetchone()["cnt"]
    conn.close()
    return cnt

# ─── Blood Record functions ──────────────────────────────────────────────────

def _row_to_blood(r) -> BloodRecord:
    return BloodRecord(
        id=r["id"],
        blood_group=r["blood_group"],
        location=r["location"],
        type=r["type"],
        units=r["units"],
        contact_info=r["contact_info"],
        status=r["status"],
        created_at=r["created_at"]
    )

def generate_blood_record_id() -> str:
    """Generate next formatted Blood Record ID like BLD-1001."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM blood_records ORDER BY rowid DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if not row or not row["id"]:
        return "BLD-1001"
    try:
        if row["id"].startswith("BLD-"):
            num = int(row["id"].split("-")[1])
            return f"BLD-{num + 1}"
    except (IndexError, ValueError):
        pass
    conn2 = get_connection()
    c2 = conn2.cursor()
    c2.execute("SELECT COUNT(*) as cnt FROM blood_records")
    cnt = c2.fetchone()["cnt"]
    conn2.close()
    return f"BLD-{1001 + cnt}"

def create_blood_record(
    blood_group: str,
    location: str,
    record_type: str,
    units: int,
    contact_info: str
) -> BloodRecord:
    """Insert a new blood stock or request record."""
    bld_id = generate_blood_record_id()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    with conn:
        conn.execute("""
            INSERT INTO blood_records
                (id, blood_group, location, type, units, contact_info, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 'Open', ?)
        """, (
            bld_id,
            blood_group.strip(),
            location.strip(),
            record_type.strip(),
            units,
            contact_info.strip(),
            created_at
        ))
    conn.close()
    return BloodRecord(
        id=bld_id,
        blood_group=blood_group.strip(),
        location=location.strip(),
        type=record_type.strip(),
        units=units,
        contact_info=contact_info.strip(),
        status="Open",
        created_at=created_at
    )

def search_blood_records(
    blood_group: str = "All",
    location_query: str = "",
    record_type: str = "All",
    status_filter: str = "Open"
) -> List[BloodRecord]:
    """Search blood records by group, location substring, type, and status."""
    conn = get_connection()
    cursor = conn.cursor()
    
    sql = "SELECT * FROM blood_records WHERE 1=1"
    params = []

    if status_filter != "All":
        sql += " AND status = ?"
        params.append(status_filter)

    if blood_group != "All":
        sql += " AND blood_group = ?"
        params.append(blood_group)

    if record_type != "All":
        sql += " AND type = ?"
        params.append(record_type)

    if location_query.strip():
        sql += " AND location LIKE ?"
        params.append(f"%{location_query.strip()}%")

    sql += " ORDER BY created_at DESC"
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    return [_row_to_blood(r) for r in rows]

def update_blood_record_status(record_id: str, new_status: str) -> bool:
    """Update a blood record's status (Open / Fulfilled / Expired)."""
    conn = get_connection()
    try:
        with conn:
            conn.execute(
                "UPDATE blood_records SET status = ? WHERE id = ?",
                (new_status, record_id.strip())
            )
        return True
    except Exception:
        return False
    finally:
        conn.close()

def count_open_blood_requests() -> int:
    """Return count of open blood requirement requests."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) as cnt FROM blood_records WHERE type = 'Requested' AND status = 'Open'"
    )
    cnt = cursor.fetchone()["cnt"]
    conn.close()
    return cnt

# ─── Facility functions ───────────────────────────────────────────────────────

def get_all_facilities() -> List[Facility]:
    """Return all affiliated facilities ordered by name."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM facilities ORDER BY name ASC")
    rows = cursor.fetchall()
    conn.close()
    return [
        Facility(
            id=r["id"],
            name=r["name"],
            address=r["address"],
            phone=r["phone"],
            specializations=r["specializations"],
            operating_hours=r["operating_hours"],
        )
        for r in rows
    ]


def seed_facilities():
    """Idempotent seed of affiliated facility directory."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as cnt FROM facilities")
    if cursor.fetchone()["cnt"] > 0:
        conn.close()
        return
    with conn:
        conn.executemany("""
            INSERT INTO facilities (id, name, address, phone, specializations, operating_hours)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [
            (
                "FAC-001",
                "Springfield Central Medical Centre",
                "147 North Grand Avenue, Springfield, IL 62701",
                "+1 555-0100",
                "General Medicine · Preventive Screening · Administrative Records · Phlebotomy",
                "Mon–Fri 08:00–18:00 · Sat 09:00–14:00 · Emergency Walk-in: 24/7"
            ),
            (
                "FAC-002",
                "Fairview General Hospital — Outpatient Wing",
                "900 East Mason Street, Fairview, IL 62702",
                "+1 555-0177",
                "Outpatient Consultations · Diagnostics Coordination · Occupational Health Certification",
                "Mon–Sat 07:30–20:00 · Emergency Department: 24/7"
            ),
            (
                "FAC-003",
                "Metroville Community Health Clinic",
                "22 Green Park Road, Metroville, IL 62703",
                "+1 555-0155",
                "Routine Checkups · Administrative Follow-up · Documentation & Certificates · Blood Draw",
                "Mon–Fri 09:00–17:00 · Closed Weekends"
            ),
            (
                "FAC-004",
                "Springfield Emergency Care & Trauma Hub",
                "515 West Capitol Avenue, Springfield, IL 62704",
                "+1 555-0144",
                "Emergency Triage · Trauma Coordination · Ambulance Receiving Bay · ICU Administrative Liaison",
                "24/7 — Walk-in & Emergency Only"
            ),
            (
                "FAC-005",
                "Lakeview Occupational Health & Screening Centre",
                "8 Riverside Drive, Lakeview, IL 62705",
                "+1 555-0122",
                "Occupational Health Certification · Employment Medicals · Fitness-for-Work Assessments",
                "Mon–Fri 08:30–17:00 · Appointment Required"
            ),
        ])
    conn.close()


# ─── Seed Demo Data ──────────────────────────────────────────────────────────


def seed_demo_data():
    """Seed initial realistic records if database is empty."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM patients")
    count = cursor.fetchone()["count"]

    if count == 0:
        demo_patients = [
            (
                "PAT-1001", "Eleanor Vance", "1988-06-14", "Female",
                "+1 555-0142", "O+", "450 Maple Avenue, Springfield",
                "Prefers communication in English. Wheelchair accessibility required.",
                "2026-09-25 09:30:00"
            ),
            (
                "PAT-1002", "Marcus Holloway", "1994-11-23", "Male",
                "+1 555-0178", "A-", "128 Oak Ridge Lane, Fairview",
                "Primary contact phone is personal cell. Evening contact preferred.",
                "2026-09-26 11:15:00"
            ),
            (
                "PAT-1003", "Priya Sharma", "1991-03-08", "Female",
                "+1 555-0199", "B+", "77 Pine Boulevard, Metroville",
                "Prefers SMS appointment confirmations.",
                "2026-09-26 14:40:00"
            ),
        ]
        with conn:
            conn.executemany("""
                INSERT INTO patients (id, name, dob, gender, phone, blood_group, address, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, demo_patients)

            conn.executemany("""
                INSERT INTO appointments (id, patient_id, date, time, reason, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, [
                (
                    "APT-1001", "PAT-1001", "2026-09-28", "10:00 AM",
                    "Routine Checkup: Annual administrative physical check",
                    "Confirmed", "2026-09-25 10:00:00"
                ),
                (
                    "APT-1002", "PAT-1002", "2026-09-29", "02:30 PM",
                    "Administrative Follow-up: Employment medical certificate review",
                    "Scheduled", "2026-09-26 12:00:00"
                ),
            ])

            conn.executemany("""
                INSERT INTO ambulance_requests
                    (id, requester_name, phone, pickup_location, urgency_tag, status,
                     patient_id, notes, latitude, longitude, location_source, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                (
                    "AMB-1001", "Daniel Carter", "+1 555-0301",
                    "Corner of Maple Ave & 3rd Street, near the pharmacy",
                    "High", "Dispatched", "PAT-1001",
                    "Unit 7 dispatched. Patient linked post-call.",
                    39.7817, -89.6501, "Auto",
                    "2026-09-27 08:15:00"
                ),
                (
                    "AMB-1002", "Riya Nair", "+91 98765 43210",
                    "Green Park Bus Stand, Gate 2, Metroville",
                    "Medium", "Pending", None,
                    "",
                    None, None, "Manual",
                    "2026-09-27 11:40:00"
                ),
            ])


            conn.executemany("""
                INSERT INTO blood_records
                    (id, blood_group, location, type, units, contact_info, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                (
                    "BLD-1001", "O+", "Springfield Central Blood Bank",
                    "Available", 12, "Coordinator Desk: +1 555-0100",
                    "Open", "2026-09-26 09:00:00"
                ),
                (
                    "BLD-1002", "A-", "Fairview General Hospital Wing B",
                    "Requested", 4, "Emergency Desk: +1 555-0177",
                    "Open", "2026-09-27 08:30:00"
                ),
                (
                    "BLD-1003", "B+", "Metroville Red Cross Donor Center",
                    "Available", 8, "Donor Helpline: +1 555-0199",
                    "Open", "2026-09-27 10:15:00"
                ),
                (
                    "BLD-1004", "O-", "Springfield Emergency Care Depot",
                    "Requested", 6, "Triage Desk: +1 555-0144",
                    "Open", "2026-09-27 11:00:00"
                ),
            ])

    # Ensure blood_records seed entries exist even if patients were previously seeded
    cursor.execute("SELECT COUNT(*) as cnt FROM blood_records")
    bld_cnt = cursor.fetchone()["cnt"]
    if bld_cnt == 0:
        with conn:
            conn.executemany("""
                INSERT INTO blood_records
                    (id, blood_group, location, type, units, contact_info, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                (
                    "BLD-1001", "O+", "Springfield Central Blood Bank",
                    "Available", 12, "Coordinator Desk: +1 555-0100",
                    "Open", "2026-09-26 09:00:00"
                ),
                (
                    "BLD-1002", "A-", "Fairview General Hospital Wing B",
                    "Requested", 4, "Emergency Desk: +1 555-0177",
                    "Open", "2026-09-27 08:30:00"
                ),
                (
                    "BLD-1003", "B+", "Metroville Red Cross Donor Center",
                    "Available", 8, "Donor Helpline: +1 555-0199",
                    "Open", "2026-09-27 10:15:00"
                ),
                (
                    "BLD-1004", "O-", "Springfield Emergency Care Depot",
                    "Requested", 6, "Triage Desk: +1 555-0144",
                    "Open", "2026-09-27 11:00:00"
                ),
            ])

    # Ensure historical completed appointments exist for demo patients
    with conn:
        conn.executemany("""
            INSERT OR IGNORE INTO appointments (id, patient_id, date, time, reason, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [
            (
                "APT-1000", "PAT-1001", "2026-08-15", "09:30 AM",
                "Preventive Screening: Initial administrative intake evaluation",
                "Completed", "2026-08-10 09:00:00"
            ),
            (
                "APT-0999", "PAT-1002", "2026-08-20", "11:00 AM",
                "Documentation & Certificates: Annual records review",
                "Completed", "2026-08-15 14:00:00"
            ),
            (
                "APT-0998", "PAT-1003", "2026-08-10", "10:30 AM",
                "Routine Checkup: Initial intake visit and administrative profiling",
                "Completed", "2026-08-05 11:00:00"
            ),
        ])

    conn.close()




# Auto-initialize tables when imported
init_db()
seed_demo_data()
seed_facilities()
