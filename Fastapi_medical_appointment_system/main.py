from fastapi import FastAPI, HTTPException, status, Query
from enum import Enum
from pydantic import BaseModel, Field
from datetime import date, time
from typing import Optional, List

app = FastAPI()

@app.get("/")
def home():
    return {"message" : "Welcome to MediCare Clinic"}

#-----------------BaseModel ----------------------------
#---- Qn 7
class AppointmentType(str, Enum):
    online = "online"
    in_person = "in-person"
    emergency = "emergency"

class AppointmentStatus(str, Enum):
    scheduled = "scheduled"
    confirmed = "confirmed"
    cancelled = "cancelled"

#---- 
class DoctorResponse(BaseModel):
    id: int
    name: str
    specialty: str
    fee: int
    experience: int
    is_available: bool

#----Qn 6
class AppointmentRequest(BaseModel):
    patient_name: str = Field(..., min_length = 2)
    doctor_id : int = Field(..., gt = 0)
    age: int = Field(..., ge=0, le=120)
    date: date
    time: time
    reason : str = Field(..., min_length = 5)
    appointment_type: AppointmentType = AppointmentType.in_person

#----Qn 11
class NewDoctor(BaseModel):
    name: str = Field(..., min_length=2)
    specialty: str = Field(..., min_length=2)
    fee: int = Field(..., gt=0)
    experience: int = Field(..., ge=0)
    is_available: bool = True

#------HELPER--------
#---Qn 5
def count_available_doctors():                      
    return sum(1 for  doc in doctors if doc["is_available"])

#----Qn 3
def find_doctor(doctor_id):
    for doctor in doctors:
        if doctor["id"] == doctor_id:
            return doctor
    return None

#----Qn 7
def is_doctor_available(doctor):     
    return doctor["is_available"]

def is_slot_available(doctor_id, date, time):    
    for appointment in appointments:
        if(
            appointment["doctor_id"] == doctor_id and
            appointment["date"] == date and
            appointment["time"] == time
        ):
            return False
    return True

#---Qn 14
def find_appointment(appointment_id):
    return next((appt for appt in appointments if appt["appointment_id"] == appointment_id), None)

#----Qn 15
def get_active_appointments_logic():
    return [
        appt for appt in appointments
        if appt.get("status") in ["scheduled", "confirmed"]
    ]

#----Qn 16
def search_doctors_logic(keyword: str):
    keyword = keyword.lower()

    results = [
        doc for doc in doctors
        if keyword in doc["name"].lower()
        or keyword in doc["specialty"].lower()
    ]

    return results

#----Qn 17
def sort_doctors_logic(sort_by: str, order: str):
    # Map user input to actual field
    field_map = {
        "fee": "fee",
        "name": "name",
        "experience_years": "experience"
    }

    actual_field = field_map[sort_by]

    reverse = True if order == "desc" else False

    sorted_list = sorted(
        doctors,
        key=lambda doc: doc[actual_field].lower() if actual_field == "name" else doc[actual_field],
        reverse=reverse
    )

    return sorted_list

#----Qn 18
def paginate_doctors_logic(page: int, limit: int):
    total = len(doctors)

    # Calculate start index
    start = (page - 1) * limit
    end = start + limit

    # Slice list
    paginated = doctors[start:end]

    # Ceiling division for total pages
    total_pages = (total + limit - 1) // limit

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "doctors": paginated
    }

#----Qn 19
def search_appointments_logic(keyword: str):
    keyword = keyword.lower()

    return [
        appt for appt in appointments
        if keyword in appt["patient_name"].lower()
    ]
#---b
def sort_appointments_logic(sort_by: str, order: str):
    allowed_fields = {
        "fee": "final_fee",
        "date": "date"
    }

    actual_field = allowed_fields[sort_by]
    reverse = True if order == "desc" else False

    return sorted(
        appointments,
        key=lambda appt: appt[actual_field],
        reverse=reverse
    )
#----c
def paginate_appointments_logic(page: int, limit: int):
    total = len(appointments)

    start = (page - 1) * limit
    end = start + limit

    paginated = appointments[start:end]

    total_pages = (total + limit - 1) // limit

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "appointments": paginated
    }
