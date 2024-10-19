from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Staff
from .models import Student
from .models import Class_Form
from .models import StudentResult
from .models import StudentClasses
from .models import Term
from .models import CustomUser
from .models import School
from django.template.loader import render_to_string
from django.contrib import messages
from .staff_view import get_years
import pdfkit
from django.conf import settings


School_marks = settings.SCHOOL_MARKS

schoolweb = settings.SCHOOL_WEB

schoolname=settings.SCHOOL_NAME
school_slogan=settings.SCHOOL_SLOGAN
school_location=settings.SCHOOL_LOCATION
school_number=settings.SCHOOL_NUM




@login_required(login_url='/')
def display_student_results(request):
    user = CustomUser.objects.get(username=request.user)
    school = School.objects.get(name=user.school.name)
    student = get_object_or_404(Student, user=request.user, user__school=school)
    student_year = None
    try:
        classes = StudentClasses.objects.get(student=student, school=school)
        class_list = classes.classes.all()
        studentResult = StudentResult.objects.filter(student=student)
        
    except:
        messages.error(request, "No marks yet")
        classes = None
        class_list = None
        student_year = None
        studentResult = []

    for item in studentResult:
            student_year = item.year
    try:       
        if request.method == 'POST' or request.GET.get('downloads'):
            
            if request.method == 'POST':
                class_id = request.POST['class']
                term = request.POST['term']
                year = request.POST['year']
                request.session['class_id'] = class_id
                request.session['term'] = term
                request.session['year'] = year
            else:
                class_id = request.session.get('class_id')
                term = request.session.get('term')
                year = request.session.get('year')
                
            
                
                
            # Fetch the class and student results
            results = StudentResult.objects.filter(student=student, previous_class=class_id, year=year, term=term)
            if results.exists():
                pass
            else:
                messages.error(request, "No results found!")
                return redirect('display_student_results')
            
            grouped_results = {student: results}

            if request.GET.get('downloads'):
                try:
                    html_content = render_to_string('student/my_result.html', {
                        'grouped_results': grouped_results,
                        'term': term,
                        'year': year,
                        'student': student,
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
                        'quiet': '',
                    }
                    
                    path_wkhtmltopdf = settings.WKHTMLTOPDF_PATH
                    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

                    pdf = pdfkit.from_string(html_content, False, options=pdfkit_options, configuration=config)

                    response = HttpResponse(pdf, content_type='application/pdf')
                    filename = f"{student.user.first_name.capitalize()}_{student.user.last_name.capitalize()}_{class_id}_Report_Card.pdf"
                    response['Content-Disposition'] = f'attachment; filename="{filename}"'
                    return response
                except Exception as e:
                    messages.error(request, f"Failed to generate PDF. Error: {str(e)}")
                    return redirect('display_student_results')

            # Save class_id in the session and update session years
            request.session['class_id'] = class_id

            
            context = {
                'grouped_results': grouped_results,
                'term': term,
                'year': year,
                'student': student,
                'student_year': student_year,
                'schoolweb': schoolweb,
                "schoolname":schoolname,
                "school_slogan":school_slogan,
                "school_location":school_location,
                "school_number":school_number,
            }
            return render(request, "student/my_result.html", context)
    except Exception as e:
        messages.error(request, f"Please select a class to fetch student results! Error: {str(e)}")
        

    data = {
        'students': student,
        'class_form': class_list,
        'student_year': student_year,
    }
    return render(request, 'student/select_class_form.html', data)







@login_required(login_url='/')
def student_home(request):
    user = CustomUser.objects.get(username=request.user)
    school = School.objects.get(name=user.school.name)
    term = Term.objects.get(school=school)
    student = get_object_or_404(Student, user=request.user, user__school=school)
    current_year, previous_year = get_years(request)
    
    
    
    total = (student.total_marks_term_one or 0) + (student.total_marks_term_two or 0) + (student.total_marks_term_three or 0)

    

    results = None
    staff = None

    try:
        if student.class_id.name != "Completed Class":
            class_instance = get_object_or_404(Class_Form,name=student.class_id.name)
            staff_class = class_instance.managed_by.staff_name
            staff = get_object_or_404(Staff,staff_name=staff_class)
            results = StudentResult.objects.filter(student=student, previous_class=class_instance, term=term.term,  year=current_year)
        else:
            class_instance = Class_Form.objects.get(name=student.class_id.name)
            staff = "None"
    except:
        pass

    context = {
        'student': student,
        'staff': staff,
        'results': results,
        'term': term,
        'total': total,
        'School_marks': School_marks,
    }

    return render(request, 'student/home.html', context)


