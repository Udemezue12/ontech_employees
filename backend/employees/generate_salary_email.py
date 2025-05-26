
from django.core.mail import EmailMessage


def send_salary_slip_email(to_email: str, filename: str, pdf_data: bytes):
    email = EmailMessage(
        subject="Your Monthly Salary Slip",
        body="Attached is your salary slip. Please keep it for your records.",
        to=[to_email]
    )
    email.attach(filename, pdf_data, 'application/pdf')
    email.send(fail_silently=True)