#----Qn 20
def browse_doctors_logic(keyword, sort_by, order, page, limit):
    # ------------------ FILTER ------------------
    filtered = doctors

    if keyword:
        keyword = keyword.lower()
        filtered = [
            doc for doc in filtered
            if keyword in doc["name"].lower()
            or keyword in doc["specialty"].lower()
        ]

    # ------------------ SORT ------------------
    field_map = {
        "fee": "fee",
        "name": "name",
        "experience_years": "experience"
    }

    actual_field = field_map[sort_by]
    reverse = True if order == "desc" else False

    filtered = sorted(
        filtered,
        key=lambda doc: doc[actual_field].lower() if actual_field == "name" else doc[actual_field],
        reverse=reverse
    )

    # ------------------ PAGINATION ------------------
    total = len(filtered)

    start = (page - 1) * limit
    end = start + limit

    paginated = filtered[start:end]

    total_pages = (total + limit - 1) // limit

    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "doctors": paginated
    }
#----Qn 2
doctors = [
    {"id": 1, "name": "Dr. Smith", "specialty": "Cardiology", "is_available": True, "fee": 500, "experience": 10},
    {"id": 2, "name": "Dr. Jones", "specialty": "Neurology", "is_available": False, "fee": 700, "experience": 8},
    {"id": 3, "name": "Dr. Taylor", "specialty": "Pediatrics", "is_available": True, "fee": 400, "experience": 5},
    {"id": 4, "name": "Dr. Brown", "specialty": "Dermatology", "is_available": True, "fee": 450, "experience": 6},
    {"id": 5, "name": "Dr. Wilson", "specialty": "Orthopedics", "is_available": False, "fee": 800, "experience": 12},
    {"id": 6, "name": "Dr. Miller", "specialty": "General Medicine", "is_available": True, "fee": 300, "experience": 7},
]

@app.get("/doctors")
def get_doctors():
    total_doctors = len(doctors)
    available_doctors = sum(1 for doc in doctors if doc["is_available"])
    #available_doctors = len([doc for doc in doctors if doc["is_available"]])

    return {
        "total": total_doctors,
        "available" : available_doctors,
        "doctors": doctors
    }

#---- Qn 5
@app.get("/doctors/summary")
def get_doctors_summary():
    total = len(doctors)
    available = count_available_doctors()
    unavailable = total - available
    specialties = list({doc["specialty"] for doc in doctors})
    return {
        "total": total,
        "available": available,
        "unavailable": unavailable,
        "specialties": specialties
    }

#----Qn 8
def filter_doctors_logic(specialization=None, max_fee=None, min_experience=None, is_available=None):
    filtered = doctors.copy()

    if specialization is not None:
        filtered = [
            doc for doc in filtered
            if specialization.lower() in doc["specialty"].lower()
        ]

    if max_fee is not None:
        filtered = [
            doc for doc in filtered
            if doc["fee"] <= max_fee
        ]

    if min_experience is not None:
        filtered = [
            doc for doc in filtered
            if doc["experience"] >= min_experience
        ]

    if is_available is not None:
        filtered = [
            doc for doc in filtered
            if doc["is_available"] == is_available
        ]

    return filtered

@app.get("/doctors/filter")
def filter_doctors(
    specialization: Optional[str] = None,
    max_fee: Optional[int] = None,
    min_experience: Optional[int] = None,
    is_available: Optional[bool] = None
):
    filtered = filter_doctors_logic(
        specialization,
        max_fee,
        min_experience,
        is_available
    )

    return {
        "total": len(filtered),
        "filters": {
            "specialization": specialization,
            "max_fee": max_fee,
            "min_experience": min_experience,
            "is_available": is_available
        },
        "doctors": filtered
    }

#----Qn 16
@app.get("/doctors/search")
def search_doctors(keyword: str = Query(..., min_length=1)):
    # Call helper function
    results = search_doctors_logic(keyword)

    # Sort results by name
    results = sorted(results, key=lambda x: x["name"].lower())

    if not results:
        return {
            "message": "No doctors found matching your search",
            "total_found": 0,
            "doctors": []
        }

    return {
        "total_found": len(results),
        "keyword": keyword,
        "doctors": results
    }

#----Qn 17
@app.get("/doctors/sort")
def sort_doctors(
    sort_by: str = Query("fee"),
    order: str = Query("asc")
):
    allowed_sort = ["fee", "name", "experience_years"]
    allowed_order = ["asc", "desc"]

    # Validation
    if sort_by not in allowed_sort:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort_by. Allowed: {allowed_sort}"
        )

    if order not in allowed_order:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid order. Allowed: {allowed_order}"
        )

    sorted_doctors = sort_doctors_logic(sort_by, order)

    return {
        "sort_by": sort_by,
        "order": order,
        "total": len(sorted_doctors),
        "doctors": sorted_doctors
    }

