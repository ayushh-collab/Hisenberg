"""
MediConnect Data Models & Validation
Administrative healthcare management platform schemas.
Zero clinical/diagnostic fields.
"""
from dataclasses import dataclass
from typing import Optional, Tuple
import re
from datetime import date, datetime

VALID_BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"]
VALID_GENDERS = ["Male", "Female", "Other", "Prefer not to say"]

@dataclass
class Patient:
    id: str
    name: str
    dob: str
    gender: str
    phone: str
    blood_group: str
    address: str = ""
    notes: str = ""
    created_at: str = ""

    @staticmethod
    def validate(name: str, dob: date, gender: str, phone: str, blood_group: str, address: str = "", notes: str = "") -> Tuple[bool, str]:
        """Validate patient registration inputs."""
        clean_name = name.strip()
        if not clean_name or len(clean_name) < 2:
            return False, "Please enter a valid patient full name (at least 2 characters)."
        
        if not dob:
            return False, "Please select a valid date of birth."
        
        if dob > date.today():
            return False, "Date of birth cannot be in the future."
        
        if gender not in VALID_GENDERS:
            return False, f"Please select a valid gender option from {VALID_GENDERS}."
        
        clean_phone = phone.strip()
        # Ensure phone has reasonable digits (at least 7, at most 15, allow +, -, space)
        digits_only = re.sub(r"[^\d]", "", clean_phone)
        if len(digits_only) < 7 or len(digits_only) > 15:
            return False, "Please provide a valid contact phone number (7 to 15 digits)."
        
        if blood_group not in VALID_BLOOD_GROUPS:
            return False, f"Please select a valid blood group from {VALID_BLOOD_GROUPS}."
        
        return True, ""

APPOINTMENT_STATUSES = ["Scheduled", "Confirmed", "Completed", "Cancelled", "No-show"]
ADMINISTRATIVE_REASONS = [
    "Routine Checkup",
    "General Consultation",
    "Administrative Follow-up",
    "Preventive Screening",
    "Documentation & Certificates",
    "Other Administrative Visit"
]

@dataclass
class Appointment:
    id: str
    patient_id: str
    date: str
    time: str
    reason: str
    status: str = "Scheduled"
    created_at: str = ""

    @staticmethod
    def validate(patient_id: str, appt_date: date, appt_time: str, reason: str) -> Tuple[bool, str]:
        """Validate appointment booking details."""
        if not patient_id or not patient_id.strip():
            return False, "A valid Patient ID is required to book an appointment."
        
        if not appt_date:
            return False, "Please select an appointment date."
        
        if appt_date < date.today():
            return False, "Appointment date cannot be in the past."
        
        if not appt_time or not appt_time.strip():
            return False, "Please select an appointment time slot."
        
        clean_reason = reason.strip()
        if not clean_reason or len(clean_reason) < 3:
            return False, "Please enter an administrative reason for the visit (at least 3 characters)."
        
        return True, ""

URGENCY_TAGS = ["High", "Medium", "Low"]
AMBULANCE_STATUSES = ["Pending", "Dispatched", "En route", "Resolved"]
LOCATION_SOURCES = ["Auto", "Manual"]

@dataclass
class AmbulanceRequest:
    id: str
    requester_name: str
    phone: str
    pickup_location: str
    urgency_tag: str
    status: str = "Pending"
    patient_id: Optional[str] = None   # nullable — linked post-stabilisation
    notes: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_source: str = "Manual"
    created_at: str = ""

    @staticmethod
    def validate(name: str, phone: str, pickup_location: str, urgency_tag: str) -> Tuple[bool, str]:
        """Minimal validation — ambulance form must stay frictionless."""
        if not name.strip():
            return False, "Requester name is required."
        clean_phone = phone.strip()
        digits_only = re.sub(r"[^\d]", "", clean_phone)
        if len(digits_only) < 7 or len(digits_only) > 15:
            return False, "Please enter a valid callback phone number (7-15 digits)."
        if not pickup_location.strip():
            return False, "Pickup location or landmark is required."
        if urgency_tag not in URGENCY_TAGS:
            return False, "Please select a valid urgency level."
        return True, ""

BLOOD_RECORD_TYPES = ["Available", "Requested"]
BLOOD_RECORD_STATUSES = ["Open", "Fulfilled", "Expired"]

@dataclass
class BloodRecord:
    id: str
    blood_group: str
    location: str
    type: str
    units: int
    contact_info: str
    status: str = "Open"
    created_at: str = ""

    @staticmethod
    def validate(blood_group: str, location: str, record_type: str, units: int, contact_info: str) -> Tuple[bool, str]:
        """Validate blood bank stock or request entry."""
        if blood_group not in VALID_BLOOD_GROUPS or blood_group == "Unknown":
            return False, "Please select a specific valid blood group (e.g., A+, O-)."
        if not location.strip():
            return False, "Please enter a valid facility or city location."
        if record_type not in BLOOD_RECORD_TYPES:
            return False, f"Please select type from {BLOOD_RECORD_TYPES}."
        if units <= 0:
            return False, "Units must be at least 1."
        if not contact_info.strip():
            return False, "Please provide coordinator contact phone or email."
        return True, ""


@dataclass
class Facility:
    id: str
    name: str
    address: str
    phone: str
    specializations: str
    operating_hours: str

