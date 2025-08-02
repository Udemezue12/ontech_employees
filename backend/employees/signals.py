
import threading, logging
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.core.exceptions import ValidationError
from django_rest_passwordreset.signals import reset_password_token_created
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import *


logger = logging.getLogger(__name__)
@receiver(pre_save, sender=PerformanceReview)
def prevent_self_review(sender, instance, **kwargs):
    if instance.reviewer == instance.employee:
        if instance.reviewer.role != CustomUser.OVERALL_ADMIN:
            raise ValidationError("Only Overall_Admin can review themselves.")


@receiver(pre_save, sender=TaxDeduction)
def prevent_unauthorized_deduction(sender, instance, **kwargs):
    creator = getattr(instance, '_creator', None)  # attached manually in view
    employee = instance.employee

    if not creator:
        return  

    if creator == employee and creator.role != CustomUser.OVERALL_ADMIN:
        raise ValidationError("You cannot assign deductions to yourself.")

    if creator.role == CustomUser.OVERALL_ADMIN:
        return  # Full access

    elif creator.role == CustomUser.MANAGER:
        if employee.role not in [CustomUser.HR_MANAGER, CustomUser.EMPLOYEE]:
            raise ValidationError(
                "Managers can only assign deductions to HR Managers or Employees.")
        if employee.department != creator.department:
            raise ValidationError(
                "You can only assign deductions in your department.")

    else:
        raise ValidationError(
            "You are not authorized to assign tax deductions.")


@receiver(pre_save, sender=LeaveBalance)
def restrict_leave_balance_updates(sender, instance, **kwargs):
    creator = getattr(instance, '_creator', None)
    employee = instance.employee

    if not creator:
        return

    if creator == employee and creator.role != CustomUser.OVERALL_ADMIN:
        raise ValidationError("You cannot update your own leave balance.")

    if creator.role == CustomUser.OVERALL_ADMIN:
        return

    elif creator.role == CustomUser.MANAGER:
        if employee.role not in [CustomUser.HR_MANAGER, CustomUser.EMPLOYEE]:
            raise ValidationError(
                "Managers can only modify HR Managers or Employees.")
        if creator.department != employee.department:
            raise ValidationError(
                "Managers can only modify balances within their department.")

    else:
        raise ValidationError(
            "You are  not authorized to modify leave balances.")





def send_reset_email(context, user_email):
    try:
        html_message = render_to_string('email.html', context=context)
        plain_message = strip_tags(html_message)

        msg = EmailMultiAlternatives(
            subject="Password Reset Request",
            body=plain_message,
            from_email='udemezue0009@gmail.com',
            to=[user_email],  # ✅ must be a list
        )
        msg.attach_alternative(html_message, 'text/html')
        msg.send()

        logger.info(f"Password reset email successfully sent to: {user_email}")
    except Exception as e:
        logger.error(f" Failed to send password reset email to {user_email}. Error: {str(e)}")


@receiver(reset_password_token_created)
def password_reset_token_created(sender, reset_password_token, **kwargs):
    logger.debug(" password_reset_token_created SIGNAL TRIGGERED")
    frontend_base_url = 'http://localhost:7000/password-reset'
    token = reset_password_token.key
    email = reset_password_token.user.email
    full_link = f"{frontend_base_url}?token={token}&email={email}"

    logger.info(f"🔗 Password reset link generated for {email}: {full_link}")

    context = {
        'full_link': full_link,
        'email_address': email,
    }

    threading.Thread(target=send_reset_email, args=(context, email)).start()



@receiver(pre_save, sender=BiometricAttendance)
def submit_tasks_on_biometric_checkout(sender, instance, **kwargs):

    
    if instance.pk:
        old_instance = BiometricAttendance.objects.get(pk=instance.pk)
        if old_instance.check_out is None and instance.check_out is not None:
            # Check-out is being set; submit associated tasks
            Task.objects.filter(
                biometric_attendance=instance,
                status__in=['pending', 'in_progress']
            ).update(status='submitted')


@receiver(pre_save, sender=ManualAttendance)
def submit_tasks_on_manual_checkout(sender, instance, **kwargs):
   
    if instance.pk:
        old_instance = ManualAttendance.objects.get(pk=instance.pk)
        if old_instance.check_out is None and instance.check_out is not None:
          
            Task.objects.filter(
                manual_attendance=instance,
                status__in=['pending', 'in_progress']
            ).update(status='submitted')
