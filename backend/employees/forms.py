import requests
from datetime import date
from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import *


class CustomChoiceField(forms.ChoiceField):
    def validate(self, value):
        pass


class HR_RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    phone_number = forms.CharField(label='Phone Number', max_length=20)
    role = forms.ChoiceField(label='Role', choices=[
                             (CustomUser.HR, 'HR')])

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2',
                  'first_name', 'last_name', 'phone_number', 'role')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "This Email already exists.")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if CustomUser.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError(
                "This Phone Number already exists.")
        return phone_number

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "This Username already exists.")
        return username


class EmployeeRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    phone_number = forms.CharField(label='Phone Number', max_length=20)
    role = forms.ChoiceField(label='Role', choices=[
                             (CustomUser.EMPLOYEE, 'Employee')])
    department = forms.ChoiceField(label='Department', choices=[
        (CustomUser.HR, 'HR'),
        (CustomUser.MARKETING, 'Marketing'),
        (CustomUser.SALES, 'Sales'),
        (CustomUser.ENGINEERING, 'Engineering'),
        (CustomUser.MARKETING, 'Marketing'),
    ])

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2',
                  'first_name', 'last_name', 'phone_number', 'role', 'department')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "This Email already exists.")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if CustomUser.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError(
                "This Phone Number already exists.")
        return phone_number

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "This Username already exists.")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        if commit:
            user.save()
        return user


class ManagerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    phone_number = forms.CharField(label='Phone Number', max_length=20)
    role = forms.ChoiceField(label='Role', choices=[
                             (CustomUser.MANAGER, 'Manager')])

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2',
                  'first_name', 'last_name', 'phone_number', 'role')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "This Email already exists.")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if CustomUser.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError(
                "This Phone Number already exists.")
        return phone_number

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "This Username already exists.")
        return username


class OverallAdmin_RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    phone_number = forms.CharField(label='Phone Number', max_length=20)
    role = forms.ChoiceField(label='Role', choices=[
                             (CustomUser.OVERALL_ADMIN, 'Overall_Admin')])

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2',
                  'first_name', 'last_name', 'phone_number', 'role')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "This Email already exists.")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if CustomUser.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError(
                "This Phone Number already exists.")
        return phone_number

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "This Username already exists.")
        return username


class UserLoginForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'password')


class EmployeeRecordForm(forms.ModelForm):
    class Meta:
        model = EmployeeRecord
        fields = ['basic_salary', 'overtime_hours', 'bonuses',
                  'deductions', 'leave_balance', 'attendance']

    def clean(self):
        cleaned_data = super().clean()
        for field in ['basic_salary', 'overtime_hours', 'bonuses', 'deductions']:
            if cleaned_data.get(field) is not None and cleaned_data[field] < 0:
                self.add_error(field, 'Value must be positive.')


class ProfileForm(forms.ModelForm):
    country = CustomChoiceField(
        label='Country', choices=[], widget=forms.Select(attrs={'id': 'country'}))
    state = CustomChoiceField(
        label='State', choices=[], widget=forms.Select(attrs={'id': 'state'}))

    class Meta:
        model = Profile
        fields = ['resume', 'personal_details',
                  'picture', 'country', 'state']

    def __init__(self, *args, **kwargs):
        fields = self.fields
        super(ProfileForm, self).__init__(*args, **kwargs)
        fields = ['country'].choices = self.fetch_countries_choices()
        fields['state'].choices = []
        fields['resume'].required = True
        fields['picture'].required = True
        # fields['signature'].required = False

    def clean_picture(self):
        pic = self.cleaned_data.get('picture')
        if pic and pic.size > 1 * 1024 * 1024:
            raise ValidationError('Max image size is 1MB.')
        return pic

    def fetch_countries_choices(self):
        url = "https://country-api-1.onrender.com/country/countries"
        response = requests.get(url)
        if response.status_code == 200:
            return [(country[0], country[1]) for country in response.json()]
        else:
            return []


