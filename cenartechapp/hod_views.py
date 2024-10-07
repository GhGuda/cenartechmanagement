from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Staff
from .models import Student
from .models import Class_Form
from .models import Term
from .models import Subject
from .models import CustomUser
from .models import PassedStudents
from .models import YearlyPassedStudents
from .models import YearlyAdmittedStudents
from .models import AdmittedStudents
from django.contrib import messages
from .staff_view import get_years
from django.db.models import Count
from django.db.models import Q
from django.conf import settings
import smtplib
from email.message import EmailMessage
import re

from .utils import delete_report_cards




EMAIL_HOST_USER = settings.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = settings.EMAIL_HOST_PASSWORD
EMAIL_HOST = settings.EMAIL_HOST
EMAIL_PORT = settings.EMAIL_PORT


schoolweb = settings.SCHOOL_WEB

schoolname=settings.SCHOOL_NAME



def is_valid_input(input_string):
    pattern = r'^[a-zA-Z0-9@.\-_]+$'
    return bool(re.match(pattern, input_string))


@login_required(login_url='/')
def home(request):
    students = Student.objects.all().exclude(user__is_active=False).exclude(class_id__name="Completed Class").count()
    staffs = Staff.objects.all().count()
    subject = Subject.objects.values('subject_name').distinct()


    term = Term.objects.first()
    student_gender_male = Student.objects.filter(gender="male").exclude(user__is_active=False).count()
    student_gender_female = Student.objects.filter(gender="female").exclude(user__is_active=False).count()
    current_year, previous_year = get_years(request)
    
    # PassedStudents doings
    past_students = PassedStudents.objects.filter(term=term.term, year=current_year) \
    .values('class_form') \
    .annotate(student_count=Count('id')) \
    .order_by('class_form')
    
    yearly_passed_students = YearlyPassedStudents.objects.all()
    year_count = PassedStudents.objects.filter(year=current_year).count()
    
    
    # Admitted Students Doings
    admit_students = AdmittedStudents.objects.filter(term=term.term, year=current_year) \
    .values('class_form') \
    .annotate(student_count=Count('id')) \
    .order_by('class_form')
    
    admitted_year_count = AdmittedStudents.objects.filter(year=current_year).count()
    admitted_students = YearlyAdmittedStudents.objects.all()

    
    
    context={
        'students':students,
        'staffs':staffs,
        'subject':subject,
        'term':term,
        # PassedStudents doings
        'year_count':year_count,
        'passed':past_students,
        'current_year':current_year,
        'yearly_passed_students':yearly_passed_students,
        
        # Admitted Students Doings
        'admitted':admit_students,
        'admitted_year_count':admitted_year_count,
        'admitted_students':admitted_students,
        
        'student_gender_male':student_gender_male,
        'student_gender_female':student_gender_female,
    }
    return render(request, 'hod/home.html', context)






@login_required(login_url='/')
def search(request):
    data = None
    try:
        if request.method == "POST":
            search = request.POST['search']
            if search:
                students_search = Student.objects.filter(
                    Q(user__username__icontains=search) |
                    Q(user__first_name__icontains=search) |
                    Q(user__last_name__icontains=search) |
                    Q(user__middle_name__icontains=search) |
                    Q(user__email__icontains=search) |
                    Q(class_id__name__icontains=search) |
                    Q(phone__icontains=search) |
                    Q(religion__icontains=search)
                )
                
                staffs_search = Staff.objects.filter(
                    Q(staff_name__username__icontains=search) |
                    Q(staff_name__first_name__icontains=search) |
                    Q(staff_name__last_name__icontains=search) |
                    Q(staff_name__middle_name__icontains=search) |
                    Q(staff_name__email__icontains=search) |
                    Q(phone__icontains=search)
                )
                data = {
                    "students":students_search,
                    "staffs":staffs_search,
                    "param":search,
                }
    except:
        messages.error(request, "An error occurred, please try again!")
    return render(request, 'hod/search.html', data)







