
import calendar
from decimal import Decimal
import logging
from io import BytesIO
from datetime import datetime
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django import urls
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.template.loader import render_to_string
from django.contrib import messages
from django.utils import timezone
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from django.views.decorators.http import require_POST
from .serializers import ManualAttendanceSerializer
from .forms import *
from .models import *
from .user_pass import *


logger = logging.getLogger(__name__)


# def hi(request):
#     return render(request, 'index.html')
def index(request):
    return render(request, 'index.html')


def frontend_view(request):
    return render(request, 'index.html')


def dashboard(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('/login')

    if user.role == CustomUser.OVERALL_ADMIN:
        return render(request, 'admin_dashboard.html')
    elif user.role == CustomUser.MANAGER:
        return render(request, 'manager_dashboard.html')
    elif user.role == CustomUser.HR_MANAGER:
        return render(request, 'hr_dashboard.html')
    elif user.role == CustomUser.EMPLOYEE:
        return render(request, 'employee_dashboard.html')
    else:
        return redirect('/')


def homepage(request):

    return render(request, "index.html")


def login_page(request):
    return render(request, 'index.html')


def logout_page(request):
    return render(request, 'index.html')


def register_page(request):
    return render(request, 'index.html')


def hr_manager_register(request):
    return render(request, 'index.html')


def manager_register(request):
    return render(request, 'index.html')


def overall_admin_register(request):
    return render(request, 'index.html')


def employee_register(request):
    return render(request, 'index.html')


@login_required
def notifications_list(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('/login')

    notifications = Notification.objects.filter(
        recipient=request.user).order_by('-timestamp')
    return render(request, 'notifications_list.html', {'notifications': notifications})


@login_required
def read_notification(request, notification_id):
    user = request.user
    if not user.is_authenticated:
        return redirect('/login')

    try:

        biometric_attendance = BiometricAttendance.objects.filter(
            employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()
        manual_attendance = ManualAttendance.objects.filter(
            employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()

        if not (biometric_attendance or manual_attendance):
            return render(request, 'access_denied.html', {'message': 'You must check in first.'})
        notification = get_object_or_404(
            Notification, id=notification_id, recipient=request.user)
        notification.mark_as_read()
        return redirect('notifications_list')
    except Exception as e:
        logger.error(f"An Error Occured: {e}")
        return HttpResponse({'error': str(e)}, status=500)


@login_required
def get_unread_notification_count(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('/login')
    try:

        biometric_attendance = BiometricAttendance.objects.filter(
            employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()
        manual_attendance = ManualAttendance.objects.filter(
            employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()

        if not (biometric_attendance or manual_attendance):
            return render(request, 'access_denied.html', {'message': 'You must check in first.'})
        count = Notification.objects.filter(
            recipient=request.user, is_read=False).count()
        return JsonResponse({'unread_count': count})
    except Exception as e:
        logger.error(f"An Error Occured: {e}")
        return HttpResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def mark_notification_read(request):
    notif_id = request.POST.get('notification_id')
    user = request.user
    if not user.is_authenticated:
        return redirect('/login')
    try:

        biometric_attendance = BiometricAttendance.objects.filter(
            employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()
        manual_attendance = ManualAttendance.objects.filter(
            employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()

        if not (biometric_attendance or manual_attendance):
            return render(request, 'access_denied.html', {'message': 'You must check in first.'})
        notification = Notification.objects.get(
            id=notif_id, recipient=request.user)
        notification.mark_as_read()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        logger.error(f"An Error Occured: {e}")
        return JsonResponse({'success': False, 'error': 'Notification not found'})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def latest_manual_attendance(request):
    user = request.user
    today = date.today()

    # Check biometric attendance
    biometric = ManualAttendance.objects.filter(
        employee=user, date=today, method="biometric").first()
    if biometric:
        dummy = ManualAttendance(employee=user)
        dummy.method = "biometric"
        return Response(ManualAttendanceSerializer(dummy).data)

    manual = ManualAttendance.objects.filter(
        employee=user, date=today, method="manual").first()
    if manual:
        return Response(ManualAttendanceSerializer(manual).data)

    dummy = ManualAttendance(employee=user)
    return Response(ManualAttendanceSerializer(dummy).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def manual_check_in(request):
    user = request.user
    today = date.today()

    # Reject if biometric used today
    if ManualAttendance.objects.filter(employee=user, date=today, method="biometric").exists():
        return Response({"detail": "Biometric attendance used. Please continue with biometric."},
                        status=status.HTTP_400_BAD_REQUEST)

    # Prevent multiple check-ins
    attendance, created = ManualAttendance.objects.get_or_create(
        employee=user, date=today, method="manual")

    if attendance.check_in is not None:
        return Response({"detail": "Already checked in."}, status=status.HTTP_400_BAD_REQUEST)

    attendance.check_in = timezone.now()
    attendance.save()
    return Response(ManualAttendanceSerializer(attendance).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def manual_check_out(request):
    user = request.user
    today = date.today()

    # Reject if biometric used today
    if ManualAttendance.objects.filter(employee=user, date=today, method="biometric").exists():
        return Response({"detail": "Biometric attendance used. Please continue with biometric."},
                        status=status.HTTP_400_BAD_REQUEST)

    attendance = ManualAttendance.objects.filter(
        employee=user, date=today, method="manual").first()
    if not attendance or not attendance.check_in:
        return Response({"detail": "Check-in first."}, status=status.HTTP_400_BAD_REQUEST)

    if attendance.check_out is not None:
        return Response({"detail": "Already checked out."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if eligible to check out (after 1 hour)
    if not attendance.can_check_out():
        return Response({"detail": "Check-out not allowed yet. Please wait."},
                        status=status.HTTP_400_BAD_REQUEST)

    attendance.check_out = timezone.now()
    attendance.save()
    return Response(ManualAttendanceSerializer(attendance).data)


@login_required
@user_passes_test(is_allowed_to_create_salaries)
def create_salary(request, user_id):

    if not request.user.is_authenticated:
        return redirect('/login')
    try:

        biometric_attendance = BiometricAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()
        manual_attendance = ManualAttendance.objects.filter(
            employee=request.useruser, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()

        if not (biometric_attendance or manual_attendance):
            return render(request, 'access_denied.html', {'message': 'You must check in first.'})
        target_user = get_object_or_404(CustomUser, id=user_id)
        current_user = request.user

        if current_user == target_user:

            messages.error(request, "You cannot create a salary for yourself.")
            return redirect('salary_list')

        if target_user.role != CustomUser.EMPLOYEE:
            messages.error(
                request, "You can only create a salary for an employee.")
            return redirect('salary_list')

        if hasattr(target_user, 'salary'):
            messages.warning(request, "This user already has a salary record.")
            return redirect('salary_list')

        if current_user.role in [CustomUser.HR_MANAGER, CustomUser.MANAGER]:
            if target_user.department != current_user.department:
                messages.error(
                    request, "You can only create salaries for employees in your department.")
                return redirect('salary_list')

        if current_user.role == CustomUser.EMPLOYEE:
            messages.error(
                request, "You are not authorized to create salaries.")
            return redirect('salary_list')

        if request.method == 'POST':
            form = SalaryForm(request.POST)
            if form.is_valid():
                salary = form.save(commit=False)
                salary.employee = target_user

                OVERTIME_RATE = Decimal('20')
                PENSION_RATE = Decimal('0.075')
                PROVIDENT_FUND_RATE = Decimal('0.05')
                HEALTH_INSURANCE_RATE = Decimal('0.03')

                salary.gross_salary = (
                    salary.basic_salary +
                    (salary.overtime_hours * OVERTIME_RATE) +
                    salary.bonuses
                )

                salary.pension_contribution = salary.basic_salary * PENSION_RATE
                salary.provident_fund = salary.basic_salary * PROVIDENT_FUND_RATE
                salary.health_insurance = salary.basic_salary * HEALTH_INSURANCE_RATE

                if salary.basic_salary <= 30000:
                    salary.income_tax = salary.basic_salary * Decimal('0.05')
                elif salary.basic_salary <= 70000:
                    salary.income_tax = salary.basic_salary * Decimal('0.10')
                elif salary.basic_salary <= 150000:
                    salary.income_tax = salary.basic_salary * Decimal('0.15')
                else:
                    salary.income_tax = salary.basic_salary * Decimal('0.20')

                salary.total_deductions = (
                    salary.pension_contribution +
                    salary.provident_fund +
                    salary.health_insurance +
                    salary.income_tax
                )
                salary.net_salary = salary.gross_salary - salary.total_deductions

                salary.save()

                Notification.notify_user(
                    recipient=target_user,
                    message=f"Your salary record has been created by {current_user.name}."
                )

                messages.success(
                    request, "Salary record created successfully.")
                return redirect('salary_list')
        else:
            form = SalaryForm()

        return render(request, 'create_salary.html', {
            'form': form,
            'target_user': target_user
        })
    except Exception as e:
        logger.error(f"An Error Occured: {e}")
        messages.error(
            request, "error occured")

        return redirect('create_salary')


@login_required
def view_salary(request, salary_id):
    if not request.user.is_authenticated:
        return redirect('/login')

    biometric_attendance = BiometricAttendance.objects.filter(
        employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
    ).first()
    manual_attendance = ManualAttendance.objects.filter(
        employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
    ).first()

    if not (biometric_attendance or manual_attendance):
        return render(request, 'access_denied.html', {'message': 'You must check in first.'})
    salary = get_object_or_404(Salary, id=salary_id)
    return render(request, 'view_salary.html', {'salary': salary})


@login_required
def salary_list(request):
    try:
        if not request.user.is_authenticated:
            return redirect('/login')

        biometric_attendance = BiometricAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()
        manual_attendance = ManualAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()

        if not (biometric_attendance or manual_attendance):
            return render(request, 'access_denied.html', {'message': 'You must check in first.'})
        if request.user.role == 'EMPLOYEE':
            salaries = Salary.objects.filter(employee=request.user)
        elif request.user.role == 'HR_MANAGER':
            salaries = Salary.objects.filter(
                employee__department=request.user.department
            ).exclude(employee__role__in=['MANAGER', 'OVERALL_ADMIN'])
        elif request.user.role == 'MANAGER':
            salaries = Salary.objects.filter(
                employee__department=request.user.department
            ).exclude(employee__role='OVERALL_ADMIN')
        else:
            salaries = Salary.objects.all()

        for salary in salaries:
            employee = salary.employee
            # Default permissions
            salary.can_edit = False
            salary.can_delete = False

            if request.user.role == 'OVERALL_ADMIN':
                salary.can_edit = True
                salary.can_delete = True
            elif request.user.role == 'MANAGER':
                if employee.department == request.user.department and employee != request.user:
                    salary.can_edit = True
                    salary.can_delete = True
            elif request.user.role == 'HR_MANAGER':
                if employee.department == request.user.department and employee.role not in ['MANAGER', 'OVERALL_ADMIN']:
                    salary.can_edit = True
                    # HR_MANAGERs don't get delete rights
        months = [

            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]

        context = {
            'salaries': salaries,
            'now': datetime.now(),
            'months': months,
        }

        return render(request, 'salary_list.html', context)
    except Exception as e:
        logger.error(f"An Error Occured: {e}")
        messages.error(
            request, "error occured")

        return redirect('create_salary')


@login_required
def edit_salary(request, salary_id):
    if not request.user.is_authenticated:
        return redirect('/login')
    try:

        biometric_attendance = BiometricAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()
        manual_attendance = ManualAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()

        if not (biometric_attendance or manual_attendance):
            return render(request, 'access_denied.html', {'message': 'You must check in first.'})
        salary = get_object_or_404(Salary, id=salary_id)
        target_user = salary.employee

        if request.user == target_user:
            messages.error(request, "You cannot edit your own salary.")
            return redirect('salary_list')

        if request.user.role in ['HR_MANAGER', 'MANAGER']:
            if request.user.department != target_user.department or \
                    (target_user.role == 'MANAGER' and request.user.role == 'HR_MANAGER'):
                messages.error(
                    request, "You do not have permission to edit this salary.")
                return redirect('salary_list')

        if request.user.role != 'OVERALL_ADMIN' and target_user.role == 'OVERALL_ADMIN':
            messages.error(
                request, "You cannot edit the Overall Admin's salary.")
            return redirect('salary_list')

        if request.method == 'POST':
            form = SalaryForm(request.POST, instance=salary)
            if form.is_valid():
                salary = form.save(commit=False)

              # Recalculate salary as in create view...
            # Save and notify
                Notification.notify_user(
                    recipient=target_user,
                    message=f"Your salary record has been updated by {request.user.name}.")
                messages.success(request, "Salary updated successfully.")
                return redirect('salary_list')
        else:
            form = SalaryForm(instance=salary)

        return render(request, 'edit_salary.html', {'form': form, 'target_user': target_user})
    except Exception as e:
        logger.error(f"An Error Occured: {e}")

        messages.error(
            request, "An Error Occured")

        return redirect('edit_salary')


@login_required
def delete_salary(request, salary_id):
    try:
        user = request.user
        if not user.is_authenticated:
            return redirect('/login')
        biometric_attendance = BiometricAttendance.objects.filter(
            employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()
        manual_attendance = ManualAttendance.objects.filter(
            employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()

        if not (biometric_attendance or manual_attendance):
            return render(request, 'access_denied.html', {'message': 'You must check in first.'})
        salary = get_object_or_404(Salary, id=salary_id)
        target_user = salary.employee

        # Prevent self-deletion
        if request.user == target_user:
            messages.error(
                request, "You cannot delete your own salary record.")
            return redirect('salary_list')

        # Check delete permissions
        can_delete = False

        if request.user.role == 'OVERALL_ADMIN':
            can_delete = True
        elif request.user.role == 'MANAGER':
            if target_user.department == request.user.department and target_user != request.user:
                can_delete = True

        if not can_delete:
            messages.error(
                request, "You are not authorized to delete this salary.")
            return redirect('salary_list')

        salary.delete()
        messages.success(request, "Salary deleted successfully.")
        return redirect('salary_list')

    except Exception as e:
        logger.error(f"An Error Occured: {e}")
        messages.error(
            request, "error occured")

        return redirect('delete_salary')


# ///


@login_required
@user_passes_test(is_allowed_to_create_user)
def create_employee(request, user_id):
    if not request.user.is_authenticated:
        return redirect('/login')
    try:

        biometric_attendance = BiometricAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()
        manual_attendance = ManualAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()

        if not (biometric_attendance or manual_attendance):
            return render(request, 'access_denied.html', {'message': 'You must check in first.'})
        target_user = get_object_or_404(CustomUser, id=user_id)

        if request.user == target_user:
            messages.error(
                request, "You cannot create an employee for yourself.")
            return redirect('employee_list')

        if target_user.role != CustomUser.EMPLOYEE:
            messages.error(
                request, "You can only create an employee for a user with the EMPLOYEE role.")
            return redirect('employee_list')

        if hasattr(target_user, 'employees'):
            messages.warning(
                request, 'This user already has an employee record.')
            return redirect('employee_list')

        if request.user.role in [CustomUser.HR_MANAGER, CustomUser.MANAGER]:
            if request.user.department != target_user.department:
                messages.error(
                    request, "You can only create an employee for users in your department.")
                return redirect('employee_list')

        if request.method == 'POST':
            form = EmployeeRecordForm(request.POST)
            if form.is_valid():
                employee_record = form.save(commit=False)
                employee_record.user = target_user
                employee_record.net_salary = employee_record.basic_salary + (
                    employee_record.overtime_hours * 20
                ) + employee_record.bonuses - employee_record.deductions
                employee_record.department = target_user.department

                employee_record.save()

                Notification.notify_user(
                    recipient=target_user,
                    message=f"Your employee record has been successfully created by {request.user.name}."
                )

                Notification.notify_user(
                    recipient=request.user,
                    message=f"You have successfully created an employee record for {target_user.name}."
                )

                messages.success(
                    request, 'Employee record created successfully.')
                return redirect('employee_list')
        else:
            form = EmployeeRecordForm()

        return render(request, 'create_employee.html', {'form': form, 'target_user': target_user})
    except Exception as e:
        logger.error(f"An Error Occured: {e}")
        messages.error(
            request, "An Error Occured")

        return redirect('create_employee')


@login_required
def view_employee(request, employee_id):
    salary = get_object_or_404(EmployeeRecord, id=employee_id)
    return render(request, 'view_employee.html', {'salary': salary})


@login_required
def employee_list(request):
    users = CustomUser.objects.filter(role=CustomUser.EMPLOYEE)
    users = users.exclude(employees__isnull=False)
    if request.user.role in [CustomUser.HR_MANAGER, CustomUser.MANAGER]:
        users = users.filter(department=request.user.department)
    if not users.exists():
        messages.info(request, 'No eligible users found.')
    return render(request, 'eligible_users.html', {'users': users})


@login_required
def employee_record_list(request):
    employee_records = EmployeeRecord.objects.all()

    if request.user.role in [CustomUser.HR_MANAGER, CustomUser.MANAGER]:
        employee_records = employee_records.filter(
            user__department=request.user.department)

    if not employee_records.exists():
        messages.info(request, 'No employee records found.')

    return render(request, 'employee_record_list.html', {'employee_records': employee_records})


@login_required
def edit_employee_record(request, record_id):
    record = get_object_or_404(EmployeeRecord, id=record_id)

    if request.user.role in [CustomUser.HR_MANAGER, CustomUser.MANAGER]:
        if record.user.department != request.user.department:
            messages.error(
                request, "You're not allowed to edit records from another department.")
            return redirect('employee_record_list')

    if request.method == 'POST':
        form = EmployeeRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, "Employee record updated successfully.")
            return redirect('employee_record_list')
    else:
        form = EmployeeRecordForm(instance=record)

    return render(request, 'edit_record.html', {'form': form, 'record': record})


@login_required
@user_passes_test(is_allowed_to_create_user)
def delete_employee_record(request, record_id):
    record = get_object_or_404(EmployeeRecord, id=record_id)

    if request.user.role in [CustomUser.HR_MANAGER, CustomUser.MANAGER]:
        if record.user.department != request.user.department:
            messages.error(
                request, "You're not allowed to delete records from another department.")
            return redirect('employee_record_list')

    if request.method == 'POST':
        record.delete()
        messages.success(request, "Employee record deleted successfully.")
        return redirect('employee_record_list')

    return render(request, 'confirm_delete.html', {'record': record})


@login_required
def user_list(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    search_query = request.GET.get('search', '')

    if search_query:
        users = CustomUser.objects.filter(
            Q(name__icontains=search_query) | Q(role__icontains=search_query)
        )
    else:
        users = CustomUser.objects.all()

    return render(request, 'user_list.html', {'users': users})
# ///////////////

# Leave Requests


def create_leave_request(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    try:

        biometric_attendance = BiometricAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()
        manual_attendance = ManualAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()

        if not (biometric_attendance or manual_attendance):
            return render(request, 'access_denied.html', {'message': 'You must check in first.'})
        if not isinstance(request.user, CustomUser):
            messages.error(
                request, "You are not authorized to create a leave request.")
            return render(request, "index.html")

        form = LeaveRequestForm(request.POST or None)

        if request.method == 'POST' and form.is_valid():
            leave = form.save(commit=False)
            leave.employee = request.user

            current_month = leave.start_date.month
            current_year = leave.start_date.year
            has_existing_leave = LeaveRequest.objects.filter(
                employee=request.user,
                start_date__year=current_year,
                start_date__month=current_month
            ).exists()

            if has_existing_leave:
                messages.error(
                    request, "You have already submitted a leave request this month.")
            else:
                leave.status = LeaveRequest.PENDING

                reviewer = None
                if request.user.role == CustomUser.HR_MANAGER:
                    reviewer = CustomUser.objects.filter(
                        role=CustomUser.MANAGER,
                        department=request.user.department
                    ).exclude(id=request.user.id).first()
                elif request.user.role == CustomUser.MANAGER:
                    reviewer = CustomUser.objects.filter(
                        role=CustomUser.OVERALL_ADMIN).exclude(id=request.user.id).first()
                else:
                    reviewer = CustomUser.objects.filter(
                        role=CustomUser.HR_MANAGER,
                        department=request.user.department
                    ).exclude(id=request.user.id).first()

                if not reviewer:
                    reviewer = CustomUser.objects.filter(
                        role=CustomUser.OVERALL_ADMIN).first()

                if reviewer:
                    leave.current_reviewer = reviewer
                    leave.save()

                    message = f"Your leave request has been submitted and is pending approval."
                    Notification.notify_user(
                        recipient=leave.employee, message=message)

                    reviewer_message = f"You have a pending leave request from {leave.employee.name} to review."
                    Notification.notify_user(
                        recipient=reviewer, message=reviewer_message)

                    messages.success(
                        request, 'Leave request submitted and is pending approval.')

                    if request.headers.get("Hx-Request"):
                        return HttpResponse(render_to_string("success_message.html", {
                            "messages": messages.get_messages(request)
                        }))
                    return render(request, 'my_leaves.html')
                else:
                    messages.error(
                        request, 'No reviewer available to process your request.')

        context = {'form': form}

        template = "leave_form.html" if request.headers.get(
            "Hx-Request") else "create_leave.html"
        return render(request, template, context)
    except Exception as e:
        logger.error(f"An Error Occured: {e}")
        messages.error(
            request, "An Error Occured")

        return redirect('create_leave')


@login_required
def approve_leave_request(request, leave_id):
    try:
        if not request.user.is_authenticated:
            return redirect('/login')

        biometric_attendance = BiometricAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()
        manual_attendance = ManualAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()

        if not (biometric_attendance or manual_attendance):
            return render(request, 'access_denied.html', {'message': 'You must check in first.'})
        leave = get_object_or_404(LeaveRequest, id=leave_id)

        if leave.employee == request.user:
            messages.error(
                request, "You can't approve your own leave request.")
            return redirect('pending_leave_requests')

        if leave.status in [LeaveRequest.REJECTED, LeaveRequest.FINAL_APPROVED]:
            messages.warning(
                request, "This request has already been processed.")
            return redirect('pending_leave_requests')

        if request.user.role == CustomUser.HR_MANAGER:
            if request.user.department != leave.employee.department:
                messages.error(
                    request, "You are not authorized to approve this request.")
                return redirect('pending_leave_requests')

            leave.hr_approved = True
            leave.status = LeaveRequest.HR_APPROVED

            # Escalate to Manager
            next_reviewer = CustomUser.objects.filter(
                role=CustomUser.MANAGER,
                department=leave.employee.department
            ).exclude(id=leave.employee.id).first()
            leave.current_reviewer = next_reviewer
            Notification.notify_user(
                recipient=next_reviewer,
                message=f"Leave request from {leave.employee.name} needs your final approval.")

        elif request.user.role == CustomUser.MANAGER:
            if request.user.department != leave.employee.department:
                messages.error(
                    request, "You are not authorized to approve this request.")
                return redirect('pending_leave_requests')

            leave.manager_approved = True
            leave.status = LeaveRequest.FINAL_APPROVED
            leave.current_reviewer = None
            Notification.notify_user(
                recipient=leave.employee,
                message="Your leave request has been fully approved!")

        elif request.user.role == CustomUser.OVERALL_ADMIN and leave.employee.role == CustomUser.MANAGER:
            leave.manager_approved = True
            leave.status = LeaveRequest.FINAL_APPROVED
            leave.current_reviewer = None
            Notification.notify_user(
                recipient=leave.employee,
                message="Your leave request has been approved by the admin!")

        else:
            messages.error(
                request, "You are not authorized to approve this request.")
            return redirect('pending_leave_requests')

        leave.reviewed_at = timezone.now()
        leave.save()
        messages.success(request, "Leave request approved successfully.")
        return redirect('pending_leave_requests')
    except Exception as e:
        logger.error(f"An Error Occured: {e}")
        messages.error(
            request, "An Error Occured")

        return redirect('approve_leave_request')


@login_required
def decline_leave_request(request, leave_id):
    try:
        if not request.user.is_authenticated:
            return redirect('/login')

        biometric_attendance = BiometricAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()
        manual_attendance = ManualAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()

        if not (biometric_attendance or manual_attendance):
            return render(request, 'access_denied.html', {'message': 'You must check in first.'})
        leave = get_object_or_404(LeaveRequest, id=leave_id)

        if leave.employee == request.user:
            messages.error(request, "You can't reject your own leave request.")
            return redirect('pending_leave_requests')

        if request.user.role not in [CustomUser.HR_MANAGER, CustomUser.MANAGER, CustomUser.OVERALL_ADMIN]:
            messages.error(
                request, "You are not authorized to reject this request.")
            return redirect('pending_leave_requests')

        leave.status = LeaveRequest.REJECTED
        leave.current_reviewer = None
        leave.reviewed_at = timezone.now()
        leave.save()

        Notification.notify_user(
            recipient=leave.employee,
            message="Your leave request has been rejected."
        )

        messages.success(request, "Leave request rejected.")
        return redirect('pending_leave_requests')

    except Exception as e:
        logger.error(f"An Error Occured: {e}")
        messages.error(
            request, "An Error Occured")

        return redirect('decline_leave_request')


@login_required
def pending_leave_requests(request):

    try:
        user = request.user
        if not user.is_authenticated:
            return redirect('/login')
        biometric_attendance = BiometricAttendance.objects.filter(
            employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()
        manual_attendance = ManualAttendance.objects.filter(
            employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()

        if not (biometric_attendance or manual_attendance):
            return render(request, 'access_denied.html', {'message': 'You must check in first.'})
        if user.role not in [CustomUser.OVERALL_ADMIN, CustomUser.MANAGER, CustomUser.HR_MANAGER]:
            messages.error(
                request, "You do not have permission to view this page.")
            return redirect('ontech_dashboard')

        pending_requests = LeaveRequest.objects.none()

        if user.role == CustomUser.HR_MANAGER:
            pending_requests = LeaveRequest.objects.filter(
                status=LeaveRequest.PENDING,
                current_reviewer=user,
                employee__department=user.department
            ).exclude(employee=user)

        elif user.role == CustomUser.MANAGER:
            pending_requests = LeaveRequest.objects.filter(
                current_reviewer=user,
                employee__department=user.department
            ).exclude(employee=user).filter(
                Q(status=LeaveRequest.PENDING) | Q(
                    status=LeaveRequest.HR_APPROVED)
            )

        elif user.role == CustomUser.OVERALL_ADMIN:
            pending_requests = LeaveRequest.objects.filter(
                status=LeaveRequest.HR_APPROVED,
                current_reviewer=user
            ).exclude(employee=user)

        return render(request, 'leaves/pending_leave_requests.html', {
            'pending_requests': pending_requests
        })

    except Exception as e:

        logger.error(f"Error loading pending leave requests: {e}")
        messages.error(
            request, "An error occurred while loading pending requests.")
        return redirect('/')


@login_required
def my_leave_requests(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('/login')
    try:
        biometric_attendance = BiometricAttendance.objects.filter(
            employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()
        manual_attendance = ManualAttendance.objects.filter(
            employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()

        if not (biometric_attendance or manual_attendance):
            return render(request, 'access_denied.html', {'message': 'You must check in first.'})

        leaves = LeaveRequest.objects.filter(
            employee=user).order_by('-submitted_at')
        return render(request, 'my_leave_requests.html', {'leaves': leaves})
    except Exception as e:
        logger.error(f"An Error Occured: {e}")
        messages.error(
            request, "An Error Occured")

        return redirect('my_leave_requests')


@login_required
def delete_leave_request(request, leave_id):
    if not request.user.is_authenticated:
        return redirect('/login')
    try:

        biometric_attendance = BiometricAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()
        manual_attendance = ManualAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()

        if not (biometric_attendance or manual_attendance):
            return render(request, 'access_denied.html', {'message': 'You must check in first.'})
        leave = get_object_or_404(
            LeaveRequest, id=leave_id, employee=request.user)
        if leave.status == LeaveRequest.PENDING:
            leave.delete()
            messages.success(request, "Leave request deleted successfully.")
        else:
            messages.error(
                request, "You can only delete leave requests that are still pending.")
        return redirect('my_leave_requests')
    except Exception as e:
        logger.error(f"An Error Occured: {e}")
        messages.error(
            request, "An Error Occured")

        return redirect('my_leave_requests')


@login_required
def all_leave_requests_admin(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    if request.user.role != 'Overall_Admin':
        messages.error(request, "You are not authorized to view this page.")
        return redirect('home')
    all_requests = LeaveRequest.objects.all().order_by('-start_date')
    return render(request, 'admin_all_leaves.html', {'leaves': all_requests})


@login_required
def department_leave_requests(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    if request.user.role not in ['Hr_Manager', 'Manager', ]:
        messages.error(request, "You are not authorized to view this page.")
        return redirect('home')

    dept = request.user.department
    dept_leaves = LeaveRequest.objects.filter(
        employee__department=dept).order_by('-start_date')
    return render(request, 'department_leaves.html', {'leaves': dept_leaves})


# Performance Review
@login_required
@user_passes_test(is_allowed_to_create_performance)
def create_review(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    try:

        biometric_attendance = BiometricAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()
        manual_attendance = ManualAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()

        if not (biometric_attendance or manual_attendance):
            return render(request, 'access_denied.html', {'message': 'You must check in first.'})
        if request.method == 'POST':
            form = PerformanceReviewForm(
                request.POST, request_user=request.user)
            if form.is_valid():
                review = form.save()
                Notification.notify_user(
                    recipient=review.employee,
                    message=f"You have received a new performance review from {review.reviewer.name}-{review.reviewer.role}."
                )
                messages.success(
                    request, 'Performance Review Created Successfully.')
                return redirect('get_performance_reviews')

        else:
            form = PerformanceReviewForm(request_user=request.user)
        return render(request, 'create_review.html', {'form': form})
    except Exception as e:
        logger.error(f"An Error Occured: {e}")
        messages.error(
            request, "An Error Occured")

        return redirect('create_reviews')


@login_required
def get_performance_reviews(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    try:
        user = request.user

        biometric_attendance = BiometricAttendance.objects.filter(
            employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()
        manual_attendance = ManualAttendance.objects.filter(
            employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()

        if not (biometric_attendance or manual_attendance):
            return render(request, 'access_denied.html', {'message': 'You must check in first.'})
        if user.role == CustomUser.OVERALL_ADMIN:
            reviews = PerformanceReview.objects.all()
        elif user.role in [CustomUser.MANAGER, CustomUser.HR_MANAGER]:
            reviews = PerformanceReview.objects.filter(
                employee__department=user.department)
        elif user.role == CustomUser.EMPLOYEE:
            reviews = PerformanceReview.objects.filter(employee=user)
        else:
            reviews = PerformanceReview.objects.none()
        return render(request, 'performance_reviews.html', {'reviews': reviews})
    except Exception as e:
        logger.error(f"An Error Occured: {e}")
        messages.error(
            request, "An Error Occured")

        return redirect('get_performance_reviews')


# Tax Deduction
@login_required
@user_passes_test(is_allowed_to_create_salaries)
def create_tax_deduction(request, employee_id):
    if not request.user.is_authenticated:
        return redirect('/login')
    try:

        biometric_attendance = BiometricAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()
        manual_attendance = ManualAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()

        if not (biometric_attendance or manual_attendance):
            return render(request, 'access_denied.html', {'message': 'You must check in first.'})
        employee = get_object_or_404(CustomUser, id=employee_id)

        if request.method == 'POST':
            form = TaxDeductionForm(
                request.POST, request_user=request.user, employee=employee)
            if form.is_valid():
                deduction = form.save(commit=False)
                deduction.employee = employee
                deduction._creator = request.user
                deduction.total_deductions = deduction.calculate_total_deductions()
                deduction.save()

                # Notify the employee that their tax deduction has been created/updated
                message = f"Your tax deduction has been updated. Total deductions: {deduction.total_deductions}."
                Notification.notify_user(recipient=employee, message=message)

                if request.headers.get("HX-Request"):
                    updated_list = render_to_string('deduction_list_partial.html', {
                        'deductions': get_user_deductions(request.user)
                    })
                    return JsonResponse({
                        'message': '<div class="alert alert-success">Deduction added successfully.</div>',
                        'updatedList': updated_list
                    })

        else:
            form = TaxDeductionForm(
                request_user=request.user, employee=employee)

        template = 'tax_deduction_form_partial.html' if request.headers.get(
            "HX-Request") else 'tax_deduction_form.html'
        return render(request, template, {'form': form, 'employee': employee})
    except Exception as e:
        logger.error(f"An Error Occured: {e}")
        messages.error(
            request, "An Error Occured")

        return redirect('create_tax_deductions')


def get_user_deductions(user):
    if not user.is_authenticated:
        return redirect('/login')
    try:
        if user.role == CustomUser.OVERALL_ADMIN:
            return TaxDeduction.objects.all()
        elif user.role == CustomUser.MANAGER:
            return TaxDeduction.objects.filter(employee__department=user.department)
        elif user.role == CustomUser.HR_MANAGER:
            return TaxDeduction.objects.filter(employee__department=user.department)
        return TaxDeduction.objects.filter(employee=user)
    except Exception as e:
        logger.error(f"An Error Occured: {e}")
        return HttpResponse({'error': str(e)}, status=500)


def get_tax_deductions(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    try:
        deductions = get_user_deductions(request.user)

        print("HTMX Request: ", request.headers.get(
            "HX-Request"))  # Debugging line

        if request.headers.get("HX-Request"):
            return render(request, 'deduction_list_partial.html', {'deductions': deductions})

        return render(request, 'deductions.html', {'deductions': deductions})
    except Exception as e:
        messages.error(
            request, "An Error Occured")

        return redirect('get_tax_deductions')


def view_tax_deductions(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    try:
        user = request.user

        # Initial deduction query
        if user.role == CustomUser.OVERALL_ADMIN:
            deductions = TaxDeduction.objects.select_related('employee')
        elif user.role in [CustomUser.MANAGER, CustomUser.HR_MANAGER]:
            deductions = TaxDeduction.objects.select_related('employee').filter(
                employee__department=user.department
            )
        else:  # Employee
            deductions = TaxDeduction.objects.select_related(
                'employee').filter(employee=user)

        search_query = request.GET.get('search', '')
        if search_query:
            deductions = deductions.filter(
                Q(employee__name__icontains=search_query) | Q(
                    employee__department__icontains=search_query)
            )

        if request.headers.get("HX-Request"):
            return render(request, 'deduction_list.html', {'deductions': deductions})

        return render(request, 'view_deductions.html', {'deductions': deductions})
    except Exception as e:
        logger.error(f"An Error Occured: {e}")
        messages.error(
            request, "An Error Occured")

        return redirect('view_tax_deductions')
# Users List


@login_required
def my_tax_deduction_view(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('/login')
    try:

        biometric_attendance = BiometricAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()
        manual_attendance = ManualAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()

        if not (biometric_attendance or manual_attendance):
            return render(request, 'access_denied.html', {'message': 'You must check in first.'})
        profile = user.user_profile
    except Profile.DoesNotExist:
        messages.error(request, 'Profile not found. Please create a profile first.')
        return redirect( '/view/profile')

    tax = TaxDeduction.objects.filter(employee=user).first()
    if not tax:
        return render(request, 'no_tax_deduction.html')

    context = {
        'user': user,
        'profile': profile,
        'tax': tax
    }
    return render(request, 'my_tax_deduction.html', context)


@login_required
@user_passes_test(is_admin_or_manager)
def all_tax_deductions_view(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('/login')
    biometric_attendance = BiometricAttendance.objects.filter(
        employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
    ).first()
    manual_attendance = ManualAttendance.objects.filter(
        employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
    ).first()

    if not (biometric_attendance or manual_attendance):
        return render(request, 'access_denied.html', {'message': 'You must check in first.'})

    deductions = TaxDeduction.objects.select_related('employee')
    tax_list = []

    for tax in deductions:
        try:
            profile = tax.employee.user_profile
            tax_list.append({
                'user': tax.employee,
                'profile': profile,
                'tax': tax
            })
        except Profile.DoesNotExist:
            continue

    context = {
        'tax_list': tax_list
    }
    return render(request, 'all_tax_deductions.html', context)


@login_required
def user_list_view(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    try:
        user = request.user

        biometric_attendance = BiometricAttendance.objects.filter(
            employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()
        manual_attendance = ManualAttendance.objects.filter(
            employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()

        if not (biometric_attendance or manual_attendance):
            return render(request, 'access_denied.html', {'message': 'You must check in first.'})
        if user.role == CustomUser.OVERALL_ADMIN:
            users = CustomUser.objects.select_related('user_profile').all()
        elif user.role in [CustomUser.MANAGER, CustomUser.HR_MANAGER]:
            users = CustomUser.objects.select_related(
                'user_profile').filter(department=user.department)
        else:
            return redirect('user_profile', user_id=user.id)
        return render(request, 'users_list.html', {'users': users})
    except Exception as e:
        logger.error(f"An Error Occured: {e}")
        messages.error(
            request, "An Error Occured")

        return redirect('/dashboard')


@login_required
def user_profile_view(request, user_id):
    if not request.user.is_authenticated:
        return redirect('/login')
    try:

        biometric_attendance = BiometricAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()
        manual_attendance = ManualAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()

        if not (biometric_attendance or manual_attendance):
            return render(request, 'access_denied.html', {'message': 'You must check in first.'})
        profile_user = get_object_or_404(CustomUser, id=user_id)
        profile = Profile.objects.get_or_create(user=profile_user)

        if not profile:
            messages.error(request, 'Profile not found.')
            return redirect('user_list')

        if request.headers.get('HX-Request'):
            html = render_to_string('user_profile.html', {
                'profile_user': profile_user,
                'profile': profile
            }, request=request)
            return HttpResponse(html)

        return render(request, 'user_profile.html', {
            'profile_user': profile_user,
            'profile': profile
        })
    except Exception as e:
        logger.error(f"An Error Occured: {e}")
        messages.error(
            request, "An Error Occured")

        return redirect('/dashboard')


# Leave Balance
@login_required
@user_passes_test(is_allowed_to_create_leave_balance)
def update_leave_balance(request, employee_id):
    if not request.user.is_authenticated:
        return redirect('/login')
    try:

        biometric_attendance = BiometricAttendance.objects.filter(
            employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()
        manual_attendance = ManualAttendance.objects.filter(
            employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()

        if not (biometric_attendance or manual_attendance):
            return render(request, 'access_denied.html', {'message': 'You must check in first.'})
        employee = get_object_or_404(CustomUser, id=employee_id)

        # Get or create the balance record
        leave_balance, _ = LeaveBalance.objects.get_or_create(
            employee=employee)

        if request.method == 'POST':
            form = LeaveBalanceForm(
                request.POST, instance=leave_balance, request_user=request.user, employee=employee
            )
            if form.is_valid():
                obj = form.save(commit=False)
                obj._creator = request.user
                obj.save()
                messages.success(
                    request, 'Leave balance updated successfully.')
                return redirect("view_leave_balances")
        else:
            form = LeaveBalanceForm(instance=leave_balance,
                                    request_user=request.user, employee=employee)

        return render(request, 'update_leave_balance.html', {
            'form': form,
            'employee': employee
        })
    except Exception as e:
        logger.error(f"An Error Occured: {e}")
        messages.error(
            request, "An Error Occured")

        return redirect('update_leave_balance')


@login_required
def view_leave_balances(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    try:
        user = request.user

        biometric_attendance = BiometricAttendance.objects.filter(
            employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()
        manual_attendance = ManualAttendance.objects.filter(
            employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()

        if not (biometric_attendance or manual_attendance):
            return render(request, 'access_denied.html', {'message': 'You must check in first.'})
        if user.role == CustomUser.OVERALL_ADMIN:
            balances = LeaveBalance.objects.select_related('employee').all()
        elif user.role == CustomUser.MANAGER:
            balances = LeaveBalance.objects.select_related(
                'employee').filter(employee__department=user.department)
        else:
            balances = LeaveBalance.objects.select_related(
                'employee').filter(employee=user)

        # Attach remaining leave values
        for balance in balances:
            balance.annual_remaining = balance.remaining_leave('ANNUAL')
            balance.sick_remaining = balance.remaining_leave('SICK')
            balance.casual_remaining = balance.remaining_leave('CASUAL')
            balance.unpaid_remaining = balance.remaining_leave('UNPAID')

        return render(request, 'leave_balance_list.html', {'balances': balances})
    except Exception as e:
        logger.error(f"An Error Occured: {e}")
        messages.error(
            request, "An Error Occured")

        return redirect('view_leave_balancs')


# Complaints
@login_required
def create_complaint(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    try:

        biometric_attendance = BiometricAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()
        manual_attendance = ManualAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()

        if not (biometric_attendance or manual_attendance):
            return render(request, 'access_denied.html', {'message': 'You must check in first.'})
        sender = request.user

        if request.method == 'POST':
            form = ComplaintForm(request.POST, initial={'sender': sender})
            if form.is_valid():
                subject = form.cleaned_data['subject']
                message = form.cleaned_data['message']

                recipients = []

                if sender.role == CustomUser.EMPLOYEE:
                    recipients = CustomUser.objects.filter(
                        role__in=[CustomUser.HR_MANAGER, CustomUser.MANAGER],
                        department=sender.department
                    )
                elif sender.role == CustomUser.HR_MANAGER:
                    recipients = CustomUser.objects.filter(
                        role=CustomUser.MANAGER,
                        department=sender.department
                    )
                elif sender.role == CustomUser.MANAGER:
                    # Manager must have selected an Overall Admin in the form
                    selected_manager = form.cleaned_data.get('manager')
                    if selected_manager and selected_manager.role == CustomUser.OVERALL_ADMIN:
                        recipients = [selected_manager]
                    else:
                        form.add_error(
                            'manager', "Manager must select an Admin.")
                        return render(request, 'create_complaint.html', {'form': form})

                # Add all Overall Admins (for all roles except Manager who selects manually)
                if sender.role in [CustomUser.EMPLOYEE, CustomUser.HR_MANAGER]:
                    recipients |= CustomUser.objects.filter(
                        role=CustomUser.OVERALL_ADMIN)

                # Create a complaint for each recipient
                for recipient in recipients:
                    Complaint.objects.create(
                        sender=sender,
                        manager=recipient,
                        subject=subject,
                        message=message
                    )
                    Notification.notify_user(
                        recipient,
                        f"You received a new complaint from {sender.name}."
                    )

                return redirect('create_complaint')  # or success page
        else:
            form = ComplaintForm(initial={'sender': sender})

        return render(request, 'create_complaint.html', {'form': form})
    except Exception as e:
        logger.error(f"An Error Occured: {e}")
        messages.error(
            request, "An Error Occured")

        return redirect('create_complaint')


@login_required
def complaint_list(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    try:
        user = request.user

        if user.role == CustomUser.OVERALL_ADMIN:
            complaints = Complaint.objects.all()

        elif user.role == CustomUser.MANAGER:
            complaints = Complaint.objects.filter(
                Q(sender__department=user.department, sender__role__in=[CustomUser.HR_MANAGER, CustomUser.EMPLOYEE]) |
                Q(sender=user)
            )

        elif user.role == CustomUser.HR_MANAGER:
            complaints = Complaint.objects.filter(
                Q(sender=user) |
                Q(sender__department=user.department,
                  sender__role=CustomUser.EMPLOYEE)
            )

        elif user.role == CustomUser.EMPLOYEE:
            complaints = Complaint.objects.filter(sender=user)

        else:
            complaints = Complaint.objects.none()

        return render(request, 'complaints_list.html', {'complaints': complaints})
    except Exception as e:
        logger.error(f"An Error Occured: {e}")
        messages.error(
            request, "An Error Occured")

        return redirect('complaint_list')


@login_required
def respond_to_complaint_view(request, pk):
    if not request.user.is_authenticated:
        return redirect('/login')
    try:

        biometric_attendance = BiometricAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()
        manual_attendance = ManualAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()

        if not (biometric_attendance or manual_attendance):
            return render(request, 'access_denied.html', {'message': 'You must check in first.'})
        complaint = get_object_or_404(Complaint, pk=pk)

        # 1. Only allow response if not already answered
        if complaint.is_answered():
            raise PermissionDenied("This complaint has already been answered.")

        user = request.user

        # 2. Role-based restrictions
        if user.role == CustomUser.OVERALL_ADMIN:
            pass  # can respond to all

        elif user.role == CustomUser.MANAGER:
            if complaint.sender == user:
                raise PermissionDenied("You cannot answer your own complaint.")
            if complaint.sender.department != user.department:
                raise PermissionDenied(
                    "You can only respond to complaints in your department.")
            if complaint.sender.role not in [CustomUser.EMPLOYEE, CustomUser.HR_MANAGER]:
                raise PermissionDenied(
                    "You can only respond to employee or HR complaints.")

        elif user.role == CustomUser.HR_MANAGER:
            if complaint.sender.role != CustomUser.EMPLOYEE:
                raise PermissionDenied(
                    "HR can only respond to employee complaints.")
            if complaint.sender.department != user.department:
                raise PermissionDenied(
                    "Only handle complaints from your department.")

        else:
            raise PermissionDenied(
                "You are not allowed to respond to complaints.")

        if request.method == 'POST':
            response = request.POST.get('manager_response', '').strip()
            if len(response) < 10:
                return render(request, 'respond.html', {
                    'complaint': complaint,
                    'error': "Response must be at least 10 characters."
                })

            complaint.manager_response = response
            complaint.response_submitted_by = user
            complaint.response_submitted_at = timezone.now()
            complaint.save()

            # Notify the complaint sender (employee/HR)
            Notification.notify_user(
                recipient=complaint.sender,
                message=f"Your complaint has been responded to by {user.name}."
            )

            messages.success(request, 'Response submitted successfully.')
            return redirect('complaint_list')

        return render(request, 'respond.html', {'complaint': complaint})
    except Exception as e:
        logger.error(f"An Error Occured: {e}")
        messages.error(
            request, "An Error Occured")

        return redirect('complaint_list')


@login_required
def reply_to_complaint_view(request, pk):
    if not request.user.is_authenticated:
        return redirect('/login')
    try:

        biometric_attendance = BiometricAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()
        manual_attendance = ManualAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()

        if not (biometric_attendance or manual_attendance):
            return render(request, 'access_denied.html', {'message': 'You must check in first.'})
        complaint = get_object_or_404(Complaint, pk=pk)

        if request.user != complaint.sender:
            return HttpResponseForbidden("You can only reply to your own complaints.")

        if not complaint.manager_response:
            return render(request, 'complaints_reply.html', {
                'complaint': complaint,
                'error': 'You can only reply after receiving a manager response.'
            })

        if complaint.user_reply:
            return render(request, 'complaints_reply.html', {
                'complaint': complaint,
                'error': 'You have already submitted a reply.'
            })

        if request.method == 'POST':
            reply_text = request.POST.get('user_reply', '').strip()
            if len(reply_text) < 5:
                return render(request, 'complaints_reply.html', {
                    'complaint': complaint,
                    'error': 'Reply must be at least 5 characters.'
                })
            complaint.user_reply = reply_text
            complaint.user_reply_submitted_at = timezone.now()
            complaint.reply_viewed_by_manager = False
            complaint.save()

            Notification.notify_user(
                recipient=complaint.response_submitted_by,
                message=f"{complaint.sender.name} has replied to your response on their complaint."
            )

            messages.success(request, 'Reply submitted successfully.')
            return redirect('complaint_list')

        return render(request, 'complaints_reply.html', {'complaint': complaint})
    except Exception as e:
        logger.error(f"An Error Occured: {e}")
        messages.error(
            request, "An Error Occured")

        return redirect('complaint_list')


@login_required
def task_list(request):
    try:
        user = request.user
        tasks = []
        assigned_tasks = []
        if not user.is_authenticated:
            return redirect('/login')

        if user.role == CustomUser.OVERALL_ADMIN:
            # Overall_Admin can view all tasks
            tasks = Task.objects.filter(status__in=['pending', 'in_progress'])
            assigned_tasks = Task.objects.filter(
                assigned_by=user, status='submitted')
        else:
            # Check for active check-in
            biometric_attendance = BiometricAttendance.objects.filter(
                employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
            ).first()
            manual_attendance = ManualAttendance.objects.filter(
                employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
            ).first()

            if not (biometric_attendance or manual_attendance):
                return render(request, 'access_denied.html', {'message': 'You must check in first.'})

            # Fetch tasks assigned to the user
            tasks = Task.objects.filter(
                assigned_to=user,
                status__in=['pending', 'in_progress']
            ).filter(
                models.Q(biometric_attendance=biometric_attendance) | models.Q(
                    manual_attendance=manual_attendance)
            )

            # Fetch tasks assigned by the user for review
            if user.role in [CustomUser.HR_MANAGER, CustomUser.MANAGER]:
                assigned_tasks = Task.objects.filter(
                    assigned_by=user)

        can_assign_tasks = user.role in [
            CustomUser.HR_MANAGER, CustomUser.MANAGER, CustomUser.OVERALL_ADMIN]
        return render(request, 'task_list.html', {
            'tasks': tasks,
            'assigned_tasks': assigned_tasks,
            'user': user,
            'can_assign_tasks': can_assign_tasks
        })
    except Exception as e:

        logger.error(f"An Error Occured: {e}")
        messages.error(
            request, "An Error Occured")

        return redirect('ontech_dashboard')


@login_required
@user_passes_test(check_can_assign_tasks, login_url='/tasks/')
def task_create(request):
    try:
        user = request.user
        if not user.is_authenticated:
            return redirect('/login')

        # Only allow specific roles to assign tasks
        if user.role not in [CustomUser.HR_MANAGER, CustomUser.MANAGER, CustomUser.OVERALL_ADMIN]:
            return render(request, 'access_denied.html', {'message': 'You are not allowed to assign tasks.'})

        if request.method == 'POST':
            form = TaskForm(request.POST, user=user)
            if form.is_valid():
                task = form.save(commit=False)
                task.assigned_by = user
                task.save()
                return redirect('task_list')
        else:
            form = TaskForm(user=user)

        return render(request, 'task_form.html', {'form': form})
    except Exception as e:
        logger.error(f"An error occurred in create_task: {e}")
        messages.error(request, "An error occured")
        return render(request, 'task_form.html')


@login_required
@user_passes_test(check_can_review_tasks, login_url='/tasks/')
def task_review(request, task_id):
    try:
        if not request.user.is_authenticated:
            return redirect('/login')

        biometric_attendance = BiometricAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()
        manual_attendance = ManualAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()

        if not (biometric_attendance or manual_attendance):
            return render(request, 'access_denied.html', {'message': 'You must check in first.'})
        task = get_object_or_404(
            Task, id=task_id, assigned_by=request.user, )
        if request.method == 'POST':
            form = TaskReviewForm(request.POST, instance=task)
            if form.is_valid():
                task = form.save(commit=False)
                task.status = 'reviewed'
                task.save()
                return redirect('task_list')
        else:
            form = TaskReviewForm(instance=task)
        return render(request, 'task_review.html', {'form': form, 'task': task})
    except Exception as e:

        logger.error(f"An Error Occured: {e}")
        messages.error(
            request, "An Error Occured")

        return redirect('ontech_dashboard')


class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'task_form.html'
    success_url = urls.reverse_lazy('task_list')
    login_url = '/login'

    def get_form_kwargs(self):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("You must be logged in to create a task.")
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return self.success_url

    def form_valid(self, form):
        task = form.save(commit=False)
        task.assigned_by = self.request.user
        try:
            task.validate_assignment(request=self.request)
            task.save()

            # ✅ Notify the assigned user
            role_code = task.assigned_by.role
            role_display = dict(CustomUser.ROLE_CHOICES).get(
                role_code, role_code)  # fallback to raw code if not found

            message = f"You've been assigned a new task: '{task.title}' by {role_display}"
            Notification.notify_user(
                recipient=task.assigned_to, message=message)

            messages.success(
                self.request, 'Task created successfully and user notified.')
            return redirect(self.get_success_url())
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)


@login_required
def hr_employee_list(request):

    try:

        user = request.user
        if not user.is_authenticated:
            return redirect('/login')

        biometric_attendance = BiometricAttendance.objects.filter(
            employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()
        manual_attendance = ManualAttendance.objects.filter(
            employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()

        if not (biometric_attendance or manual_attendance):
            return render(request, 'access_denied.html', {'message': 'You must check in first.'})
        if user.role != [CustomUser.HR_MANAGER, CustomUser.OVERALL_ADMIN]:
            return render(request, 'access_denied.html', {"message": 'Access Denied'})

        employees = CustomUser.objects.filter(
            role=CustomUser.EMPLOYEE, department=user.department).select_related('user_profile')
        paignator = Paginator(employees, 6)
        page_number = request.GET.get('page')
        page_obj = paignator.get_page(page_number)
        return render(request, 'employee_list.html', {
            'page_obj': page_obj
        })
    except Exception as e:

        logger.error(f"An Error Occured: {e}")
        messages.error(
            request, "An Error Occured")

        return redirect('ontech_dashboard')


@login_required
def employee_profile_detail(request, pk):
    try:
        user = request.user
        if not user.is_authenticated:
            return redirect('/login')
        biometric_attendance = BiometricAttendance.objects.filter(
            employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()
        manual_attendance = ManualAttendance.objects.filter(
            employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()

        if not (biometric_attendance or manual_attendance):
            return render(request, 'access_denied.html', {'message': 'You must check in first.'})

        employee = get_object_or_404(
            CustomUser, pk=pk, role=CustomUser.EMPLOYEE)
        if user.role == CustomUser.OVERALL_ADMIN:
            pass

        if user.role == CustomUser.HR_MANAGER:
            if user.department != employee.department:
                return render(request, 'access_denied.html', {
                    'message': "You are not authorize to view this profile"
                })
        return render(request, "employee_detail.html", {
            'employee': employee
        })
    except Exception as e:

        logger.error(f"An Error Occured: {e}")
        messages.error(
            request, "An Error Occured")

        return redirect('ontech_dashboard')


@login_required
def manager_team_view(request):
    try:
        user = request.user
        if not user.is_authenticated:
            return redirect('/login')

        biometric_attendance = BiometricAttendance.objects.filter(
            employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()
        manual_attendance = ManualAttendance.objects.filter(
            employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()

        if not (biometric_attendance or manual_attendance):
            return render(request, 'access_denied.html', {'message': 'You must check in first.'})
        if user.role != [CustomUser.MANAGER, CustomUser.OVERALL_ADMIN]:

            return render(request, 'access_denied.html', {
                'message': 'You are not authorized to view this page.'
            })

        department = user.department

        # Team members in the same department
        hr_managers = CustomUser.objects.filter(
            role=CustomUser.HR_MANAGER, department=department)
        employees = CustomUser.objects.filter(
            role=CustomUser.EMPLOYEE, department=department)

        team_members = list(hr_managers) + list(employees)

        # Build a dict of user to profile (or None if missing)
        team_data = []
        for member in team_members:
            # Gracefully handles missing profiles
            profile = Profile.objects.filter(user=member).first()
            team_data.append({
                'user': member,
                'profile': profile
            })

        # Manager profile (optional fallback)
        manager_profile = Profile.objects.filter(user=user).first()

        return render(request, 'team_list.html', {
            'team_data': team_data,
            'manager_profile': manager_profile,
        })
    except Exception as e:

        logger.error(f"An Error Occured: {e}")
        messages.error(
            request, "An Error Occured")

        return redirect('ontech_dashboard')


@login_required
def send_message(request, user_id):
    try:
        if not request.user.is_authenticated:
            return redirect('/login')

        biometric_attendance = BiometricAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()
        manual_attendance = ManualAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()

        if not (biometric_attendance or manual_attendance):
            return render(request, 'access_denied.html', {'message': 'You must check in first.'})
        receiver = get_object_or_404(CustomUser, id=user_id)

        if receiver.role == CustomUser.OVERALL_ADMIN:
            return render(request, 'not_allowed.html')

        if request.method == 'POST':
            form = MessageForm(request.POST)
            if form.is_valid():
                message = form.save(commit=False)
                message.sender = request.user
                message.receiver = receiver
                message.save()
                return redirect('inbox')
        else:
            form = MessageForm(initial={'receiver': receiver})

        return render(request, 'send_message.html', {
            'form': form,
            'receiver': receiver
        })
    except Exception as e:

        logger.error(f"An Error Occured: {e}")
        messages.error(
            request, "An Error Occured")

        return redirect('ontech_dashboard')


@login_required
def inbox(request):
    try:
        if not request.user.is_authenticated:
            return redirect('/login')

        biometric_attendance = BiometricAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()
        manual_attendance = ManualAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()

        if not (biometric_attendance or manual_attendance):
            return render(request, 'access_denied.html', {'message': 'You must check in first.'})
        messages = Message.objects.filter(
            receiver=request.user).order_by('-sent_at')
        return render(request, 'inbox.html', {'messages': messages})
    except Exception as e:

        logger.error(f"An Error Occured: {e}")
        messages.error(
            request, "An Error Occured")

        return redirect('ontech_dashboard')


@login_required
def message_detail(request, message_id):
    if not request.user.is_authenticated:
        return redirect('/login')
    try:

        biometric_attendance = BiometricAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()
        manual_attendance = ManualAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()

        if not (biometric_attendance or manual_attendance):
            return render(request, 'access_denied.html', {'message': 'You must check in first.'})
        message = get_object_or_404(
            Message, id=message_id, receiver=request.user)

        if not message.is_read:
            message.is_read = True
            message.save()

        sender_role = dict(CustomUser.ROLE_CHOICES).get(
            message.sender.role, message.sender.role)

        return render(request, 'message_detail.html', {
            'message': message,
            'sender_role': sender_role
        })
    except Exception as e:

        logger.error(f"An Error Occured: {e}")
        messages.error(
            request, "An Error Occured")

        return redirect('ontech_dashboard')


@login_required
def unread_message_count(request):
    try:
        if not request.user.is_authenticated:
            return redirect('/login')
        user = request.user
        if not user.is_authenticated:
            return redirect('/login')
        biometric_attendance = BiometricAttendance.objects.filter(
            employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()
        manual_attendance = ManualAttendance.objects.filter(
            employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()

        if not (biometric_attendance or manual_attendance):
            return render(request, 'access_denied.html', {'message': 'You must check in first.'})
        count = Message.objects.filter(
            receiver=request.user, is_read=False).count()
        return JsonResponse({'unread_count': count})
    except Exception as e:

        logger.error(f"An Error Occured: {e}")
        messages.error(
            request, "An Error Occured")

        return redirect('ontech_dashboard')


@login_required
def monthy_attendance(request):
    try:
        if not request.user.is_authenticated:
            return redirect('/login')

        biometric_attendance = BiometricAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()
        manual_attendance = ManualAttendance.objects.filter(
            employee=request.user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()

        if not (biometric_attendance or manual_attendance):
            return render(request, 'access_denied.html', {'message': 'You must check in first.'})
        user = request.user
        role = user.role
        department = user.department
        month = request.GET.get('month')
        if not request.user.is_authenticated:
            return render(request, 'access_denied.html', {'message': 'You are not authorized to view this page.'})

        if not month:
            today = datetime.today()
            year = today.year
            month_int = today.month
        else:
            try:
                year, month_int = map(int, month.split("-")
                                      )
            except:
                return render(request, 'invalid_month.html')
        manual_attendance_qs = ManualAttendance.objects.filter(
            date__year=year, date__month=month_int)
        biometric_attendance_qs = BiometricAttendance.objects.filter(
            date__year=year, date__month=month_int)
        if role == 'Overall_Admin':
            pass
        elif role == 'Manager':
            manual_attendance_q = manual_attendance_qs.filter(Q(employee=user) | (
                Q(employee__department=department) & Q(employee__role__in=['Employee', 'Hr_Manager'])))
            biometric_attendance_q = biometric_attendance_qs.filter(Q(employee=user) | (
                Q(employee__department=department) & Q(employee__role__in=['Employee', 'Hr_Manager'])))
        elif role == 'Hr_Manager':
            manual_attendance_q = manual_attendance_qs.filter(
                Q(employee=user) |
                (Q(employee__department=department) & Q(employee__role='Employee'))
            )
            biometric_attendance_q = biometric_attendance_qs.filter(
                Q(employee=user) |
                (Q(employee__department=department) & Q(employee__role='Employee'))
            )
        elif role == 'Employee':
            manual_attendance_q = manual_attendance_qs.filter(employee=user)
            biometric_attendance_q = biometric_attendance_qs.filter(
                employee=user)
        context = {
            'manaual_attendance': manual_attendance_q,
            'biometric_attendance': biometric_attendance_q,
            'month': f"{year}-{month_int:02}"
        }
        return render(request, 'monthly_attendance.html', context)
    except Exception as e:

        logger.error(f"An Error Occured: {e}")
        messages.error(
            request, "An Error Occured")

        return redirect('ontech_dashboard')


@login_required
def team_review_list_view(request):
    try:
        user = request.user
        if not user.is_authenticated:
            return redirect('/login')

        biometric_attendance = BiometricAttendance.objects.filter(
            employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()
        manual_attendance = ManualAttendance.objects.filter(
            employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()

        if not (biometric_attendance or manual_attendance):
            return render(request, 'access_denied.html', {'message': 'You must check in first.'})
        reviews = TeamPerformanceReview.objects.all()

        # Filter by access level
        if user.role == CustomUser.OVERALL_ADMIN:
            pass
        elif user.role == CustomUser.MANAGER:
            reviews = reviews.filter(manager=user)
        else:
            reviews = reviews.filter(department=user.department)

        # Month/year filter from GET
        month = request.GET.get('month')
        year = request.GET.get('year')

        if month:
            reviews = reviews.filter(month__month=int(month))
        if year:
            reviews = reviews.filter(month__year=int(year))

        # Search filter
        search_query = request.GET.get('search')
        if search_query:
            reviews = reviews.filter(review_text__icontains=search_query)

        # Pagination
        paginator = Paginator(reviews, 5)  # 5 reviews per page
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        month_names = [(i, calendar.month_name[i]) for i in range(1, 13)]
        current_year = datetime.now().year
        current_month = datetime.now().month
        year_options = [current_year - i for i in range(5)]

        return render(request, 'team_review_list.html', {
            'page_obj': page_obj,
            'month': month,
            'year': year,
            'search_query': search_query,
            'month_names': month_names,
            'year_options': year_options,
            'current_month': current_month,
            'current_year': current_year,
        })
    except Exception as e:

        logger.error(f"An Error Occured: {e}")
        messages.error(
            request, "An Error Occured")

        return redirect('ontech_dashboard')


@login_required
def team_review_create_view(request):
    try:
        user = request.user
        if not user.is_authenticated:
            return redirect('/login')

        biometric_attendance = BiometricAttendance.objects.filter(
            employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()
        manual_attendance = ManualAttendance.objects.filter(
            employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()

        if not (biometric_attendance or manual_attendance):
            return render(request, 'access_denied.html', {'message': 'You must check in first.'})
        if user.role != CustomUser.MANAGER:
            return redirect('team-review-list')

        today = datetime.today()
        month_start = today.replace(day=1)

        if TeamPerformanceReview.objects.filter(manager=user, month__year=today.year, month__month=today.month).exists():
            return redirect('team-review-list')

        if request.method == 'POST':
            form = TeamPerformanceReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.manager = user
                review.department = user.department
                review.month = month_start
                review.save()

                # Notify HR Managers and Employees in the same department
                team_members = CustomUser.objects.filter(
                    department=user.department,
                    role__in=[CustomUser.HR_MANAGER, CustomUser.EMPLOYEE]
                )
                for member in team_members:
                    Notification.notify_user(
                        recipient=member,
                        message=f"A new team performance review for {user.department} has been posted by {user.role}."
                    )

                return redirect('team-review-list')
        else:
            form = TeamPerformanceReviewForm()

        return render(request, 'team_review_form.html', {'form': form})
    except Exception as e:

        logger.error(f"An Error Occured: {e}")
        messages.error(
            request, "An Error Occured")

        return redirect('ontech_dashboard')


@login_required
def view_all_leave_requests(request):
    try:
        user = request.user
        if not user.is_authenticated:
            return redirect('/login')

        biometric_attendance = BiometricAttendance.objects.filter(
            employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()
        manual_attendance = ManualAttendance.objects.filter(
            employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()

        if not (biometric_attendance or manual_attendance):
            return render(request, 'access_denied.html', {'message': 'You must check in first.'})

        if user.role == CustomUser.OVERALL_ADMIN:
            leaves = LeaveRequest.objects.select_related(
                'employee').all().order_by('-submitted_at')
        elif user.role in [CustomUser.HR_MANAGER, CustomUser.MANAGER]:
            leaves = LeaveRequest.objects.select_related('employee').filter(
                employee__department=user.department
            ).order_by('-submitted_at')
        else:
            leaves = LeaveRequest.objects.none()

        context = {
            'leaves': leaves,
            'user_role': user.role,
        }
        return render(request, 'leaves/leave_requests_list.html', context)
    except Exception as e:

        logger.error(f"An Error Occured: {e}")
        messages.error(
            request, "An Error Occured")

        return redirect('ontech_dashboard')


@login_required
def view_messages(request):
    try:
        user = request.user
        if not user.is_authenticated:
            return redirect('/login')

        biometric_attendance = BiometricAttendance.objects.filter(
            employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()
        manual_attendance = ManualAttendance.objects.filter(
            employee=user, date=timezone.now().date(), check_in__isnull=False, check_out__isnull=True
        ).first()

        if not (biometric_attendance or manual_attendance):
            return render(request, 'access_denied.html', {'message': 'You must check in first.'})
        if user.role != CustomUser.OVERALL_ADMIN:
            return render(request, 'access_denied.html', {'message': 'You are not authorized to view this page.'})
        messages = Message.objects.all().order_by('-sent_at')
        return render(request, 'view_messages.html', {'messages': messages})
    except Exception as e:

        logger.error(f"An Error Occured: {e}")
        messages.error(
            request, "An Error Occured")

        return redirect('ontech_dashboard')
