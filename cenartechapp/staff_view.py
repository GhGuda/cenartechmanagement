from django.shortcuts import render, redirect, get_object_or_404
from .models import Staff
from .models import Student
from .models import Class_Form
from .models import StudentResult
from .models import Term
from .models import Subject
from .models import StudentClasses
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime
from django.template.loader import get_template
import smtplib
from django.conf import settings
import pdfkit
from django.http import HttpResponse
from django.template.loader import render_to_string
import os
from django.core.files.storage import default_storage
from email.message import EmailMessage
from concurrent.futures import ThreadPoolExecutor
from django.http import JsonResponse


EMAIL_HOST_USER = settings.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = settings.EMAIL_HOST_PASSWORD
EMAIL_HOST = settings.EMAIL_HOST
EMAIL_PORT = settings.EMAIL_PORT

schoolweb = settings.SCHOOL_WEB

schoolname=settings.SCHOOL_NAME
school_slogan=settings.SCHOOL_SLOGAN
school_location=settings.SCHOOL_LOCATION
school_number=settings.SCHOOL_NUM

from twilio.rest import Client


@login_required(login_url='/')
def get_years(request):
    current_year = datetime.now().year
    previous_year = current_year - 1
    return current_year, previous_year



@login_required(login_url='/')
def staff_home(request):
    staff = get_object_or_404(Staff, staff_name__username=request.user.username)

    class_form = Class_Form.objects.filter(managed_by=staff)
    
     
    staff_sub_class = staff.subject_teacher_class.all()
    staff_sub = staff.subject_teacher_subject.all()
    term = Term.objects.first()
    
    
    class_id = request.GET.get('class_id')
    action = request.GET.get('action')
    
    # Use set to get unique class names and subject names
    unique_staff_sub_class = set(staff_sub_class.values_list('name', flat=True))
    unique_staff_sub = set(staff_sub.values_list('subject_name', flat=True))

    action = request.GET.get('action')
    students = None
    student_class = None
    subject = None
    is_class_manager = None
    is_subject=None
    show_status_column=None
    try:
        if action is not None and request.method == 'POST':
            class_manager_action = request.POST.get('class_manager_action')
            
            if staff.stafftype == "Class Manager":
                if class_manager_action == "class-managing":
                    class_id = request.POST.get('class_form_manage')
                    if class_id == "Select Class/Form":
                        messages.error(request, "Please select class!")
                        return redirect(staff_home)
                    student_class = Class_Form.objects.get(id=class_id)
                    students = Student.objects.filter(class_id__name=student_class).exclude(user__is_active=False)
                                      
                    for item in students:
                        is_class_manager = item.class_id.managed_by == staff
                        if item.status:
                            show_status_column = any(item.status )
                        
                    if students.exists():
                        pass
                    else:
                        messages.error(request, f"No students registered in {student_class}!")
                        
                        
                elif class_manager_action == "subject-class":
                    class_id = request.POST.get('class_form_subject')
                    
                    if class_id == "Select Class/Form":
                        messages.error(request, "Please select class!")
                        return redirect(staff_home)
                    selected_subject = request.POST.get('subject')
                    
                    if selected_subject == "Subject":
                        messages.error(request, "Please select subject!")
                        return redirect(staff_home)
                    subject = Subject.objects.filter(class_Form__name=class_id, subject_name=selected_subject).first()
                    student_class = Class_Form.objects.get(name=class_id)
                    
                    students = Student.objects.filter(class_id__name=student_class, subjects__subject_name=selected_subject, subjects__managed_by=staff).exclude(user__is_active=False)
                    for item in students:
                        is_subject = is_class_manager = any(subject.managed_by == staff for subject in item.subjects.all())
                        is_class_manager = item.class_id.managed_by == staff
                        if item.status:
                            show_status_column = any(item.status )
                        
                    
                    try:
                        if subject.managed_by == staff:
                            if students.exists():
                                pass
                            else:
                                
                                messages.error(request, f"No students registered in {student_class}!")
                        else:
                            messages.error(request, f"You don't have access to students registered in {subject}!")
                            return redirect(staff_home)
                            
                    except:
                        messages.error(request, f"Subject did not match the selected class!")
                        return redirect(staff_home)
                        
            
            if staff.stafftype == "Subject Teacher":
                class_id = request.POST.get('class')
                if class_id == "Select Class/Form":
                    messages.error(request, "Please select class!")
                    return redirect(staff_home)
                
                
                
                selected_subject = request.POST.get('subject')
                if selected_subject == "Subject":
                    messages.error(request, "Please select subject!")
                    return redirect(staff_home)
                
                subject = Subject.objects.filter(class_Form__name=class_id, subject_name=selected_subject).first()
                
                student_class = Class_Form.objects.get(name=class_id)
                
                students = Student.objects.filter(class_id__name=student_class, subjects__subject_name=selected_subject, subjects__managed_by=staff).exclude(user__is_active=False)
                
                for item in students:
                    is_subject = is_class_manager = any(subject.managed_by == staff for subject in item.subjects.all())
                    is_class_manager = item.class_id.managed_by == staff
                    
                    
                
                if subject.managed_by == staff:
                    if students.exists():
                        pass
                    else:
                        
                        messages.error(request, f"No students registered in {student_class}!")
                else:
                    messages.error(request, f"You don't have access to students registered in {subject}!")
    except:
        messages.error(request, "An error occured, refresh your page!")    
        return redirect(staff_home)
    data = {
        'staff': staff,
        'students': students,
        'term': term,
        'class_form': class_form,
        'student_class': student_class,
        'staff_sub_class': unique_staff_sub_class,  # Use unique values
        'staff_sub': unique_staff_sub,              # Use unique values
        'subject': subject,
        'is_class_manager': is_class_manager,
        'is_subject': is_subject,
        'show_status_column': show_status_column,
    }

    if students:
        return render(request, "staff/home.html", data)
    else:
        return render(request, 'staff/select_class.html', data)