@login_required(login_url='/')
def add_student(request):
    student_classes = Class_Form.objects.all().exclude(name="Completed Class")

    if request.method == "POST":
        try:
            profile_pic = request.FILES.get('profile_pic', 'blank.webp')
            fname = request.POST["fname"].lower().replace(' ', '')
            lname = request.POST["lname"].lower().replace(' ', '')
            mname = request.POST["mname"].lower()
            email = request.POST['email'].lower().replace(' ', '')
            username = request.POST['username'].lower().replace(' ', '').replace("@", "")
            gender = request.POST['gender']
            dob = request.POST['dob']
            class_id = request.POST['class']
            religion = request.POST['religion'].lower()
            phone = request.POST['phone']
            student_password = request.POST['student_password'].lower()

            # Parents' information
            father_name = request.POST['father_name']
            father_number = request.POST['father_number']
            father_email = request.POST['father_email']
            mother_email = request.POST['mother_email']
            mother_name = request.POST['mother_name']
            mother_number = request.POST['mother_number']
                
            # Student's address
            address1 = request.POST['address1']
            address2 = request.POST['address2']
            
            max_file_size = 5 * 1024 * 1024
            
            if profile_pic:
                if profile_pic.size > max_file_size:
                    messages.error(request, "Profile picture is too large. Maximum size allowed is 5MB!")
                    return render(request, 'hod/add_student.html', {
                        "class": student_classes,
                        "entered_data": request.POST,
                    })
            
            
            if len(student_password) <= 7:
                messages.error(request, "Password must be more than 7 letters long!")
                return render(request, 'hod/add_student.html', {
                    "entered_data": request.POST,
                    "class": student_classes,
                })
            
            if email=="" and CustomUser.objects.filter(email=""):
                pass
            else:
                if CustomUser.objects.filter(email__iexact=email).exists():
                    messages.error(request, "Email already exists!")
                    return render(request, 'hod/add_student.html', {
                        "entered_data": request.POST,
                        "class": student_classes,
                    })
                
            if gender == "Select Gender":
                messages.error(request, "Select Student Gender!")
                return render(request, 'hod/add_student.html', {
                    "entered_data": request.POST,
                    "class": student_classes,
                })
            
            if class_id == "Select Class/Form":
                messages.error(request, "Select Student Class/Form!")
                return render(request, 'hod/add_student.html', {
                    "entered_data": request.POST,
                    "class": student_classes,  
                })
            elif CustomUser.objects.filter(username__iexact=username).exists():
                messages.error(request, "Username already exists!")
                return render(request, 'hod/add_student.html', {
                    "entered_data": request.POST,
                    "class": student_classes,
                })
            else:
                # Send mail
                email_sent = False

                # Attempt to send the email to the student's email
                if email:
                    try:
                        smtp = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
                        smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                        msg = EmailMessage()
                        msg['Subject'] = f"Welcome to {schoolname}"
                        msg['From'] = settings.EMAIL_HOST_USER
                        msg['To'] = email

                        msg.add_alternative(
                            f"""
                            <html>
                            <body>
                                <h2 style="color: #2E86C1;">Welcome to {schoolname}!</h2>
                                <p>Dear <strong>{str(fname).capitalize()} {str(mname).capitalize()} {str(lname).capitalize()}</strong>,</p>
                                <p>
                                    We are thrilled to welcome you to {schoolname}! Our community is dedicated to providing
                                    a nurturing environment that fosters academic excellence and personal growth.
                                </p>
                                <p>
                                    We hope you enjoy your experience with us, and we look forward to supporting you on your educational journey.
                                </p>
                                <h3 style="margin-top: 20px; text-align:center;">Here Are Your Log In Credentials.</h3>
                                <strong style="margin-top: 20px; color:red; text-align:center;">Please keep these credentials confidential!</strong>
                                <p>Username: {str(username).capitalize()}</p>
                                <p>Email: {str(email).capitalize()}</p>
                                <p>Password: {str(student_password)}</p>
                                <p>Access your dashboard at: <a href="{schoolweb}">{str(schoolweb).upper()}</a></p>
                                <p style="margin-top: 20px;">Best regards,</p>
                                <p><strong>The {schoolname} Team</strong></p>
                            </body>
                            </html>
                            """,
                            subtype='html'
                        )
                        smtp.send_message(msg)
                        smtp.quit()
                        email_sent = True
                    except:
                        messages.error(request, f"Failed to send email, please check your internet connection!")
                        return redirect(add_student)
                
                # Attempt to send the email to the father's email
                if father_email:
                    try:
                        smtp = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
                        smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                        msg = EmailMessage()
                        msg['Subject'] = f"Thank You for Admitting Your Ward to {schoolname}"
                        msg['From'] = settings.EMAIL_HOST_USER
                        msg['To'] = father_email
                        if father_name:
                            greeting = f"Dear Mr. {father_name},"
                        else:
                            greeting = "Dear Parent,"
                            
                        msg.add_alternative(
                            f"""
                            <html>
                            <body>
                                <p>{greeting}</p>
                                <p>Thank you for entrusting us with your ward's education. We are honored to have them as part of the 
                                {schoolname} family. Our commitment is to provide a nurturing environment that promotes both academic 
                                excellence and personal growth.</p>
                                <h3 style="margin-top: 20px; text-align:center;">Here Are Your Ward's Login Credentials</h3>
                                <strong style="margin-top: 20px; color:red; text-align:center;">Please keep these credentials confidential!</strong>
                                <p>Username: <strong>{str(username).capitalize()}</strong></p>
                                <p>Email: <strong>{str(email).capitalize()}</strong></p>
                                <p>Password: <strong>{str(student_password)}</strong></p>
                                <p>Access your ward's dashboard at: <a href="{schoolweb}">{str(schoolweb).upper()}</a></p>
                                <p style="margin-top: 20px;">Best regards,</p>
                                <p><strong>{schoolname}</strong></p>
                            </body>
                            </html>
                            """,
                            subtype='html'
                        )
                        smtp.send_message(msg)
                        smtp.quit()
                        email_sent = True
                    except:
                        messages.error(request, f"Failed to send email to, please check your internet connection!")

                # Attempt to send the email to the mother's email
                if mother_email:
                    try:
                        smtp = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
                        smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                        msg = EmailMessage()
                        msg['Subject'] = f"Thank You for Admitting Your Ward to {schoolname}"
                        msg['From'] = settings.EMAIL_HOST_USER
                        msg['To'] = mother_email
                        if mother_name:
                            greetin = f"Dear Mrs. {mother_name},"
                        else:
                            greetin = "Dear Parent,"
                            
                        msg.add_alternative(
                            f"""
                            <html>
                            <body>
                                <p>{greetin}</p>
                                <p>Thank you for entrusting us with your ward's education. We are honored to have them as part of the 
                                {schoolname} family. Our commitment is to provide a nurturing environment that promotes both academic 
                                excellence and personal growth.</p>
                                <h3 style="margin-top: 20px; text-align:center;">Here Are Your Ward's Login Credentials</h3>
                                <strong style="margin-top: 20px; color:red; text-align:center;">Please keep these credentials confidential!</strong>
                                <p>Username: <strong>{str(username).capitalize()}</strong></p>
                                <p>Email: <strong>{str(email).capitalize()}</strong></p>
                                <p>Password: <strong>{str(student_password)}</strong></p>
                                <p>Access your ward's dashboard at: <a href="{schoolweb}">{str(schoolweb).upper()}</a></p>
                                <p style="margin-top: 20px;">Best regards,</p>
                                <p><strong>{schoolname}</strong></p>
                            </body>
                            </html>
                            """,
                            subtype='html'
                        )
                        smtp.send_message(msg)
                        smtp.quit()
                        email_sent = True
                    except:
                        messages.error(request, f"Failed to send email, please check your internet connection!")

                # Save the user and student data if at least one email was provided and sent successfully
                if email_sent or (not email and not father_email and not mother_email):
                    user = CustomUser.objects.create_user(
                        username=username,
                        password=student_password,
                        first_name=fname,
                        last_name=lname,
                        middle_name=mname,
                        email=email,
                        profile_pic=profile_pic,
                        user_type="STUDENT",
                    )

                    # Get class and create student
                    student_class = Class_Form.objects.get(id=class_id)
                    student = Student.objects.create(
                        user=user,
                        gender=gender,
                        dob=dob,
                        class_id=student_class,
                        religion=religion,
                        phone=phone,
                        father_name=father_name,
                        father_number=father_number,
                        father_email=father_email,
                        mother_name=mother_name,
                        mother_email=mother_email,
                        mother_number=mother_number,
                        address1=address1,
                        address2=address2,
                    )

                    current_year, previous_year = get_years(request)
                    term = Term.objects.get(pk=1)

                    admitted_students = AdmittedStudents.objects.create(
                        class_form=student.class_id.name,
                        term=term.term,
                        year=current_year,
                    )
                    admitted_students.save()

                    yearly, created = YearlyAdmittedStudents.objects.update_or_create(
                        year=current_year,
                    )
                    yearly.number += 1
                    yearly.save()

                    # Ensure student is saved before assigning subjects
                    student.save()
                    student.assign_subjects()
                    messages.success(request, "Student added successfully!")
                    return redirect('add_student')

        except:
            messages.error(request, f"Error: Failed to add student!")
            return render(request, 'hod/add_student.html', {
                "entered_data": request.POST
            })

    context = {
        "class": student_classes,
    }
    return render(request, 'hod/add_student.html', context)



