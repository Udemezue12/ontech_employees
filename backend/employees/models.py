import logging
from datetime import datetime, date, timedelta
from decimal import Decimal
import threading
from django.contrib import messages
from django.http import HttpResponse
from django.core.validators import MinValueValidator
from django.utils.dateformat import format
from django.core.exceptions import ValidationError
from typing import TYPE_CHECKING
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils.timezone import now
# from django.conf import settings
from django.dispatch import receiver
# from django.urls import reverse
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django_rest_passwordreset.signals import reset_password_token_created
from .doc import image, document


logger = logging.getLogger(__name__)


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    HR_MANAGER = 'Hr_Manager'
    EMPLOYEE = 'Employee'
    MANAGER = 'Manager'
    OVERALL_ADMIN = 'Overall_Admin'
    HR = 'Human Resources'
    ENGINEERING = 'Engineering'
    SALES = 'Sales'
    MARKETING = 'Marketing'

    ROLE_CHOICES = [
        (HR_MANAGER, 'Hr_Manager'),
        (MANAGER, 'Manager'),
        (EMPLOYEE, 'Employee'),
        (OVERALL_ADMIN, 'Overall_Admin'),
    ]

    DEPARTMENT_CHOICES = [
        (HR, 'Human Resources'),
        (ENGINEERING, 'Engineering'),
        (SALES, 'Sales'),
        (MARKETING, 'Marketing'),
    ]

    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default=EMPLOYEE, null=False, blank=False)
    department = models.CharField(
        max_length=50, choices=DEPARTMENT_CHOICES, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    # is_approved = models.BooleanField(default=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=200, unique=True)
    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.name}"


class Profile(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name='user_profile')
    resume = models.FileField(upload_to='documents/', null=True, blank=True)
    personal_details = models.TextField(null=True, blank=True)
    picture = models.ImageField(upload_to='images/', null=True, blank=True)
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    # signature = models.ImageField(
    #     upload_to='documents/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.name}"


class LeaveRequest(models.Model):
    PENDING = 'PENDING'
    HR_APPROVED = 'HR_APPROVED'
    FINAL_APPROVED = 'FINAL_APPROVED'
    REJECTED = 'REJECTED'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (HR_APPROVED, 'HR Approved'),
        (FINAL_APPROVED, 'Final Approved'),
        (REJECTED, 'Rejected'),
    ]

    LEAVE_TYPES = [
        ('ANNUAL', 'Annual Leave'),
        ('SICK', 'Sick Leave'),
        ('UNPAID', 'Unpaid Leave'),
    ]

    employee = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="leave_requests")
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=PENDING)
    hr_approved = models.BooleanField(default=False)
    manager_approved = models.BooleanField(default=False)
    current_reviewer = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='to_review')
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee.name()} - {self.leave_type} - {self.status}"

    def days(self):
        return (self.end_date - self.start_date).days + 1


class LeaveBalance(models.Model):
    employee = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="employees_leave_balance"
    )
    annual_leave = models.IntegerField(default=30)
    sick_leave = models.IntegerField(default=10)
    unpaid_leave = models.IntegerField(default=0)
    casual_leave = models.IntegerField(default=0)

    @property
    def total_paid_leave(self):
        """
        Returns total annual + sick leave (used for payroll/paid reporting).
        """
        return self.annual_leave + self.sick_leave

    @property
    def total_leave_balance(self):
        """
        Returns total paid leave balance: annual + sick + casual.
        """
        return self.annual_leave + self.sick_leave + self.casual_leave

    @property
    def total_leave_including_unpaid(self):
        """
        Returns total leave balance including unpaid.
        """
        return self.total_leave_balance + self.unpaid_leave

    def remaining_leave(self, leave_type):
        """
        Returns remaining days for a specific leave type, subtracting all FINAL_APPROVED leave days.
        Supports 'ANNUAL', 'SICK', 'CASUAL', and 'UNPAID'.
        """
        taken = LeaveRequest.objects.filter(
            employee=self.employee,
            leave_type=leave_type,
            status=LeaveRequest.FINAL_APPROVED
        ).aggregate(
            total=models.Sum(models.F('end_date') -
                             models.F('start_date') + timedelta(days=1))
        )['total'] or timedelta(days=0)

        taken_days = taken.days if isinstance(taken, timedelta) else 0

        leave_mapping = {
            'ANNUAL': self.annual_leave,
            'SICK': self.sick_leave,
            'CASUAL': self.casual_leave,
            'UNPAID': self.unpaid_leave,  # No subtraction for unpaid
        }

        return leave_mapping.get(leave_type, 0) - taken_days if leave_type != 'UNPAID' else self.unpaid_leave

    def as_dict(self):
        """
        Serializes balance info (used in APIs or dashboard tables).
        """
        return {
            "employee": self.employee.name(),
            "annual_leave": self.annual_leave,
            "sick_leave": self.sick_leave,
            "casual_leave": self.casual_leave,
            "unpaid_leave": self.unpaid_leave,
            "total_paid_leave": self.total_leave_balance(),
            "total_leave_with_unpaid": self.total_leave_including_unpaid()
        }

    def __str__(self):
        return f"{self.employee.name()} - Paid Leave: {self.total_leave_balance()} days"

    def save(self, *args, **kwargs):
        created = self.pk is None
        super().save(*args, **kwargs)

        action = "created" if created else "updated"
        message = f"Your leave balance has been {action}. Annual: {self.annual_leave} days, Sick: {self.sick_leave} days, Casual: {self.casual_leave} days."

        Notification.notify_user(self.employee, message)


