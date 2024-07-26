# from django.core.mail import send_mail
# import random
# from django.conf import settings
# from user_management.models import User

# def send_otp_via_email(email,otp):
#     subject=f'Welcome to Tesseract !!- User verification mail'
#     otp=random.randint(1000,9999)
#     message=f'your otp is {otp}'
#     email_from=settings.EMAIL_HOST
#     try:
#         send_mail(subject, message, email_from, [email])
#         user_obj=User.objects.get(email=email)
#         user_obj.otp = otp
#         user_obj.save()
#         print(f"OTP sent successfully to {email}")
#         print(otp)
#     except Exception as e:
#         print(f"Error sending OTP to {email}: {e}")
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import random
from django.conf import settings
from user_management.models import User

def send_otp_via_email(email,otp):
    subject = 'Welcome to Tesseract!! - User verification mail'
    otp = random.randint(1000, 9999)
    context = {'otp': otp}
    html_content = render_to_string('otpstyle.html', context)
    text_content = strip_tags(html_content)
    email_from = settings.EMAIL_HOST_USER  # Use EMAIL_HOST_USER for the sender's email address

    try:
        msg = EmailMultiAlternatives(subject, text_content, email_from, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        user_obj = User.objects.get(email=email)
        user_obj.otp = otp
        user_obj.save()

        print(f"OTP sent successfully to {email}")
        print(otp)
    except Exception as e:
        print(f"Error sending OTP to {email}: {e}")

def send_approval(email):
    subject = 'Tesseract-Teacher Request approved mail'
    html_content = render_to_string('teacherapproval.html')
    text_content = strip_tags(html_content)
    email_from = settings.EMAIL_HOST_USER 

    try:
        msg = EmailMultiAlternatives(subject, text_content, email_from, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        print(f"approval sent successfully to {email}")
    except Exception as e:
        print(f"Error sending approval to {email}: {e}")