@login_required(login_url='/')
def view_student(request):
    students = Student.objects.all().exclude(class_id__name="Completed Class").exclude(user__is_active=False)


    context={
        'students':students
    }
    return render(request, 'hod/view_student.html', context)




@login_required(login_url='/')
def delete_student(request, user_name):
    try:
        user = get_object_or_404(CustomUser, username=user_name)
        student= get_object_or_404(Student, user=user)
        current_year, previous_year = get_years(request)
        term = Term.objects.get(pk=1)
        
        passed_stedents = PassedStudents.objects.create(
            class_form = student.class_id.name,
            term = term.term,
            year= current_year
        )
        passed_stedents.save()
        
        yearlyp, created = YearlyPassedStudents.objects.update_or_create(
            year = current_year,
        )
        yearlyp.number = yearlyp.number + 1
        yearlyp.save()
        
        
        student.year_stopped = current_year
        student.term_stopped = term.term
        student.save()
        
        yearly = YearlyAdmittedStudents.objects.get(
            year = student.user.date_joined.year,
        )
        yearly.number = yearly.number - 1
        yearly.save()
        
        
        admitted =  AdmittedStudents.objects.filter(class_form = student.class_id.name, year=student.user.date_joined.year).first()
        admitted.delete()
        
        user.is_active = False
        user.save()
        messages.success(request, f'{user.first_name.capitalize()} {user.middle_name.capitalize()} {user.last_name.capitalize()} was deleted successfully!')
    except:
        messages.error(request, "Error deleting student!")
    return redirect('view_student')




@login_required(login_url='/')
def activate_user(request, user_name):
    try:
        user = get_object_or_404(CustomUser, username=user_name)
        student = get_object_or_404(Student, user=user)
        user.is_active = True
        yearly = PassedStudents.objects.filter(class_form=student.class_id.name, year=student.year_stopped).first()
        yearly_passed_students = YearlyPassedStudents.objects.get(year=student.year_stopped)
        yearly_passed_students.number = yearly_passed_students.number - 1
        yearly_passed_students.save()
        yearly.delete()
        
        current_year, previouse_year = get_years(request)
        
        
        admitted_stedents = AdmittedStudents.objects.create(
            class_form = student.class_id.name,
            term = student.term_stopped,
            year= current_year
        )
        admitted_stedents.save()
        admitted_students, created = YearlyAdmittedStudents.objects.update_or_create(year=student.user.date_joined.year)
        
        admitted_students.number = admitted_students.number +1
        admitted_students.save()
        
        student.year_stopped = ""
        student.term_stopped = ""
        student.save()
        user.save()
        messages.success(request, f'{user.first_name.capitalize()} {user.middle_name.capitalize()} {user.last_name.capitalize()} has been activated successfully!')
        return redirect(student_details, user)
    except:
        messages.error(request, "Error activating student!")
        return redirect(student_details, user)