class ExpenseReimbursement(models.Model):
    employee = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='employees_rembursement')
    date = models.DateField(default=now)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), (
        'Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending')
    manager_approval = models.BooleanField(default=False)
    hr_approval = models.BooleanField(default=False)

    def __str__(self):
        return f"Expense Reimbursement for {self.employee.name} - {self.date}"


class EmployeeRecord(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name='employees')
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    overtime_hours = models.DecimalField(
        max_digits=5, decimal_places=2, default=0)
    bonuses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    net_salary = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, editable=False)
    leave_balance = models.IntegerField(default=20)
    attendance = models.IntegerField(default=0)

    def calculate_net_salary(self):
        self.net_salary = self.basic_salary + \
            (self.overtime_hours * 20) + self.bonuses - self.deductions
        return self.net_salary

    def save(self, *args, **kwargs):
        self.calculate_net_salary()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.name} - Net Salary: {self.net_salary}"


class SalarySlip(models.Model):
    employee = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='employee_salary_slips')
    salary_month = models.CharField(max_length=20)
    salary_year = models.PositiveIntegerField()
    file = models.FileField(upload_to='salary_slips/')
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.name} - {self.salary_month}-{self.salary_year}"


class Salary(models.Model):
    employee = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="salaries")
    basic_salary = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    overtime_hours = models.DecimalField(
        max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    bonuses = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    pension_contribution = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    income_tax = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    provident_fund = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    health_insurance = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)

    total_deductions = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, editable=False)
    gross_salary = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, editable=False)
    net_salary = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, editable=False)
    salary_month = models.CharField(max_length=20, blank=True, null=True)
    salary_year = models.PositiveIntegerField(blank=True, null=True)

    def calculate_gross_salary(self):
        gross = self.basic_salary + \
            (self.overtime_hours * Decimal(20)) + self.bonuses
        self.gross_salary = gross
        return gross

    def calculate_deductions(self):
        self.pension_contribution = self.basic_salary * \
            Decimal('0.075')  # 7.5%
        self.income_tax = self.calculate_income_tax()
        # provident_fund and health_insurance could be manually entered or calculated similarly
        total = self.pension_contribution + self.income_tax + \
            (self.provident_fund or 0) + (self.health_insurance or 0)
        self.total_deductions = total
        return total

    def calculate_net_salary(self):
        self.net_salary = self.gross_salary - self.total_deductions
        return self.net_salary

    def calculate_income_tax(self):
        # Simple tax bands (example; replace with actual country-specific logic)
        if self.basic_salary <= 30000:
            return self.basic_salary * Decimal('0.05')
        elif self.basic_salary <= 70000:
            return self.basic_salary * Decimal('0.1')
        elif self.basic_salary <= 150000:
            return self.basic_salary * Decimal('0.15')
        else:
            return self.basic_salary * Decimal('0.2')

    def save(self, *args, **kwargs):
        self.calculate_gross_salary()
        self.calculate_deductions()
        self.calculate_net_salary()
        if not self.salary_month or not self.salary_year:
            now_date = now()
            if not self.salary_month:
                self.salary_month = now_date.strftime("%B")  # e.g. "May"
            if not self.salary_year:
                self.salary_year = now_date.year
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.name} - {self.employee.email} with  {self.net_salary} and {self.pension_contribution}"


