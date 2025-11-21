from django.shortcuts import render, redirect
from base import models as base_models
from doctor import models as doctor_models
from patient import models as patient_models
from django.contrib.auth.decorators import login_required

def index(request):
    services = base_models.Service.objects.all()
    context = {
        "services": services
    }
    return render(request, "base/index.html", context)


def service_detail(request, service_id):
    service = base_models.Service.objects.get(id=service_id)
    context = {
        "service": service
    }
    return render(request, "base/service_detail.html", context)


@login_required
def book_appointment(request, service_id, doctor_id):
    service = base_models.Service.objects.get(id=service_id)
    doctor = doctor_models.Doctor.objects.get(id=doctor_id)
    patient = patient_models.Patient.objects.get(user=request.user)

    slots = doctor_models.DoctorAvailableSlot.objects.filter(
        doctor=doctor,
        is_booked=False
    ).order_by("date", "start_time")

    if request.method == "POST":
        # Update patient information with new fields
        patient.first_name = request.POST.get("first_name")
        patient.last_name = request.POST.get("last_name")
        patient.email = request.POST.get("email")
        patient.mobile = request.POST.get("mobile")
        patient.gender = request.POST.get("gender")
        patient.address = request.POST.get("address")
        patient.dob = request.POST.get("dob")
        patient.blood_group = request.POST.get("blood_group")
        patient.save()

        # Get selected slot
        slot_id = request.POST.get("slot_id")
        slot = doctor_models.DoctorAvailableSlot.objects.get(id=slot_id)

        # Mark slot as booked
        slot.is_booked = True
        slot.save()

        # Create appointment with slot
        appointment = base_models.Appointment.objects.create(
            service=service,
            doctor=doctor,
            patient=patient,
            slot=slot,
            issues=request.POST.get("issues"),
            symptoms=request.POST.get("symptoms"),
            status="Scheduled"
        )

        # Notify doctor
        doctor_models.Notification.objects.create(
            doctor=doctor,
            appointment=appointment,
            type="New Appointment"
        )

        return redirect("base:appointment_success", appointment_id=appointment.appointment_id)

    return render(request, "base/book_appointment.html", {
        "service": service,
        "doctor": doctor,
        "patient": patient,
        "slots": slots
    })


def appointment_success(request, appointment_id):
    """Appointment success page after booking"""
    try:
        appointment = base_models.Appointment.objects.get(appointment_id=appointment_id)
        context = {
            "appointment": appointment,
            "appointment_id": appointment_id
        }
    except base_models.Appointment.DoesNotExist:
        context = {
            "appointment": None,
            "appointment_id": appointment_id
        }
    
    return render(request, "base/appointment_success.html", context)