@login_required(login_url='/')
def edit_student(request, user_name):
    user = get_object_or_404(CustomUser, username=user_name)
    student = get_object_or_404(Student, user=user)
    classes = Class_Form.objects.all().exclude(name="Completed Class")
    term = Term.objects.get(pk=1)
    try:
        if request.method == "POST":
            firstname = request.POST["fname"].capitalize().replace(' ', '')
            lastname = request.POST["lname"].capitalize().replace(' ', '')
            middlename = request.POST["mname"].capitalize().replace(' ', '')
            email = request.POST['email'].lower().replace(' ', '')
            username = user.username
            gender = request.POST['gender']
            
            dob = request.POST['dob']
            class_id = request.POST['class']
            religion = request.POST['religion'].capitalize()
            phone = request.POST['phone']

            # Parents information
            father_name = request.POST['father_name']
            father_number = request.POST['father_number']
            father_email = request.POST['father_email']
            mother_email = request.POST['mother_email']
            mother_name = request.POST['mother_name']
            mother_number = request.POST['mother_number']

            # Student address
            address1 = request.POST['address1']
            address2 = request.POST['address2']

            # Username and Email uniqueness check
            if username != user.username:
                if CustomUser.objects.filter(username__iexact=username).exists():
                    messages.error(request, "Username already exists!")
                    return redirect('edit_student', user_name)
                else:
                    user.username = username
                    user.save()
                    
       
                
            if email != user.email:
                if email == "":
                    user.email = ""
                elif CustomUser.objects.filter(email__iexact=email).exists():
                    messages.error(request, "Email already exists!")
                    return redirect('edit_student', username)
                else:
                    user.email = email
                    user.save()

                

                
            if class_id != "Select Class/Form":    
                admitted = AdmittedStudents.objects.filter(class_form=student.class_id.name, year=student.user.date_joined.year).first()
                admitted.delete()
                
                student_class_id = Class_Form.objects.get(id=class_id)
                
                
                admitted_stedents = AdmittedStudents.objects.create(
                    class_form = student_class_id.name,
                    term = term.term,
                    year= student.user.date_joined.year
                )
                admitted_stedents.save()
                
                
                yearadmitted = YearlyAdmittedStudents.objects.get(year=student.user.date_joined.year)
                yearadmitted.number = yearadmitted.number - 1
                yearadmitted.save()
                    
                admitted_students, created = YearlyAdmittedStudents.objects.update_or_create(year=student.user.date_joined.year)
                
                admitted_students.number = admitted_students.number +1
                admitted_students.save()
            
            

            # Update user details
            user.first_name = firstname
            user.last_name = lastname
            user.middle_name = middlename
            if gender !="":
                student.gender = gender
            else:
                student.gender = student.gender
            student.dob = dob
            if class_id != "Select Class/Form":
                student.class_id = Class_Form.objects.get(id=class_id)
            else:
                student.class_id = student.class_id
            student.religion = religion
            student.phone = phone
            student.father_name = father_name
            student.father_number = father_number
            student.father_email = father_email
            student.mother_name = mother_name
            student.mother_email = mother_email
            student.mother_number = mother_number
            student.address1 = address1
            student.address2 = address2
            student.subjects.clear()
            student.assign_subjects()
            student.save()

            messages.success(request, "Student details edited successfully!")
            return redirect('edit_student', user_name)
    except:
        messages.error(request, "Error updating student details!")
        return redirect('edit_student', user_name)

    context = {
        'student': student,
        'class': classes,
    }

    return render(request, 'hod/edit_student.html', context)




@login_required(login_url='/')
def student_details(request, user_name):
    user = get_object_or_404(CustomUser, username=user_name)
    students = get_object_or_404(Student,user__username=user)
    
    studentclass = Class_Form.objects.all().exclude(name="Completed Class")
    
    
    try:
        if request.method == "POST":
            password = request.POST['password']
            password2 = request.POST['password2']
            
            if not is_valid_input(password) or not is_valid_input(password2):
                messages.error(request, "Invalid characters detected in password.")
                return redirect(student_details, user.username)
        
            if len(password) <=7:
                messages.error(request, "Password must be more than 7 letters long!")
                return redirect(student_details, user.username)
            elif password == password2:
                students.user.set_password(password)
                students.user.save()
                messages.success(request, "Password changed successfully!")
                return redirect(student_details, user.username)
            else:
                messages.error(request, "Password did not match!")
                return redirect(student_details, user.username)
    except:
        messages.error(request, "Password change failed!")
        return redirect(student_details, user.username)
        
    context={
        'student':students,
        "class":studentclass,

    }
    return render(request, 'hod/students_details.html', context)