class PerformanceReview(models.Model):
    employee = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="performance_reviews")
    reviewer = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='reviewer')
    date = models.DateField(default=now)
    work_quality = models.IntegerField()
    attendance = models.IntegerField()
    productivity = models.IntegerField()
    comments = models.TextField()

    def __str__(self):
        return f"{self.employee.name} - Reviewed by {self.reviewer.name}"

    def get_previous_month_range(self):
        # Get the previous month range based on `self.date`
        first_day_of_current_month = self.date.replace(day=1)
        last_day_of_previous_month = first_day_of_current_month - \
            timedelta(days=1)
        first_day_of_previous_month = last_day_of_previous_month.replace(day=1)
        return first_day_of_previous_month, last_day_of_previous_month

    def calculate_attendance(self):
        start_date, end_date = self.get_previous_month_range()

        bio_count = BiometricAttendance.objects.filter(
            employee=self.employee,
            check_in__isnull=False,
            check_out__isnull=False,
            date__range=(start_date, end_date)
        ).count()

        manual_count = ManualAttendance.objects.filter(
            employee=self.employee,
            check_in__isnull=False,
            check_out__isnull=False,
            date__range=(start_date, end_date)
        ).count()

        total = bio_count + manual_count

        return total if total > 0 else None

    def save(self, *args, **kwargs):
        if self.attendance:
            self.attendance = self.calculate_attendance()
        super().save(*args, **kwargs)


class PayrollReport(models.Model):
    employee = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='payroll_reports')
    month = models.DateField()

    generated_at = models.DateTimeField(auto_now_add=True)
    report_pdf = models.FileField(upload_to='payroll_reports/')

    def __str__(self):
        return f"Payroll Report for {self.employee.name}"


class Notification(models.Model):
    recipient = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.recipient.name} - Read: {self.is_read}"

    @staticmethod
    def notify_user(recipient, message):
        try:
            if not isinstance(recipient, CustomUser):
                raise ValueError(
                    "Recipient must be a valid CustomUser instance.")

            Notification.objects.create(recipient=recipient, message=message)
            logger.info(f"Notification sent to {recipient.email}: {message}")

        except ObjectDoesNotExist:
            logger.error(f"Recipient {recipient} does not exist.")
            return False

        except ValueError as ve:
            logger.error(f"ValueError: {ve}")
            return False

        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False

        return True

    def mark_as_read(self):
        self.is_read = True
        self.save()


class WebAuthnCredential(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="credentials")
    credential_id = models.CharField(max_length=255, unique=True)
    public_key = models.BinaryField()
    counter = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    device_fingerprint = models.CharField(
        max_length=255, unique=True)  # Store the fingerprint ID

    def __str__(self):
        return f"WebAuthn Credential for {self.user.name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'credential_id'], name='unique_user_credential_id'),
            models.UniqueConstraint(
                fields=['user', 'public_key'], name='unique_user_public_key'),
            models.UniqueConstraint(
                fields=['user', 'device_fingerprint'], name='unique_user_device_fingerprint'),
        ]


