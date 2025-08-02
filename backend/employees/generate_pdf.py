from io import BytesIO
import zipfile
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from .logger import logger
from .generate_qrcode import generate_qr_code
from .generate_salary_email import send_salary_slip_email
from .models import CustomUser, Salary, CompanyProfile, SalarySlip, Profile


@login_required
def generate_salary_slip(request, employee_id):
    employee = get_object_or_404(CustomUser, id=employee_id)
    current_user = request.user

    if request.method != 'POST':
        return HttpResponse("Invalid request method", status=405)

    try:
        if current_user.role not in ['Overall_Admin', 'Manager', 'HR_Manager', 'Employee']:
            raise PermissionDenied('You do not have permission')
        if current_user.role in ['HR_Manager', 'Employee'] and employee != current_user:
            raise PermissionDenied(
                'You can only generate your own salary slip')

        month = request.POST.get('salary_month')
        year = request.POST.get('salary_year')
        if not month or not year:
            now_date = now()
            if not month:
                month = now_date.strftime("%B")  # "May"
            if not year:
                year = now_date.year

        salary = get_object_or_404(Salary, employee=employee)
        if salary.salary_month != month or salary.salary_year != int(year):
            salary.salary_month = month
            salary.salary_year = int(year)
            salary.save()

        salary = get_object_or_404(Salary, employee=employee)
        company_profile = CompanyProfile.objects.first()  # if you only expect one profile


        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

       
        if company_profile.company_logo:
            elements.append(
                Image(company_profile.company_logo.path, width=2*inch, height=2*inch))
            elements.append(Spacer(1, 0.1 * inch))

      
        elements += [
            Paragraph(f"<b>{company_profile.company_name}</b>",
                      styles['Title']),
            Paragraph(company_profile.company_address, styles['Normal']),
            Paragraph(company_profile.business_info, styles['Normal']),
            Spacer(1, 0.3 * inch),
            Paragraph(
                f"<b>Salary Slip for {employee.name()}</b>", styles['Title']),
            Spacer(1, 0.2 * inch),
            Paragraph(f"<b>Month:</b> {month}", styles['Normal']),
            Paragraph(f"<b>Year:</b> {year}", styles['Normal']),
            Paragraph(
                f"<b>Basic Salary:</b> ${salary.basic_salary}", styles['Normal']),
            Paragraph(
                f"<b>Overtime Pay:</b> ${salary.overtime_hours * 20}", styles['Normal']),
            Paragraph(f"<b>Bonuses:</b> ${salary.bonuses}", styles['Normal']),
            Paragraph(
                f"<b>Deductions:</b> ${salary.total_deductions}", styles['Normal']),
            Paragraph(
                f"<b>Net Salary:</b> ${salary.net_salary}", styles['Normal']),
            Spacer(1, 0.2 * inch),
        ]

        profile = getattr(employee, 'profile', None)
        if profile:
            elements += [
                Paragraph(
                    f"<b>Location:</b> {profile.state}, {profile.country}", styles['Normal']),
                Paragraph(
                    f"<b>Department:</b> {employee.department}", styles['Normal']),
                Paragraph(f"<b>Role:</b> {employee.role}", styles['Normal']),
                Spacer(1, 0.5 * inch)
            ]
            if profile.signature:
                elements.append(
                    Paragraph("<b>Employee Signature:</b>", styles['Normal']))
                elements.append(Image(profile.signature.path,
                                width=1.5*inch, height=0.5*inch))

    
        manager_profile = Profile.objects.filter(
            user__role='Manager', user__department=employee.department).first()
        if manager_profile and manager_profile.signature:
            elements.append(
                Paragraph("<b>Manager Signature:</b>", styles['Normal']))
            elements.append(Image(manager_profile.signature.path,
                            width=1.5*inch, height=0.5*inch))

        
        hr_profile = Profile.objects.filter(
            user__role='HR_Manager', user__department=employee.department).first()
        if hr_profile and hr_profile.signature:
            elements.append(
                Paragraph("<b>HR Signature:</b>", styles['Normal']))
            elements.append(Image(hr_profile.signature.path,
                            width=1.5*inch, height=0.5*inch))

        
        qr_data = f"{employee.username}_{month}_{year}"
        qr_image = generate_qr_code(qr_data)
        elements.append(Spacer(1, 0.3 * inch))
        elements.append(
            Paragraph("<b>Verification QR Code:</b>", styles['Normal']))
        elements.append(qr_image)

        doc.build(elements)
        buffer.seek(0)

       
        pdf_filename = f"salary_slip_{employee.username}_m{month}_{year}.pdf"
        slip = SalarySlip.objects.create(
            employee=employee,
            salary_month=month,
            salary_year=year
        )
        slip.file.save(pdf_filename, buffer)

      
        send_salary_slip_email(employee.email, pdf_filename, buffer.getvalue())

        response = HttpResponse(
            buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{pdf_filename}"'
        return response

    except Exception as e:
        logger.error(f"Unexpected error in salary slip generation: {e}")
        messages.error(request, "Something went wrong.")
        return redirect(request.META.get('HTTP_REFERER', 'salary_list'))


@login_required
def generate_salary_slips_bulk(request):
    try:

        employee_ids = request.POST.getlist('employee_ids[]')
        month = request.POST.get('month')
        year = request.POST.get('year')

        if not employee_ids or not month or not year:
            return HttpResponse("Employee IDs, month, and year are required.", status=400)

        zip_buffer = BytesIO()
        zip_file = zipfile.ZipFile(zip_buffer, 'w')
        company_profile = get_object_or_404(CompanyProfile, user__id=1)

        for employee_id in employee_ids:
            employee = get_object_or_404(CustomUser, id=employee_id)
            salary = get_object_or_404(Salary, employee=employee)

            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []

            if company_profile.company_logo:
                logo = Image(company_profile.company_logo.path,
                             width=2*inch, height=2*inch)
                elements.append(logo)
                elements.append(Spacer(1, 0.1 * inch))

            elements += [
                Paragraph(
                    f"<b>{company_profile.company_name}</b>", styles['Title']),
                Paragraph(company_profile.company_address,
                          styles['Normal']),
                Paragraph(company_profile.business_info, styles['Normal']),
                Spacer(1, 0.3 * inch),
                Paragraph(
                    f"<b>Salary Slip for {employee.name}</b>", styles['Title']),
                Spacer(1, 0.2 * inch),
                Paragraph(f"<b>Month:</b> {month}", styles['Normal']),
                Paragraph(f"<b>Year:</b> {year}", styles['Normal']),
                Paragraph(
                    f"<b>Basic Salary:</b> ${salary.basic_salary}", styles['Normal']),
                Paragraph(
                    f"<b>Overtime:</b> ${salary.overtime_hours * 20}", styles['Normal']),
                Paragraph(
                    f"<b>Bonuses:</b> ${salary.bonuses}", styles['Normal']),
                Paragraph(
                    f"<b>Deductions:</b> ${salary.total_deductions}", styles['Normal']),
                Paragraph(
                    f"<b>Net Salary:</b> ${salary.net_salary}", styles['Normal']),
                Spacer(1, 0.2 * inch),
            ]

            profile = getattr(employee, 'user_profile', None)
            if profile:
                elements.append(Paragraph(
                    f"<b>Location:</b> {profile.state}, {profile.country}", styles['Normal']))

            elements += [
                Paragraph(
                    f"<b>Department:</b> {employee.department}", styles['Normal']),
                Paragraph(
                    f"<b>Role:</b> {employee.role}", styles['Normal']),
                Spacer(1, 0.3 * inch)
            ]

            manager_profile = Profile.objects.filter(
                user__role='Manager').first()
            if manager_profile and manager_profile.signature:
                elements.append(
                    Paragraph("<b>Manager Signature:</b>", styles['Normal']))
                elements.append(
                    Image(manager_profile.signature.path, width=1.5*inch, height=0.5*inch))
                elements.append(Spacer(1, 0.2 * inch))

            hr_profile = Profile.objects.filter(user__role='HR').first()
            if hr_profile and hr_profile.signature:
                elements.append(
                    Paragraph("<b>HR Signature:</b>", styles['Normal']))
                elements.append(
                    Image(hr_profile.signature.path, width=1.5*inch, height=0.5*inch))

            qr_data = f"{employee.username}_{month}_{year}"
            qr_image = generate_qr_code(qr_data)
            elements.append(Spacer(1, 0.3 * inch))
            elements.append(
                Paragraph("<b>Verification QR Code:</b>", styles['Normal']))
            elements.append(qr_image)

            doc.build(elements)
            buffer.seek(0)

            salary_slip = SalarySlip.objects.create(
                employee=employee,
                salary_month=month,
                salary_year=year
            )
            pdf_filename = f"salary_slip_{employee.username}_{month}_{year}.pdf"
            salary_slip.file.save(pdf_filename, buffer)

            send_salary_slip_email(
                employee.email, pdf_filename, buffer.getvalue())

            zip_file.writestr(pdf_filename, buffer.read())

        zip_file.close()
        zip_buffer.seek(0)

        response = HttpResponse(zip_buffer.getvalue(),
                                content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="salary_slips_{month}_{year}.zip"'
        return response
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return HttpResponse('Something went wrong', status=500)
