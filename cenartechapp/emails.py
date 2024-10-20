from django.conf import settings
import smtplib
from email.message import EmailMessage
from django.contrib import messages




def send_email(request, subject, recipient, body):
    try:
        smtp = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
        smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = settings.EMAIL_HOST_USER
        msg['To'] = recipient
        msg.add_alternative(body, subtype='html')
        smtp.send_message(msg)
        smtp.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}")
        messages.error(request, f"Failed to send email, please check your internet connection!")
        return False