@login_required(login_url='/')
def add_staff(request):
    class_forms = Class_Form.objects.all().exclude(name="Completed Class")
    subject = Subject.objects.values('subject_name').distinct()
    try:
        if request.method == "POST":
            profile_pic = request.FILES.get('profile_pic')
            fname = request.POST["fname"].capitalize().replace(' ', '')
            lname = request.POST["lname"].capitalize().replace(' ', '')
            mname = request.POST["mname"].capitalize()
            email = request.POST['email'].lower().replace(' ', '')
            username = request.POST['username'].lower().replace(' ', '').replace("@", "")
            gender = request.POST['gender']
            class_form_ids = request.POST['class_form']
            class_form_teach = request.POST["class_form_teach"]
            stafftype = request.POST['staff_type']
            subject_teach = request.POST['subject_teach']
            state = request.POST['state']
            religion = request.POST['religion']
            phone = request.POST['phone']
            staff_password1 = request.POST['password1'].lower()
            staff_password2 = request.POST['password2'].lower()
            address = request.POST['address']
            city = request.POST['city']
            zipcode = request.POST['zipcode']
            country = request.POST['country']
            qualification = request.POST['qualification']
            experience = request.POST['experience']
            
            
            max_file_size = 5 * 1024 * 1024
            
            if profile_pic:
                if profile_pic.size > max_file_size:
                    messages.error(request, "Profile picture is too large. Maximum size allowed is 5MB!")
                    return render(request, 'hod/add_staff.html', {
                        "class": class_forms,
                        "subject": subject,
                        "entered_data": request.POST
                    })
            
            if stafftype == "Class Manager":
                # Call `.exists()` to check if the subject exists
                checker = Subject.objects.filter(class_Form__name=class_form_ids, subject_name=subject_teach).exists()
                
                if checker:
                    pass  # Proceed if the subject exists
                else:
                    messages.error(request, "Subject did not match the selected class!")
                    return render(request, 'hod/add_staff.html', {
                        "class": class_forms,
                        "subject": subject,
                        "entered_data": request.POST
                    })

            # For Subject Teacher
            if stafftype == "Subject Teacher":
                # Call `.exists()` to check if the subject exists
                checker = Subject.objects.filter(class_Form__name=class_form_teach, subject_name=subject_teach).exists()
            
                if checker:
                    pass  # Proceed if the subject exists
                else:
                    messages.error(request, "Subject did not match the selected class!")
                    return render(request, 'hod/add_staff.html', {
                        "class": class_forms,
                        "subject": subject,
                        "entered_data": request.POST
                    })
        
            
            if email=="" and CustomUser.objects.filter(email=""):
                    pass
            else:
                if CustomUser.objects.filter(email__iexact=email).exists():
                    messages.error(request, "Email already exists!")
                    return render(request, 'hod/add_staff.html', {
                        "class": class_forms,
                        "subject": subject,
                        "entered_data": request.POST
                    })
            
            if stafftype == "Staff Type":
                messages.error(request, "Staff Type field can't be empty!")
                return render(request, 'hod/add_staff.html', {
                        "class": class_forms,
                        "subject": subject,
                        "entered_data": request.POST
                    })
                
            if stafftype == "Class Manager":
                if class_form_ids == "Select Class/Form":
                    messages.error(request, "Select Class/Form, field can't be empty!")
                    return render(request, 'hod/add_staff.html', {
                            "class": class_forms,
                            "subject": subject,
                            "entered_data": request.POST
                        })
                    
                
            else:
                if class_form_teach == "Select Class/Form":
                    messages.error(request, "Select Class/Form, field can't be empty!")
                    return render(request, 'hod/add_staff.html', {
                            "class": class_forms,
                            "subject": subject,
                            "entered_data": request.POST
                        })
            
                
            if subject_teach == "Select Subject":
                messages.error(request, "Select Subject, field can't be empty!")
                return render(request, 'hod/add_staff.html', {
                        "class": class_forms,
                        "subject": subject,
                        "entered_data": request.POST
                    })
            
                            
            

            if staff_password1 == staff_password2:
                if gender == "Gender":
                    messages.error(request, "Gender field can't be empty!")
                    return render(request, 'hod/add_staff.html', {
                        "class": class_forms,
                        "subject": subject,
                        "entered_data": request.POST
                    })
                if len(staff_password1) <= 7:
                    messages.error(request, "Password must be more than 7 letters long!")
                    return render(request, 'hod/add_staff.html', {
                        "class": class_forms,
                        "subject": subject,
                        "entered_data": request.POST
                    })
                if CustomUser.objects.filter(username__iexact=username).exists():
                    messages.error(request, "Username already exists!")
                    return render(request, 'hod/add_staff.html', {
                        "class": class_forms,
                        "subject": subject,
                        "entered_data": request.POST
                    })
                
                else:
                    
                    email_sent = False
                    if email:
                        try:
                            smtp = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
                            smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                            msg = EmailMessage()
                            msg['Subject'] = f"Welcome to {schoolname}"
                            msg['From'] = EMAIL_HOST_USER
                            msg['To'] = email
                            
                            
                            

                            msg.add_alternative(
                                f"""
                                <html>
                                <body>
                                    <h2 style="color: #2E86C1;">Welcome to {schoolname}!</h2>
                                    <p>Dear <strong>{str(fname).capitalize()} {str(mname).capitalize()} {str(lname).capitalize()}</strong>,</p>
                                    <p>
                                        We are delighted to welcome you to {schoolname}! As a valued member of our community, you play a crucial role in our mission to provide an exceptional learning environment.
                                    </p>
                                    <p>
                                        Here at {schoolname}, we are committed to supporting you and ensuring your experience with us is both rewarding and fulfilling.
                                    </p>
                                    <h3 style="margin-top: 20px; text-align:center;">Your Log In Credentials</h3>
                                    <strong style="margin-top: 20px; color:red; text-align:center;">Please keep these credentials confidential!</strong>
                                    <p><strong>Username:</strong> {str(username).capitalize()}</p>
                                    <p><strong>Email:</strong> {str(email).capitalize()}</p>
                                    <p><strong>Password:</strong> {str(staff_password1)}</p>
                                    <p>Access your dashboard at: <a href="{schoolweb}">{str(schoolweb).upper()}</a></p>
                                    <p style="margin-top: 20px;">Best regards,</p>
                                    <p><strong>{schoolname}</strong></p>
                                </body>
                                </html>
                                """,
                                subtype='html'
                            )
                            smtp.send_message(msg)
                            smtp.quit()
                            email_sent = True
                        except:
                            messages.error(request, f"Please check your internet connection!")
                            return render(request, 'hod/add_staff.html', {
                                "class": class_forms,
                                "subject": subject,
                                "entered_data": request.POST
                            })
                        
                    if email_sent or (not email):
                        if profile_pic is None:
                            profile_pic = "blank.webp"

                        staff_user = CustomUser.objects.create_user(
                            username=username,
                            password=staff_password1,
                            first_name=fname,
                            last_name=lname,
                            middle_name=mname,
                            email=email,
                            profile_pic=profile_pic,
                            user_type="STAFF",
                        )

                        staff = Staff.objects.create(
                            staff_name=staff_user,
                            gender=gender,
                            stafftype=stafftype,
                            state=state,
                            religion=religion,
                            phone=phone,
                            address=address,
                            city=city,
                            zipcode=zipcode,
                            country=country,
                            experience=experience,
                            qualification=qualification,
                        )
                        
                        if stafftype == "Class Manager":
                            # Get the class_form_instance for the class to be managed
                            class_form_instance = Class_Form.objects.filter(name=class_form_ids)
                            
                            # Loop through each class to get the class name
                            for classes in class_form_instance:
                                name = classes.name

                            # Combine querysets to get any existing staff managing the same class and teaching the subject
                            staffs_with_class_and_sub = (
                                Staff.objects.filter(class_managed__name=name, subject_teacher_subject__subject_name=subject_teach) |
                                Staff.objects.filter(subject_teacher_class__name=name, subject_teacher_subject__subject_name=subject_teach)
                            ).distinct()

                            # Remove the class management and subject assignment from these staff members
                            for staff_member in staffs_with_class_and_sub:
                                staff_member.class_managed.remove(classes)  # Remove the class from managed classes
                                staff_member.subject_teacher_subject.remove(subject_teach)
                                staff_member.save()
                            
                            # Get or create the subject for the class
                            subjectm = Subject.objects.filter(class_Form=classes.pk, subject_name=subject_teach)
                            for subjecting in subjectm:
                                subjecting.managed_by = staff
                                subjecting.save()

                            # Assign the staff to teach the subject and manage the class
                            staff.subject_teacher_subject.set(subjectm)
                            staff.class_managed.set(class_form_instance)
                            staff.subject_teacher_class.set(class_form_instance)

                            # Set this staff as the class manager
                            for class_form in class_form_instance:
                                class_form.managed_by = staff
                                class_form.save()

                        if stafftype == "Subject Teacher":
                            # Get the class the subject teacher is teaching
                            class_form_id = Class_Form.objects.filter(name=class_form_teach)
                            
                            for n in class_form_id:
                                name = n.name
                                class_form_instance2 = Class_Form.objects.get(name=name)
                                
                                subjectss = Subject.objects.filter(class_Form=class_form_instance2.pk, subject_name=subject_teach)
                                subjectssj = Subject.objects.get(class_Form=class_form_instance2.pk, subject_name=subject_teach)
                            # Find existing subject teachers for the class and subject
                                staffs_with_class_nd_subject = Staff.objects.filter(
                                    subject_teacher_class=class_form_instance2, 
                                    subject_teacher_subject__subject_name=subject_teach
                                )
                            

                                # Remove the class and subject assignments from these staff members
                                for staff_member in staffs_with_class_nd_subject:
                                    # staff_member.subject_teacher_class.remove(class_form_instance2)
                                    staff_member.subject_teacher_subject.remove(subjectssj)
                                    staff_member.save()

                            # Update managed_by for each subject
                            for subject in subjectss:
                                subject.managed_by = staff
                                subject.save()
                                        
                            # Assign this staff as a subject teacher for the class
                                staff.subject_teacher_class.set(class_form_id)
                                staff.subject_teacher_subject.set(subjectss)

                            # Do NOT assign the subject teacher to the `managed_by` field
                            # Ensure that `managed_by` is only set for "Class Manager" roles

                        # Save staff details
                        staff_user.save()
                        staff.save()

                messages.success(request, "Staff added successfully!")
                return redirect('add_staff')

            else:
                messages.error(request, "Password did not match!")
                return render(request, 'hod/add_staff.html', {
                        "class": class_forms,
                        "subject": subject,
                        "entered_data": request.POST
                    })
    except:
        messages.error(request, "Unexpected error occured!")
        return redirect('add_staff')
    context = {
        "class": class_forms,
        "subject": subject,
    }
    return render(request, 'hod/add_staff.html', context)