class BiometricAttendance(models.Model):
    CHECKOUT_ELIGIBLE_HOURS = 1
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    credential = models.ForeignKey(
        WebAuthnCredential, on_delete=models.CASCADE)
    date = models.DateField(default=now)
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)
    worked_hours = models.DecimalField(
        max_digits=5, decimal_places=2, default=0)
    overtime_hours = models.DecimalField(
        max_digits=5, decimal_places=2, default=0)
    biometric_verified = models.BooleanField(default=False)
    method = models.CharField(default="biometric", max_length=10)

    def __str__(self):
        return f"{self.employee.name} - Biometric - {self.date}"

    def calculate_worked_hours(self):
        if self.check_in and self.check_out:
            worked_seconds = (self.check_out - self.check_in).total_seconds()
            self.worked_hours = round(worked_seconds / 3600, 2)
            return self.worked_hours
        return 0

    def calculate_overtime(self):
        if self.check_in and not self.check_out:
            now_time = timezone.now()
            elapsed = (now_time - self.check_in).total_seconds()
            overtime_seconds = elapsed - (8 * 3600)
            self.overtime_hours = round(max(overtime_seconds / 3600, 0), 2)
        elif self.check_in and self.check_out:
            worked = (self.check_out - self.check_in).total_seconds()
            overtime_seconds = worked - (8 * 3600)
            self.overtime_hours = round(max(overtime_seconds / 3600, 0), 2)

    def can_check_out(self):
        if self.check_in:
            return timezone.now() >= self.check_in + timedelta(hours=self.CHECKOUT_ELIGIBLE_HOURS)
        return False

    def should_show_check_in(self):
        return self.check_in is None and self.check_out is None

    def should_show_check_out(self):
        if self.check_in and not self.check_out:
            elapsed = (timezone.now() - self.check_in).total_seconds()
            return elapsed >= self.CHECKOUT_ELIGIBLE_HOURS * 3600
        return False

    def get_check_in_time_display(self):
        return format(self.check_in, 'H:i:s') if self.check_in else None

    def get_current_overtime(self):
        if self.check_in and not self.check_out:
            now_time = timezone.now()
            elapsed = (now_time - self.check_in).total_seconds()
            overtime_seconds = elapsed - (8 * 3600)
            return round(max(overtime_seconds / 3600, 0), 2)
        return self.overtime_hours


def company_logo_upload_path(instance, filename):
    return f'company_logos/{instance.user.id}/{filename}'


class CompanyProfile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='company_profile'
    )
    company_name = models.CharField(max_length=100)
    company_address = models.CharField(max_length=255)
    company_email = models.EmailField(max_length=100, null=True, blank=True)
    company_phone = models.CharField(max_length=20, null=True, blank=True)
    company_logo = models.ImageField(
        upload_to=company_logo_upload_path, null=True, blank=True)
    business_info = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name


class Complaint(models.Model):
    sender = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='sent_complaints'
    )

    manager = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='received_complaints',
        limit_choices_to={'role': CustomUser.OVERALL_ADMIN},
    )

    subject = models.CharField(max_length=255)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    manager_response = models.TextField(null=True, blank=True)
    response_submitted_by = models.ForeignKey(
        CustomUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='complaint_responses'
    )
    response_submitted_at = models.DateTimeField(null=True, blank=True)
    response_viewed = models.BooleanField(default=False)

    user_reply = models.TextField(null=True, blank=True)
    user_reply_submitted_at = models.DateTimeField(null=True, blank=True)
    reply_viewed_by_manager = models.BooleanField(default=False)

    def __str__(self):
        return f"Complaint from {self.sender.name} ({self.sender.role}) to CEO"

    def is_answered(self):
        return self.manager_response and self.response_submitted_by is not None

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class Emails(models.Model):
    subject = models.CharField(max_length=300)
    message = models.TextField(max_length=500)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    edited_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.id


class TaxDeduction(models.Model):
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    income_tax = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    provident_fund = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    health_insurance = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=10, decimal_places=2)

    def calculate_total_deductions(self):
        self.total_deductions = self.income_tax + \
            self.provident_fund + self.health_insurance
        return self.total_deductions

    def __str__(self):
        return f"{self.employee.name} - {self.income_tax}"

 # Adjust path as needed


class ManualAttendance(models.Model):
    CHECKOUT_ELIGIBLE_HOURS = 1
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)
    worked_hours = models.DecimalField(
        max_digits=5, decimal_places=2, default=0)
    overtime_hours = models.DecimalField(
        max_digits=5, decimal_places=2, default=0)
    manual_check_in = models.BooleanField(default=True)
    method = models.CharField(default="manual", max_length=10)
    is_biometric = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.employee.name} - {'Biometric' if self.is_biometric else 'Manual'} - {self.date}"

    def save(self, *args, **kwargs):
        # Calculate worked hours if checked out
        if self.check_in and self.check_out:
            self.worked_hours = self.calculate_worked_hours()
        # Always update overtime (including if check_out is None)
        self.calculate_overtime()
        super().save(*args, **kwargs)

    def calculate_worked_hours(self):
        if self.check_in and self.check_out:
            worked_seconds = (self.check_out - self.check_in).total_seconds()
            return round(worked_seconds / 3600, 2)
        return 0

    def calculate_overtime(self):
        if self.check_in:
            end_time = self.check_out or timezone.now()
            worked_seconds = (end_time - self.check_in).total_seconds()
            overtime_seconds = worked_seconds - (8 * 3600)
            self.overtime_hours = round(max(overtime_seconds / 3600, 0), 2)

    def can_check_out(self):
        if self.check_in:
            return timezone.now() >= self.check_in + timedelta(hours=self.CHECKOUT_ELIGIBLE_HOURS)
        return False

    def should_show_check_in(self):
        return self.check_in is None and self.check_out is None

    def should_show_check_out(self):
        if self.check_in and not self.check_out:
            elapsed = (timezone.now() - self.check_in).total_seconds()
            return elapsed >= self.CHECKOUT_ELIGIBLE_HOURS * 3600
        return False


# ///////////////////////
# //////////////////////


class Task(models.Model):
    PENDING = 'Pending'
    SUBMITTED = 'Submitted'
    IN_PROGRESS = 'In_Progress'
    REVIEWED = 'Reviewed'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (IN_PROGRESS, 'In_Progress'),
        (SUBMITTED, 'Submitted'),
        (REVIEWED, 'Reviewed'),
    ]

    title = models.CharField(max_length=2250)
    description = models.TextField()
    assigned_to = models.ForeignKey(
        CustomUser, related_name='tasks_assigned', on_delete=models.CASCADE)
    assigned_by = models.ForeignKey(
        CustomUser, related_name='tasks_created', on_delete=models.CASCADE)
    biometric_attendance = models.ForeignKey(
        BiometricAttendance, null=True, blank=True, on_delete=models.CASCADE)
    manual_attendance = models.ForeignKey(
        ManualAttendance, null=True, blank=True, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    review_comments = models.TextField(blank=True, null=True)
    review_score = models.IntegerField(blank=True, null=True, choices=[
                                       # 1-5 rating
                                       (i, str(i)) for i in range(1, 6)])

    def validate_assignment(self, request=None):
        creator = self.assigned_by
        assignee = self.assigned_to
        today = now().date()

        if creator == assignee:
            raise ValidationError("Users cannot assign tasks to themselves.")
        if Task.objects.filter(assigned_by=creator, created_at__date=today).exists():
            raise ValidationError("You can only create one task per day.")
        if creator.role == CustomUser.HR_MANAGER:
            if assignee.role != CustomUser.EMPLOYEE:
                raise ValidationError(
                    "HR_Manager can only assign tasks to Employees in the same department."
                )
            if assignee.department != creator.department:
                raise ValidationError(
                    "HR_Manager can only assign tasks to Employees within their own department."
                )

        elif creator.role == CustomUser.MANAGER:
            if assignee.role not in [CustomUser.EMPLOYEE, CustomUser.HR_MANAGER]:
                raise ValidationError(
                    "Manager can only assign tasks to Employees or HR_Managers in the same department."
                )
            if assignee.department != creator.department:
                raise ValidationError(
                    "Manager can only assign tasks to users within their own department."
                )

        elif creator.role == CustomUser.OVERALL_ADMIN:
            if assignee == creator:
                raise ValidationError(
                    "Overall_Admin cannot assign tasks to themselves.")

        else:
            raise ValidationError(
                "You do not have permission to assign tasks.")

    # class Meta:
    #     constraints = [
    #         models.CheckConstraint(
    #             check=models.Q(biometric_attendance__isnull=False) | models.Q(
    #                 manual_attendance__isnull=False),
    #             name='task_has_one_attendance'
    #         ),
    #         models.CheckConstraint(
    #             check=~models.Q(biometric_attendance__isnull=False,
    #                             manual_attendance__isnull=False),
    #             name='task_has_only_one_attendance'
    #         )
    #     ]

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ['-created_at']


class Message(models.Model):
    sender = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=255)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender} to {self.receiver} - {self.subject[:30]}"


class TeamPerformanceReview(models.Model):
    manager = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': CustomUser.MANAGER}
    )
    department = models.CharField(
        max_length=50, choices=CustomUser.DEPARTMENT_CHOICES)
    month = models.DateField(default=now)
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # One review per month per manager
        unique_together = ('manager', 'month')
        ordering = ['-month']

    def __str__(self):
        return f"{self.department} - {self.month.strftime('%B %Y')}"
