from django.contrib import admin
from .models import *

admin = admin.site.register
admin(CustomUser)
admin(SalarySlip)
admin(TaxDeduction)
admin(LeaveRequest)
admin(CompanyProfile)
admin(EmployeeRecord)
admin(Complaint)
admin(Notification)
admin(PayrollReport)
admin(PerformanceReview)
admin(Profile)
admin(Emails)
admin(Salary)
admin(Task)
admin(LeaveBalance)
admin(ExpenseReimbursement)