@login_required(login_url='/')
def edit_staff(request, staff):
    staff_user = get_object_or_404(CustomUser, username=staff)
    staff = get_object_or_404(Staff, staff_name=staff_user)
    class_forms = Class_Form.objects.all().exclude(name="Completed Class")

    if request.method == "POST":
        fname = request.POST["fname"].capitalize().replace(' ', '')
        lname = request.POST["lname"].capitalize().replace(' ', '')
        mname = request.POST["mname"].capitalize().replace(' ', '')
        email = request.POST['email'].lower().replace(' ', '')
        username = staff.staff_name.username
        gender = request.POST['gender'].capitalize()
        stafftype = 'Class Manager'
        # class_form_input = request.POST.getlist('class_form')
        state = request.POST['state']
        religion = request.POST['religion']
        phone = request.POST['phone']
        address = request.POST['address']
        city = request.POST['city']
        zipcode = request.POST['zipcode']
        country = request.POST['country']
        qualification = request.POST['qualification']
        experience = request.POST['experience']


        try:
            if username != staff_user.username:
                if CustomUser.objects.filter(username__iexact=username).exists():
                    messages.error(request, "Username exists!")
                    return redirect("edit_staff", staff_user.username)
                else:
                    staff_user.username = username

            if email != staff_user.email:
                if email == "":
                    staff_user.email = ""
                elif CustomUser.objects.filter(email__iexact=email).exists():
                    messages.error(request, "Email already exists!")
                    return redirect("edit_staff", staff_user.username)
                else:
                    staff_user.email = email
                    
                
            staff_user.first_name = fname
            staff_user.last_name = lname
            staff_user.middle_name = mname
            staff.gender = gender
            staff.stafftype = stafftype
            staff.state = state
            staff.religion = religion
            staff.phone = phone
            staff.address = address
            staff.city = city
            staff.zipcode = zipcode
            staff.country = country
            staff.qualification = qualification
            staff.experience = experience
            staff_user.save()
            staff.save()

            messages.success(request, "Staff details edited successfully!")
            return redirect('edit_staff', staff_user.username)
        except Exception as e:
            messages.error(request, f"Error updating staff details: {str(e)}")
            return redirect('edit_staff', staff_user.username)

    context = {
        "staff": staff,
        "class_forms": class_forms,
    }

    return render(request, 'hod/edit_staff.html', context)