@login_required(login_url="/")
def see_results(request):
    staff = get_object_or_404(Staff, staff_name__username=request.user.username)
    

    class_form = Class_Form.objects.filter(managed_by=staff)
    students = None
    student_classx = None

    if request.method == 'POST' or request.GET.get('downloads'):
        try:
            if request.method == 'POST':
                class_id = request.POST['class']
            else:
                class_id = request.session.get('class_id')
            
            student_classx = Class_Form.objects.get(id=class_id)
            student_class = Class_Form.objects.get(id=class_id)
            students = Student.objects.filter(class_id=student_class).exclude(user__is_active=False)
            
            results = StudentResult.objects.filter(student__class_id=student_class).exclude(student__user__is_active=False)
            
            
            current_year, previous_year = get_years(request)

            grouped_results = {}
            for result in results:
                student = result.student
                if student not in grouped_results:
                    grouped_results[student] = []
                grouped_results[student].append(result)
            
            if request.GET.get('downloads'):
                try:
                    html_content = render_to_string('staff/report_card.html', {
                        'grouped_results': grouped_results,
                        'term': Term.objects.get(pk=1),
                        'previous_year': request.session.get('previous_year'),
                        'current_year': request.session.get('current_year'),
                        "schoolname":schoolname,
                        "school_slogan":school_slogan,
                        "school_location":school_location,
                        "school_number":school_number,
                        "schoolweb":schoolweb,
                    })

                    pdfkit_options = {
                        'enable-local-file-access': '', 
                        'no-outline': None,
                        'encoding': "UTF-8",
                        'quiet': ''
                    }
                    
                    path_wkhtmltopdf = settings.WKHTMLTOPDF_PATH
                    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

                    pdf = pdfkit.from_string(html_content, False, options=pdfkit_options, configuration=config)

                    response = HttpResponse(pdf, content_type='application/pdf')
                    filename = f"{student_class.name}_Report_Card.pdf"
                    response['Content-Disposition'] = f'attachment; filename="{filename}"'
                    return response
                except Exception:
                    messages.error(request, "Failed to generate PDF. Check network connection!")
                    return redirect('staff:see_results')
            
            request.session['class_id'] = class_id
            current_year, previous_year = get_years(request)
            request.session['previous_year'] = previous_year
            request.session['current_year'] = current_year

            staff = get_object_or_404(Staff, staff_name__username=request.user.username)

            context = {
                'grouped_results': grouped_results,
                'term': Term.objects.get(pk=1),
                "current_year":current_year,
                "previous_year":previous_year,
                "staff":staff,
                "schoolweb":schoolweb,
                "schoolname":schoolname,
                "school_slogan":school_slogan,
                "school_location":school_location,
                "school_number":school_number,
                "student_class":student_classx,
            }
            return render(request, "staff/report_card.html", context)
        except Exception:
            messages.error(request, "Select class to fetch student report cards!")

    data = {
        'staff': staff,
        'students': students,
        'class_form': class_form,
        'student_classx': student_classx,
    }
    return render(request, 'staff/select_class_form.html', data)

        

@login_required(login_url="/")
def send_all_results(request, class_id):
    if request.user.user_type != "STAFF":
        return JsonResponse({"error": "Unauthorized"}, status=403)

    staff = get_object_or_404(Staff, staff_name=request.user)
    students = Student.objects.filter(class_id__managed_by=staff, class_id__name=class_id).exclude(user__is_active=False)

    status_tracker = {}

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(send_report_card, student, request, status_tracker) for student in students]
        
        for future in futures:
            try:
                future.result()
            except Exception as e:
                messages.error(request, f"Error sending report card: {str(e)}")

    return JsonResponse({"status_tracker": status_tracker})





def send_report_card(student, request, status_tracker):
    try:
        if student.user.email:
            single_card(request, student.user.username)
            student.status = "SENT"
            student.save()
            status_tracker[student.user.get_full_name()] = "Sent"
        else:
            single_card(request, student.user.username)
            student.status = "NO EMAIL"
            student.save()
            status_tracker[student.user.get_full_name()] = "Sent" 
    except Exception as e:
        student.status = "FAILED"
        student.save()
        status_tracker[student.user.get_full_name()] = f"Failed: {str(e)}"





def generate_pdf(template_name, context):
    template = get_template(template_name)
    html = template.render(context)

    path_wkhtmltopdf = settings.WKHTMLTOPDF_PATH
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    
    pdfkit_options = {
        'enable-local-file-access': '',
        'no-outline': None,
        'encoding': "UTF-8",
        'quiet': '',
    }
    pdf = pdfkit.from_string(html, False, configuration=config, options=pdfkit_options)  # False returns the PDF as a byte string
    return pdf




@login_required(login_url="/")
def single_card(request, student):
    try:
        staff = get_object_or_404(Staff, staff_name__username=request.user.username)
        term = Term.objects.get(pk=1)
        
        staff_class = staff.class_managed.all()
        
        students = None
        
        for item in staff_class:
            class_id = item.name
        
            try:
                students = Student.objects.get(class_id__name=class_id, class_id__managed_by=staff, user__username=student)
                break
            except Student.DoesNotExist:
                continue
            
        if not students:
            messages.error(request, "Student not found in the classes managed by the staff.")

        
        results = StudentResult.objects.filter(student=students, term=term.term).exclude(student__user__is_active=False)
            
        grouped_results = {students: results}

        context = {
                'grouped_results': grouped_results,
                'term': term,
                'previous_year': get_years(request)[1],  
                'current_year': get_years(request)[0],
                'staff': staff,
                "schoolname":schoolname,
                "school_slogan":school_slogan,
                "school_location":school_location,
                "school_number":school_number,
                "schoolweb":schoolweb,
            }

        pdf_file = generate_pdf('staff/single_repot.html', context)
        

        report_cards_dir = os.path.join(settings.MEDIA_ROOT, 'report_cards')
        os.makedirs(report_cards_dir, exist_ok=True)

        pdf_filename = f"{students.user.get_username()}_Term_{term.term}_Report_Card.pdf"
        pdf_path = os.path.join(report_cards_dir, pdf_filename)

        with open(pdf_path, 'wb') as f:
            f.write(pdf_file)

        pdf_url = default_storage.url(os.path.join('report_cards', pdf_filename))  # Adjust the URL to include the subfolder

        pdf_url = request.build_absolute_uri(pdf_url)

        email = students.user.email
        
        smtp = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
        smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                    
                    
        msg = EmailMessage()
        msg['Subject'] = f"{students.class_id.name} Report Card"
        msg['From'] = EMAIL_HOST_USER
        msg['To'] = email

        if email:
            try:
                
                msg.add_alternative(
                    f"""
                    <html>
                        <body>
                            <p>Dear <strong>{str(students.user.get_full_name()).capitalize()}</strong>,</p>
                            <p>Please find your report card for {students.class_id.name} Term {term.term} of the year {context['current_year']} at the following link:</p>
                            <p><a href="{pdf_url}">View your Report Card</a></p>
                            <p>Best regards,</p>
                            <p><strong>{schoolname}</strong></p>
                        </body>
                    </html>
                    """, subtype='html'
                )
                
                smtp.send_message(msg)
                smtp.quit()
                
            except:
                pass
    except:
        messages.error(request, "Error generating report card for students!")
    return redirect('staff_home')







@login_required(login_url="/")
def add_marks(request, class_id):
    
    staff = get_object_or_404(Staff, staff_name__username = request.user)

    student = get_object_or_404(Student,user__username=class_id)

    current_year, previous_year = get_years(request)

    is_class_manager = student.class_id.managed_by == staff

    # Fetch all subjects for the student's class
    subjects = Subject.objects.filter(class_Form=student.class_id)

    # Only allow editing of the subjects the staff is teaching
    staff_subjects = Subject.objects.filter(class_Form=student.class_id, managed_by=staff)

    try:
        if request.method == 'POST':
            #Conduct & Remarks
            if is_class_manager :
                conduct = request.POST['conduct']
                remarks = request.POST['remarks']
                attendance = request.POST['attendance']
                student.remarks=remarks
                student.conduct = conduct
                student.attendance = attendance
                student.save()
            for subject in subjects:
                # Check if the staff teaches this subject (allow editing)
                if subject in staff_subjects :
                    exercise_score = request.POST.get(f'exercise_{subject.subject_name}')
                    homework_score = request.POST.get(f'homework_{subject.subject_name}')
                    project_work_score = request.POST.get(f'project_{subject.subject_name}')
                    exam_score = request.POST.get(f'exam_{subject.subject_name}')

                    # Convert scores to decimal, handle missing values by defaulting to 0
                    exercise_score = float(exercise_score) if exercise_score else 0
                    homework_score = float(homework_score) if homework_score else 0
                    project_work_score = float(project_work_score) if project_work_score else 0
                    exam_score = float(exam_score) if exam_score else 0
                    if exercise_score >40:
                        messages.error(request, "Exercise marks should not be more than 40!")
                        return redirect(add_marks, student.user.username)
                    elif homework_score >40:
                        messages.error(request, "Home work marks should not be more than 40!")
                        return redirect(add_marks, student.user.username)
                    elif project_work_score >20:
                        messages.error(request, "Project work marks should not be more than 20!")
                        return redirect(add_marks, student.user.username)
                    elif exam_score >100:
                        messages.error(request, "Exams marks should not be more than 100!")
                        return redirect(add_marks, student.user.username)


                    term = Term.objects.first()

                    # Create or update the StudentResult
                    student_result, created = StudentResult.objects.update_or_create(
                        student=student,
                        subject=subject.subject_name,
                        term=term.term,
                        previous_class=student.class_id.name,
                        year=current_year,
                        defaults={
                            'exercise_score': exercise_score,
                            'homework_score': homework_score,
                            'project_work_score': project_work_score,
                            'exam_score': exam_score,
                        }
                    )
                    student_result.save()
                classes, created = StudentClasses.objects.update_or_create(
                    student = student,
                )
                classes.classes.add(student.class_id)
                classes.year=current_year
                classes.save()
            messages.success(request, "Saved successfully!")
            return redirect(add_marks, student.user.username)
    except:
        messages.error(request, "Did not run!")
        return redirect(add_marks, student.user.username)
    terms = Term.objects.first()
    student_results = StudentResult.objects.filter(student=student, term=terms.term, previous_class =student.class_id.name,  year=current_year)
    context={
        'staff': staff,
        'students': student,
        'subjects': subjects,
        'current_year': current_year,
        'previous_year': previous_year,
        'student_results': student_results,
        "student":student,
        "term":terms,
        'is_class_manager': is_class_manager,
        'staff_subjects': staff_subjects,
    }
    return render (request, 'staff/add_marks.html', context)