from fastapi import FastAPI, HTTPException, status
from enum import Enum
from pydantic import BaseModel, Field
from datetime import date, time
from typing import Optional

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
        "date": str(appointment.date),
        "time": str(appointment.time),
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
    new_id = len(doctors) + 1

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
    # 1. Find doctor
    doctor = find_doctor(doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # 2. Check active appointments
    for appointment in appointments:
        if (
            appointment["doctor_id"] == doctor_id and
            appointment.get("status") == "scheduled"
        ):
            raise HTTPException(
                status_code=400,
                detail="Cannot delete doctor with active scheduled appointments"
            )

    # 3. Delete doctor
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

#----Qn 14
@app.post("/appointments/{appointment_id}/confirm")
def confirm_appointment(appointment_id: int):
    appointment = find_appointment(appointment_id)

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

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

    # 1. Update status
    appointment["status"] = "cancelled"

    # 2. Free doctor
    doctor = find_doctor(appointment["doctor_id"])
    if doctor:
        doctor["is_available"] = True

    return {
        "status": "success",
        "message": "Appointment cancelled",
        "appointment": appointment
    }