#----Qn 18
@app.get("/doctors/page")
def get_doctors_page(
    page: int = Query(1, ge=1),
    limit: int = Query(3, ge=1, le=10)
):
    result = paginate_doctors_logic(page, limit)

    # Optional: handle empty page
    if page > result["total_pages"] and result["total_pages"] != 0:
        raise HTTPException(
            status_code=400,
            detail="Page number exceeds total pages"
        )

    return result

#----QN 20 ALL COMBINED
@app.get("/doctors/browse")
def browse_doctors(
    keyword: Optional[str] = None,
    sort_by: str = Query("fee"),
    order: str = Query("asc"),
    page: int = Query(1, ge=1),
    limit: int = Query(4, ge=1, le=10)
):
    allowed_sort = ["fee", "name", "experience_years"]
    allowed_order = ["asc", "desc"]

    # Validation
    if sort_by not in allowed_sort:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort_by. Allowed: {allowed_sort}"
        )

    if order not in allowed_order:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid order. Allowed: {allowed_order}"
        )

    result = browse_doctors_logic(keyword, sort_by, order, page, limit)

    if page > result["total_pages"] and result["total_pages"] != 0:
        raise HTTPException(
            status_code=400,
            detail="Page exceeds total pages"
        )

    return result

#----Qn 3
@app.get("/doctors/{doctor_id}")
def get_doctor_by_id(doctor_id: int):
    doctor = find_doctor(doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail= "Doctor not found")
    return doctor

#----Qn 4
appointments = []
appointment_counter = 1

@app.get("/appointments", status_code=status.HTTP_200_OK)
def get_appointments():
    total_appointments = len(appointments)
    return {
        "total" : total_appointments,
        "appointments": appointments
    }

#----Qn 7
def calculate_fee(doctor_fee, appointment_type, senior):
    # Base fee from doctor
    base_fee = doctor_fee

    # Modify based on appointment type
    if appointment_type == AppointmentType.online:
        base_fee *= 0.8   # 20% less
    elif appointment_type == AppointmentType.emergency:
        base_fee *= 1.5   # 50% extra
    # in_person → no change

    original_fee = int(base_fee)

    # Apply senior discount
    if senior:
        final_fee = original_fee * 0.85
    else:
        final_fee = original_fee

    return {
        "original_fee": original_fee,
        "final_fee": int(final_fee)
    }
