# from django_rest_passwordreset.signals import reset_password_token_created
# from django.dispatch import receiver

# def send_reset_email(context, user_email):
#     html_message = render_to_string('email.html', context=context)
#     plain_message = strip_tags(html_message)

#     msg = EmailMultiAlternatives(
#         subject=f"Request for resetting password for {user_email}",
#         body=plain_message,
#         from_email='udemezue0009@gmail.com',
#         to=[user_email],
#     )
#     msg.attach_alternative(html_message, 'text/html')
#     msg.send()


# @receiver(reset_password_token_created)
# def password_reset_token_created(sender, reset_password_token, **kwargs):
#     sitelink = 'http://localhost:7000/'
#     token = reset_password_token.key
#     email = reset_password_token.user.email
#     full_link = f"{sitelink}password-reset/?token={token}&email={email}"

#     # print("Token:", token)
#     # print("Reset link:", full_link)

#     context = {
#         'full_link': full_link,
#         'email_address': reset_password_token.user.email,
#     }

#     # Send email in a new thread
#     threading.Thread(target=send_reset_email, args=(
#         context, reset_password_token.user.email)).start()
# #  I want the notification  to be like (a message icon), where if a user gets a message, a read mark will show indicating how many messages he has, then he goes to the message folder and sees all his unread messages which will be in bold black and when he clicks on an unread message, the bold black will change to normal black, and instead of having 3read marks, it will now change to 2)

# # your_app/middleware.py