@login_required(login_url='/')
def delete_staff(request, staff):
    try:
        staff_user = get_object_or_404(CustomUser, username=staff)
        user = str(staff_user)
        messages.success(request, f'{user.capitalize()} has been deleted successfully!')
        staff_user.delete()
        return redirect("view_staffs")
    except:
        messages.error(request, f'{user.capitalize()} was not deleted successfully!')
        return redirect("view_staffs")
        


@login_required(login_url='/')
def view_staffs(request):
    staffs = Staff.objects.all()

    context = None
    for staff in staffs:
        manager = staff
        clas = Class_Form.objects.filter(managed_by=manager)
        subs = Subject.objects.filter(managed_by=manager)

        context={
            "staffs":staffs,
            "clas":clas,
            "subs":subs,
        }
    return render(request, 'hod/view_staff.html', context)


@login_required(login_url='/')
def view_staff_details(request, staffname):
    staff_user = get_object_or_404(CustomUser, username=staffname)
    staff = get_object_or_404(Staff, staff_name=staff_user)
    try:
        if request.method == "POST":
            password = request.POST["password1"]
            password2 = request.POST["password2"]
            
            if not is_valid_input(password) or not is_valid_input(password2):
                messages.error(request, "Invalid characters detected in password.")
                return redirect(student_details, staffname)

            if len(password) <=7:
                messages.error(request, "Password must be more than 7 letters long!")
                return redirect(view_staff_details, staffname)
            elif password == password2:
                staff_user.set_password(password)
                staff_user.save()
                messages.success(request, "Password changed successfully!")
                return redirect(view_staff_details, staffname)
            else:
                messages.error(request, "Password did not match!")
                return redirect(view_staff_details, staffname)
    except:
        messages.error(request, "Password change failed!")
        return redirect(view_staff_details, staffname)
    context={
        "staff":staff
    }
    return render(request, 'hod/view_staff_details.html', context)