class SalarySlipForm(forms.ModelForm):
    class Meta:
        model = SalarySlip
        fields = ['salary_month', 'salary_year', 'file']

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file and not file.name.endswith('.pdf'):
            raise ValidationError('Salary slip must be a PDF file.')
        if file and file.size > 2 * 1024 * 1024:  # 2MB
            raise ValidationError('File too large. Max size is 2MB.')
        return file


class SalaryForm(forms.ModelForm):

    class Meta:
        model = Salary
        fields = [
            'basic_salary', 'overtime_hours', 'bonuses',

        ]

    def clean(self):
        fields = self.fields
        cleaned_data = super().clean()
        for field in fields:
            if cleaned_data.get(field) is not None and cleaned_data[field] < 0:
                self.add_error(field, 'Value must be non-negative.')


class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        fields = ['company_name', 'company_address',
                  'company_logo', 'business_info']

    def clean_company_logo(self):
        logo = self.cleaned_data.get('company_logo')
        if logo and logo.size > 2 * 1024 * 1024:
            raise ValidationError('Logo size must be less than 2MB.')
        return logo


class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'leave_type': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError('End date must be after start date.')
            if start_date < date.today():
                raise ValidationError('Start date cannot be in the past.')

        return cleaned_data


class PerformanceReviewForm(forms.ModelForm):
    class Meta:
        model = PerformanceReview
        fields = ['employee', 'reviewer', 'date',
                  'work_quality', 'productivity', 'comments']

    def __init__(self, *args, **kwargs):
        # fields = self.fields
        self.request_user = kwargs.pop('request_user')
        super().__init__(*args, **kwargs)

        self.fields['reviewer'].disabled = True
        self.fields['reviewer'].initial = self.request_user

        # Optional: Set employee queryset and label format
        self.fields['employee'].queryset = CustomUser.objects.all()
        self.fields['employee'].label_from_instance = lambda obj: f"{obj.name} - {obj.role} - {obj.department}- {obj.email}"

    def clean(self):
        cleaned_data = super().clean()
        reviewer = self.request_user
        employee = cleaned_data.get('employee')
        date = cleaned_data.get('date')
        temp_instance = PerformanceReview(employee=employee, date=date)
        attendance = temp_instance.calculate_attendance()

        if not employee:
            raise ValidationError("Please select an employee.")

        # Check if a review already exists for the same employee and month
        start_of_month = date.replace(day=1)
        if PerformanceReview.objects.filter(employee=employee, date__year=date.year, date__month=date.month).exists():
            raise ValidationError(
                "A performance review for this employee already exists for this month.")

        if attendance is None:
            raise ValidationError(
                "Employee does not have any valid attendance records for the previous month.")

        cleaned_data['attendance'] = attendance
        if employee == reviewer and reviewer.role != CustomUser.OVERALL_ADMIN:
            raise ValidationError("You cannot review yourself.")

    # Role-based permissions
        if reviewer.role == CustomUser.MANAGER:
            if employee.role != CustomUser.HR_MANAGER or employee.department != reviewer.department:
                raise ValidationError(
                    "Managers can only review HR Managers in the same department.")
        elif reviewer.role == CustomUser.HR_MANAGER:
            if employee.role != CustomUser.EMPLOYEE or employee.department != reviewer.department:
                raise ValidationError(
                    "HR Managers can only review Employees in the same department.")
        elif reviewer.role == CustomUser.EMPLOYEE:
            raise ValidationError(
                "Employees cannot create performance reviews.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.attendance = self.cleaned_data['attendance']()
        if commit:
            instance.save()
            return instance


class PayrollReportForm(forms.ModelForm):
    class Meta:
        model = PayrollReport
        fields = ['month', 'report_pdf']

    def clean_report_pdf(self):
        report = self.cleaned_data.get('report_pdf')
        if report and not report.name.endswith('.pdf'):
            raise ValidationError('Report must be a PDF file.')
        if report and report.size > 3 * 1024 * 1024:
            raise ValidationError('Max file size is 3MB.')
        return report


class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['recipient', 'message', 'is_read']

    def clean_message(self):
        msg = self.cleaned_data.get('message')
        if msg and len(msg) < 5:
            raise ValidationError(
                'Message must be at least 5 characters long.')
        return msg


class ViewProfileForm(forms.ModelForm):
    email = forms.EmailField(disabled=True)
    name = forms.CharField(disabled=True)
    phone_number = forms.CharField(disabled=True)
    role = forms.CharField(disabled=True)
    department = forms.CharField(disabled=True)

    class Meta:
        model = Profile
        fields = ['picture', 'resume', 'personal_details', 'country', 'state']

    def __init__(self, *args, **kwargs):
        fields = self.fields
        user = kwargs.pop('user', None)
        super(ViewProfileForm, self).__init__(*args, **kwargs)

        if user:
            fields['email'].initial = user.email
            fields['name'].initial = user.name
            fields['phone_number'].initial = user.phone_number
            fields['role'].initial = user.role
            fields['department'].initial = user.department

        # Set profile fields to read-only too
        for field_name in fields:
            fields[field_name].widget.attrs['readonly'] = True


class EmailForm(forms.ModelForm):
    email = forms.EmailField(label='Email', required=True)

    class Meta:
        model = Emails
        exclude = ['created_at', 'edited_at', 'message', 'subject']


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['manager', 'subject', 'message']

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.sender = kwargs.get('initial', {}).get('sender')

        if self.sender:
            if self.sender.role != CustomUser.MANAGER:
                self.fields['manager'].required = False
                self.fields['manager'].widget = forms.HiddenInput()

    def clean_message(self):
        msg = self.cleaned_data.get('message')
        if msg and len(msg.strip()) < 10:
            raise ValidationError(
                'Message must be more detailed (at least 10 characters).')
        return msg

    def clean(self):
        cleaned_data = super().clean()
        sender = self.sender
        manager = cleaned_data.get('manager')

        if not sender:
            return cleaned_data

        if sender.role == CustomUser.MANAGER:
            if not manager:
                raise ValidationError(
                    "Managers must select a complaint recipient.")
            if manager.role != CustomUser.OVERALL_ADMIN:
                raise ValidationError(
                    "Managers can only send complaints to Admin.")
            if sender == manager:
                raise ValidationError(
                    "You cannot send a complaint to yourself.")

        elif sender.role == CustomUser.EMPLOYEE:
            # manager is hidden, don't validate its role here
            pass

        elif sender.role == CustomUser.HR_MANAGER:
            # manager is hidden, don't validate its role here
            pass

        return cleaned_data


class TaxDeductionForm(forms.ModelForm):
    class Meta:
        model = TaxDeduction
        fields = ['income_tax', 'provident_fund', 'health_insurance']

    def __init__(self, *args, **kwargs):
        fields = self.fields
        self.request_user = kwargs.pop('request_user')
        self.employee = kwargs.pop('employee')
        super().__init__(*args, **kwargs)

        fields['income_tax'].label = f"Income Tax for {self.employee.username}"
        fields['provident_fund'].label = f"Provident Fund for {self.employee.username}"
        fields['health_insurance'].label = f"Health Insurance for {self.employee.username}"

    def clean(self):
        cleaned_data = super().clean()
        user = self.request_user
        target = self.employee
        fields = self.fields

        # Role-based creation logic
        if user.role == CustomUser.OVERALL_ADMIN:
            pass
        elif user.role == CustomUser.MANAGER:
            if target.role not in [CustomUser.HR_MANAGER, CustomUser.EMPLOYEE]:
                raise ValidationError(
                    "Managers can only assign deductions to HR Managers or Employees."
                )
            if user.department != target.department:
                raise ValidationError(
                    "You can only assign deductions within your department."
                )
        else:
            raise ValidationError(
                "You do not have permission to assign tax deductions."
            )

        for field in fields:
            value = cleaned_data.get(field)
            if value is not None and value < 0:
                self.add_error(field, 'Value must be non-negative.')

        return cleaned_data


class LeaveBalanceForm(forms.ModelForm):
    class Meta:
        model = LeaveBalance
        fields = ['annual_leave', 'sick_leave', 'unpaid_leave', 'casual_leave']

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user')
        self.employee = kwargs.pop('employee')
        super().__init__(*args, **kwargs)

    def clean(self):

        cleaned_data = super().clean()
        user = self.request_user
        target = self.employee
        fields = self.fields

        if user.role == CustomUser.OVERALL_ADMIN:

            pass

        elif user.role == CustomUser.MANAGER:

            if target.role not in [CustomUser.HR_MANAGER, CustomUser.EMPLOYEE]:
                raise ValidationError(
                    "Managers can only update leave balances for HR Managers or Employees.")
            if user.department != target.department:
                raise ValidationError(
                    "You can only update balances for users in your department.")

        else:

            raise ValidationError(
                "You are not authorized to modify leave balances.")

        for field in fields:
            value = cleaned_data.get(field)
            if value is not None and value < 0:
                self.add_error(field, 'Leave balance cannot be negative.')

        return cleaned_data


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'assigned_to': forms.Select(),
        }

    def __init__(self, *args, user=None, **kwargs):

        super().__init__(*args, **kwargs)
        self.user = user
        if not user or not hasattr(user, 'role'):
            self.fields['assigned_to'].queryset = CustomUser.objects.none()
            return
        if user:
            if user.role == CustomUser.OVERALL_ADMIN:
                self.fields['assigned_to'].queryset = CustomUser.objects.filter(
                    role__in=[CustomUser.EMPLOYEE,
                              CustomUser.HR_MANAGER, CustomUser.MANAGER]
                ).exclude(id=user.id)
            elif user.role == CustomUser.MANAGER:
                self.fields['assigned_to'].queryset = CustomUser.objects.filter(
                    department=user.department, role__in=[
                        CustomUser.EMPLOYEE, CustomUser.HR_MANAGER]
                ).exclude(id=user.id)
            elif user.role == CustomUser.HR_MANAGER:
                self.fields['assigned_to'].queryset = CustomUser.objects.filter(
                    department=user.department, role=CustomUser.EMPLOYEE
                ).exclude(id=user.id)
            else:
                self.fields['assigned_to'].queryset = CustomUser.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        assigned_to = cleaned_data.get('assigned_to')

        if not self.user:
            raise ValidationError(
                "User must be provided to validate task assignment.")

        if assigned_to == self.user:
            raise ValidationError("You cannot assign a task to yourself.")
        today = timezone.now().date()
        existing_task = Task.objects.filter(
            assigned_by=self.user,
            created_at__date=today
        ).exists()

        if existing_task:
            raise ValidationError("You can only create one task per day.")
        if self.user.role == CustomUser.HR_MANAGER and assigned_to.role != CustomUser.EMPLOYEE:
            raise ValidationError(
                "Hr_Manager can only assign tasks to Employees in the same department.")
        if self.user.role == CustomUser.MANAGER and assigned_to.role not in [CustomUser.EMPLOYEE, CustomUser.HR_MANAGER]:
            raise ValidationError(
                "Manager can only assign tasks to Employees or Hr_Managers in the same department.")

        return cleaned_data


class TaskReviewForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['review_comments', 'review_score']
        widgets = {
            'review_comments': forms.Textarea(attrs={'rows': 4}),
            'review_score': forms.Select(choices=[(i, str(i)) for i in range(1, 6)]),
        }


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['receiver', 'subject', 'body']
        widgets = {
            'receiver': forms.HiddenInput(),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }


class TeamPerformanceReviewForm(forms.ModelForm):
    class Meta:
        model = TeamPerformanceReview
        fields = ['review_text']
        widgets = {
            'review_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }
