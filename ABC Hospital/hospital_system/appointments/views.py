from django.shortcuts import render,redirect
from django.http import JsonResponse
from .models import Department, Appointment, Doctor
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import Appointment, Doctor
from django.contrib import messages
from django.core.paginator import Paginator

# Home Page
def home(request):
    return render(request, 'appointments/home.html')



@csrf_exempt
def create_appointment(request):
    if request.method == 'POST':
        department_id = request.POST.get('department_id')
        name = request.POST.get('name')
        mobile_number = request.POST.get('mobile_number')

        if not department_id or not name or not mobile_number:
            return JsonResponse({'message': 'All fields are required'}, status=400)
        
        try:
            department = Department.objects.get(id=department_id)
            # Get all doctors in the selected department
            doctors = Doctor.objects.filter(department=department)
        except Department.DoesNotExist:
            return JsonResponse({'message': 'Department not found'}, status=404)

        # Check if there are any doctors in the department
        if not doctors.exists():
            return JsonResponse({'message': 'No doctors found in this department'}, status=404)
        
        # Find the doctor with the least number of appointments
        doctor_counts = {doctor.id: Appointment.objects.filter(doctor=doctor).count() for doctor in doctors}
        least_appointments_doctor_id = min(doctor_counts, key=doctor_counts.get)
        
        # Get the doctor with the least appointments
        doctor = Doctor.objects.get(id=least_appointments_doctor_id)
        
        # Calculate token number based on department and doctor
        token_number = Appointment.objects.filter(department=department, doctor=doctor).count() + 1
        
        # Create the appointment
        appointment = Appointment.objects.create(
            department=department,
            doctor=doctor,
            name=name,
            mobile_number=mobile_number,
            token_number=token_number
        )

        # Redirect to success page with the token number
        return redirect('appointment_success', token_number=token_number)

    # For GET request, render the form (if necessary)
    departments = Department.objects.all()
    return render(request, 'appointments/create_appointment.html', {'departments': departments})

def appointment_success(request, token_number):
    return render(request, 'appointments/appointment_success.html', {'token_number': token_number})

# View for listing departments
def department_list(request):
    departments = Department.objects.all()
    return JsonResponse({'departments': [department.name for department in departments]})


def appointment_list(request):
    search_query = request.GET.get('search', '')  # Get the search query from GET request
    group_by_doctor = request.GET.get('group_by_doctor', 'false') == 'true'  # Check if grouping is enabled

    if search_query:
        # If there's a search query, filter appointments by name or mobile number
        appointments = Appointment.objects.filter(
            name__icontains=search_query
        ) | Appointment.objects.filter(
            mobile_number__icontains=search_query
        )
    else:
        # Otherwise, fetch all appointments
        appointments = Appointment.objects.all()

    # Pagination
    paginator = Paginator(appointments, 10)  # Show 10 appointments per page
    page_number = request.GET.get('page')  # Get the current page number from GET
    page_obj = paginator.get_page(page_number)

    # If the 'group_by_doctor' flag is True, group appointments by doctor
    if group_by_doctor:
        appointments_by_doctor = {}
        for appointment in page_obj:
            if appointment.doctor not in appointments_by_doctor:
                appointments_by_doctor[appointment.doctor] = []
            appointments_by_doctor[appointment.doctor].append(appointment)
        return render(request, 'appointments/appointment_list.html', {
            'appointments': appointments_by_doctor,
            'group_by_doctor': True,
            'search_query': search_query,
            'page_obj': page_obj
        })

    # If not grouping, show all appointments in a table
    return render(request, 'appointments/appointment_list.html', {
        'appointments': page_obj,
        'group_by_doctor': False,
        'search_query': search_query,
        'page_obj': page_obj
    })





def get_doctors(request, department_id):
    doctors = Doctor.objects.filter(department_id=department_id)
    doctor_list = [{'id': doctor.id, 'name': doctor.name} for doctor in doctors]
    return JsonResponse({'doctors': doctor_list})