@login_required(login_url='/')
def assign_staffs(request):
    class_form = Class_Form.objects.all().exclude(name="Completed Class")
    staff = Staff.objects.all()
    subjects = Subject.objects.values('subject_name').distinct()

    try:
        if request.method == "POST":
            action = request.POST['action']
            if action == "AssignToClass":
                class_form_name = request.POST["class"]
                staff_name = request.POST["staff_name"]

                if class_form_name == "Select Class/Form":
                    messages.error(request, "Please select a Class/Form!")
                    return redirect(assign_staffs)
                elif staff_name == "Staff":
                    messages.error(request, "Please select a staff!")
                    return redirect(assign_staffs)

                # Get the Class_Form instance by ID
                class_form_instance = Class_Form.objects.get(id=class_form_name)

                staffs_with_class = Staff.objects.filter(class_managed=class_form_instance)

                for staff_member in staffs_with_class:
                    staff_member.class_managed.remove(class_form_instance)

                    if not staff_member.class_managed.exists():
                        staff_member.stafftype = "Subject Teacher"
                        staff_member.save()

                # Get the selected staff member
                staf = get_object_or_404(Staff, staff_name__username=staff_name)

                # Assign the class to the selected staff member
                staf.class_managed.add(class_form_instance)
                staf.stafftype = "Class Manager"
                class_form_instance.managed_by = staf
                class_form_instance.save()
                staf.save()

                messages.success(request, f"{class_form_instance.name} assigned to staff {staf.staff_name.get_full_name().capitalize()}.")
                return redirect(assign_staffs)

            elif action == "AssignToSubject":
                class_form_name = request.POST.get("subjectClass")
                staff_name = request.POST.get("subjectStaff_name")
                subject_id = request.POST.get('subject')
                

                if class_form_name == "Select Class/Form":
                    messages.error(request, "Please select a Class/Form!")
                    return redirect(assign_staffs)
                elif staff_name == "Staff":
                    messages.error(request, "Please select a staff!")
                    return redirect(assign_staffs)
                elif subject_id == "Select Subject":
                    messages.error(request, "Please select a subject!")
                    return redirect(assign_staffs)

                # Get the Class_Form and Subject instances
                class_form_instance = Class_Form.objects.get(id=class_form_name)
                try:
                    subject_instance = Subject.objects.get(subject_name=subject_id, class_Form=class_form_instance)
                    staff_with_subject = Staff.objects.filter(subject_teacher_class=class_form_instance, subject_teacher_subject=subject_instance)
                        
                    if staff_with_subject.exists():
                        # Remove the subject from the current staff managing it
                        for current_staff in staff_with_subject:
                            current_staff.subject_teacher_subject.remove(subject_instance)
                            
                            remaining_subjects_in_class = current_staff.subject_teacher_subject.filter(class_Form=class_form_instance)
                            
                            if not remaining_subjects_in_class.exists():
                                current_staff.subject_teacher_class.remove(class_form_instance)
                            
                            sub4staff = Subject.objects.get(subject_name=subject_id, class_Form=class_form_instance, managed_by=current_staff)
                            sub4staff.managed_by = None
                            sub4staff.save()
                            current_staff.save()
                    new_staff = get_object_or_404(Staff, staff_name__username=staff_name)
                    new_staff.subject_teacher_subject.add(subject_instance)
                    new_staff.subject_teacher_class.add(class_form_instance)
                    substaff = Subject.objects.get(subject_name=subject_id, class_Form=class_form_instance)
                    substaff.managed_by = new_staff
                    substaff.save()
                    new_staff.save()

                    messages.success(request, f"{subject_instance.subject_name} for {class_form_instance.name} assigned to {new_staff.staff_name.get_full_name().capitalize()}.")
                    return redirect(assign_staffs)
                except:
                    messages.error(request, f"{subject_id} is not associated to {class_form_instance} ")
                    return redirect(assign_staffs)
                    
    except:
        messages.error(request, "An error occurred!")
        return redirect(assign_staffs)
        
    data = {
        'class': class_form,
        'staffs': staff,
        'subject': subjects,
    }
    return render(request, 'hod/assign_staffs.html', data)





@login_required(login_url='/')
def add_term(request):
    term = Term.objects.get(pk=1)
    students = Student.objects.all().exclude(user__is_active=False).exclude(class_id__name="Completed Class")
    
    
     
    try:
        if request.method == "POST":
            vacation = request.POST['vacation']
            rdate = request.POST['rdate']
            term_value = request.POST['term']
            hod_remark = request.POST['hod_remark']
            cutoffpoint = request.POST['cutoffpoint']

            previous_term = term.term 

            if term_value != "Select Term":
                term.term = term_value
                term.vacation_date = vacation
                term.reopening_date = rdate
                term.hod_remarks = hod_remark
                term.cutOfPoint = cutoffpoint
                for student in students:
                    student.status = ""
                    student.save()
                delete_report_cards()
                term.save()
            
                
                if previous_term == "Three" and term_value == "One":
                    promote_students(request)
                    for student in students:
                        student.total_marks_term_one = 0
                        student.total_marks_term_two = 0
                        student.total_marks_term_three = 0
                        student.overall_total_marks = 0
                        student.save()
    
                    messages.success(request, "Students have been promoted sucessfully!")

                messages.success(request, f"Term updated to '{term_value.capitalize()}' successfully! ")
                return redirect(add_term)
            else:
                messages.error(request, "Failed, please select a term!")
                return redirect(add_term)

    except Exception:
        messages.error(request, f"Could not update term!")
        return redirect(add_term)

    context = {
        'term': term,
    }
    return render(request, 'hod/edit_term.html', context)







def promote_students(request):
    try:
        term = Term.objects.get(pk=1)
        
        
        forms_promotion = {
            "Form One": "Form Two",
            "Form Two": "Form Three",
            "Form Three": ""
        }

        lower_classes_promotion = {
            "Nursery One": "Nursery Two",
            "Nursery Two": "Kindergarten One",
            "Kindergarten One": "Kindergarten Two",
            "Kindergarten Two": "Class One",
            "Class One": "Class Two",
            "Class Two": "Class Three",
            "Class Three": "Class Four",
            "Class Four": "Class Five",
            "Class Five": "Class Six",
            "Class Six": "Form One"
        }

        students = Student.objects.all().exclude(user__is_active=False).exclude(class_id__name="Completed Class")
        

        for student in students:
            current_class = student.class_id.name
            
            

            class_f3 = Class_Form.objects.get(name="Completed Class")
            
            if student.overall_total_marks >= term.cutOfPoint:
                # Handle promotion for students in Form Three, Term Three
                if current_class == "Form Three":
                    class_f3 = Class_Form.objects.get(name="Completed Class")
                    student.class_id = class_f3
                    student.subjects.clear()  # Clear all subjects
                    student.save()
                    continue

                if current_class in forms_promotion:
                    new_class_name = forms_promotion[current_class]
                elif current_class in lower_classes_promotion:
                    new_class_name = lower_classes_promotion[current_class]
                else:
                    new_class_name = None

                if new_class_name:
                    new_class = Class_Form.objects.get(name=new_class_name)
                    student.class_id = new_class
                    student.promoted_to=new_class
                    student.subjects.clear()  
                    student.assign_subjects() 
                    student.save()
            else:
                student.promoted_to = student.class_id
                student.save()  
    except:
        messages.error(request, "An error occured while processing promotion.")
        return redirect(add_term)
        

 
 
 