#----Qn 6
@app.post("/appointments", status_code=status.HTTP_201_CREATED)
def create_appointment(appointment: AppointmentRequest):
    global appointment_counter

    # 1. Check doctor exists
    doctor = find_doctor(appointment.doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # 2. Check doctor availability
    if not is_doctor_available(doctor):
        raise HTTPException(status_code=400, detail="Selected doctor is currently unavailable")

    # 3. Check slot availability
    if not is_slot_available(appointment.doctor_id, appointment.date, appointment.time):
        raise HTTPException(status_code=400, detail="Slot already booked")
    
    senior = appointment.age >= 65
    doctor_fee = doctor["fee"]
    # 4. Calculate fee
    fee_details = calculate_fee(
        doctor_fee,
        appointment.appointment_type,
        senior
    )

    # 5. Create appointment record
    new_appointment = {
        "appointment_id": appointment_counter,
        "patient_name": appointment.patient_name,
        "doctor_id": appointment.doctor_id,
        "date": appointment.date,
        "time": appointment.time,
        "age": appointment.age,
        "senior_citizen": senior,
        "reason": appointment.reason,
        "appointment_type": appointment.appointment_type,

        "original_fee": fee_details["original_fee"],
        "final_fee": fee_details["final_fee"],

        "status": "scheduled"
    }

    # 6. Save appointment
    appointments.append(new_appointment)
    appointment_counter += 1

    # 7. Return response
    return {
        "status": "scheduled",
        "message": "Appointment booked successfully",
        "appointment": new_appointment
    }

#----Qn 11
@app.post("/doctors", status_code=status.HTTP_201_CREATED)
def add_doctor(doctor: NewDoctor):

    # 1. Duplicate check
    for doc in doctors:
        if (
            doc["name"].lower() == doctor.name.lower() and
            doc["specialty"].lower() == doctor.specialty.lower()
        ):
            raise HTTPException(status_code=400, detail="Doctor already exists in this specialty")
    # 2. Generate ID
    new_id = max(doc["id"] for doc in doctors) + 1 

    # 3. Create doctor
    new_doctor = {
        "id": new_id,
        "name": doctor.name,
        "specialty": doctor.specialty,
        "fee": doctor.fee,
        "experience": doctor.experience,
        "is_available": doctor.is_available
    }

    # 4. Add to list
    doctors.append(new_doctor)

    # 5. Return
    return {
        "status": "success",
        "doctor": new_doctor
    }

#----Qn 12
@app.put("/doctors/{doctor_id}")
def update_doctor(
    doctor_id: int,
    fee: Optional[int] = None,
    is_available: Optional[bool] = None
):
    # 1. Find doctor
    doctor = find_doctor(doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # 2. Apply updates only if provided
    if fee is not None:
        doctor["fee"] = fee

    if is_available is not None:
        doctor["is_available"] = is_available

    # 3. Return updated doctor
    return {
        "status": "updated",
        "doctor": doctor
    }

#----Qn 13
@app.delete("/doctors/{doctor_id}")
def delete_doctor(doctor_id: int):
    doctor = find_doctor(doctor_id)

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # Check BOTH scheduled + confirmed appointments
    for appointment in appointments:
        if (
            appointment["doctor_id"] == doctor_id and
            appointment.get("status") in ["scheduled", "confirmed"]
        ):
            raise HTTPException(
                status_code=400,
                detail="Cannot delete doctor with active appointments"
            )
    doctors.remove(doctor)

    return {
        "status": "deleted",
        "message": f"{doctor['name']} removed successfully"
    }
    
#----Qn 15
@app.get("/appointments/active")
def get_active_appointments():
    active = get_active_appointments_logic()

    return {
        "total": len(active),
        "appointments": active
    }

#----Qn 19
@app.get("/appointments/search")
def search_appointments(keyword: str = Query(..., min_length=1)):
    results = search_appointments_logic(keyword)

    if not results:
        return {
            "message": "No appointments found",
            "total_found": 0,
            "appointments": []
        }

    return {
        "keyword": keyword,
        "total_found": len(results),
        "appointments": results
    }
#---b
@app.get("/appointments/sort")
def sort_appointments(
    sort_by: str = Query("fee"),
    order: str = Query("asc")
):
    allowed_sort = ["fee", "date"]
    allowed_order = ["asc", "desc"]

    if sort_by not in allowed_sort:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort_by. Allowed: {allowed_sort}"
        )

    if order not in allowed_order:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid order. Allowed: {allowed_order}"
        )

    sorted_list = sort_appointments_logic(sort_by, order)

    return {
        "sort_by": sort_by,
        "order": order,
        "total": len(sorted_list),
        "appointments": sorted_list
    }
#----c
@app.get("/appointments/page")
def get_appointments_page(
    page: int = Query(1, ge=1),
    limit: int = Query(3, ge=1, le=10)
):
    result = paginate_appointments_logic(page, limit)

    if page > result["total_pages"] and result["total_pages"] != 0:
        raise HTTPException(
            status_code=400,
            detail="Page number exceeds total pages"
        )

    return result

#----Qn 14
@app.post("/appointments/{appointment_id}/confirm")
def confirm_appointment(appointment_id: int):
    appointment = find_appointment(appointment_id)

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Prevent confirming again
    if appointment["status"] != "scheduled":
        raise HTTPException(
            status_code=400,
            detail="Only scheduled appointments can be confirmed"
        )

    appointment["status"] = "confirmed"

    return {
        "status": "success",
        "message": "Appointment confirmed",
        "appointment": appointment
    }

@app.post("/appointments/{appointment_id}/cancel")
def cancel_appointment(appointment_id: int):
    appointment = find_appointment(appointment_id)

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if appointment["status"] == "cancelled":
        raise HTTPException(status_code=400, detail="Appointment already cancelled")

    # Update status
    appointment["status"] = "cancelled"

    # Make doctor available again
    doctor = find_doctor(appointment["doctor_id"])
    if doctor:
        doctor["is_available"] = True

    return {
        "status": "success",
        "message": "Appointment cancelled",
        "appointment": appointment
    }