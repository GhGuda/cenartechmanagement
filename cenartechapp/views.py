from django.shortcuts import render, redirect, HttpResponse
from cenartechapp.email_auth import EmailBackend
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from django.conf import settings
import smtplib
from email.message import EmailMessage




EMAIL_HOST_USER = settings.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = settings.EMAIL_HOST_PASSWORD
EMAIL_HOST = settings.EMAIL_HOST
EMAIL_PORT = settings.EMAIL_PORT

schoolname=settings.SCHOOL_NAME


def Stafftype(request):
    staff = Staff.objects.get(staff_name=request.user)
    return render(request, "includes/sidebar.html", {"staff":staff})


def Login(request):
    return render(request, 'index.html')



def doLogin(request):
    if request.method == "POST":
        # Authenticate the user
        if "@" in request.POST['email']:
            user = EmailBackend.authenticate(request, username=request.POST['email'].lower(), 
                                         password=request.POST['password'].lower())
        else:
            user = authenticate(request, username=request.POST['email'].lower(), 
                                         password=request.POST['password'].lower())
        
        if user is not None:
            # Establish SMTP connection
            try:
                smtp = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
                smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                
                
                msg = EmailMessage()
                msg['Subject'] = "New Login Detected"
                msg['From'] = EMAIL_HOST_USER
                msg['To'] = user.email

                if user.email:
                    msg.add_alternative(
                        f"""
                        <html>
                        <body>
                            <p>Dear <strong>{user.first_name.capitalize()} {user.last_name.capitalize()}</strong>,</p>
                            <p>
                                We noticed a new login to your account on <strong>{schoolname}</strong> platform. If this was you, there's nothing to worry about.
                                However, if you did not initiate this login, please contact our support team immediately.
                            </p>
                            <p>
                                Stay secure, and thank you for being part of our community.
                            </p>
                            <p>
                                For any assistance, feel free to reach out to us at:
                            </p>
                            <p>Email: <a href="mailto:ghguda@gmail.com">ghguda@gmail.com</a></p>
                            <p>Phone: <a href="tel:+233594074717">0594074717</a></p>
                            <p style="margin-top: 20px;">Best regards,</p>
                            <p><strong>{schoolname} Security Team</strong></p>
                        </body>
                        </html>
                        """,
                        subtype='html'
                    )
                    smtp.send_message(msg)
                    
            except:
                messages.error(request, "Error logging in, check your internet connection!")
                return render(request, 'login.html', {
                        "entered_data": request.POST
                })

            login(request, user)
            user_type = user.user_type
            
            if user_type == 'HOD':
                messages.success(request, "Login successful!")
                return redirect('hod_home')
            elif user_type == 'STAFF':
                messages.success(request, "Login successful!")
                return redirect('staff_home')
            elif user_type == 'STUDENT':
                messages.success(request, "Login successful!")
                return redirect('student_home')
            else:
                messages.error(request, "User type is not recognized.")
                return render(request, 'login.html', {
                        "entered_data": request.POST
                })
        else:
            if "@" in request.POST['email']:
                messages.error(request, "Email and password are invalid!")
                return render(request, 'login.html', {
                        "entered_data": request.POST
                    })
                
            else:
                email=request.POST['email']
                messages.error(request, "Username and password are invalid!")
                return render(request, 'login.html', {
                        "entered_data": request.POST
                    })
    else:
        context={
            'email':email,
        }
        # Render the login page for GET request
        return render(request, 'index.html', context)
    

def doLogout(request):
    try:
        logout(request)
        messages.success(request, "Logout successful!")
        return redirect('login')
    except:
        pass



@login_required(login_url="login")
def profile(request):
    try:
        user = CustomUser.objects.get(username=request.user)

        context={
            "user":user,
        }
        
        if request.method == "POST":
            email = request.POST['email'].lower().replace(' ', '')
            
            
            
            try:
                if email == "":
                    user.email =user.email
                    messages.error(request, 'Your email cannot be empty.')
                elif email!=user.email:
                    current_userEmail = CustomUser.objects.filter(email__iexact=email)
                    if current_userEmail.exists():
                        user.email = user.email
                        messages.error(request, 'Email taken!')
                    else:
                        user.email = email
                        messages.success(request, 'Your email updated successfully.')
                    
                user.save()
                return redirect('profile')
                        
            except:
                    messages.error(request, 'Profile failed to update.')
                    return redirect('profile')
                
        
        else:           
            return render(request, 'profile.html', context)
    except:
        messages.error(request, 'Profile failed to show!')
        user_type = user.user_type
            
        if user_type == 'HOD':
            return redirect('hod_home')
        elif user_type == 'STAFF':
            return redirect('staff_home')
        elif user_type == 'STUDENT':
            return redirect('student_home')
        
        



