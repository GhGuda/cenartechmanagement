from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from cenartechapp.models import *
from django.http import JsonResponse
# Create your views here.


@login_required(login_url='/')
def enartech_admin_home(request):
    user = CustomUser.objects.get(username=request.user.username)
    schools = School.objects.all()
    schools_total = School.objects.all().count()
    
    school_user_counts = []  # List to store school and user count

    for school in schools:
        # Count users related to the school
        school_users = CustomUser.objects.filter(school=school)
        school_size = school_users.count()
        # Add the school and the user count to the list
        school_user_counts.append({
            'activeness': school.deactivate,
            'id': school.pk,
            'logo': school.logo,
            'name': school.name,
            'number': school.number,
            'address': school.address,
            'user_count': school_size,
            'school_users': school_users,
        })
    schoolusers = CustomUser.objects.all().exclude(user_type="ADMIN").count()
    active_users = CustomUser.objects.filter(is_active=True).count()
    inactive_users = CustomUser.objects.filter(is_active=False).count()
    
    
    
    context={
            'schools_total':schools_total,
            'school':schools,
            'schoolusers':schoolusers,
            'user':user,
            'active_users':active_users,
            'inactive_users':inactive_users,
            'school_user_counts': school_user_counts,
        }
    return render(request, 'admin/home.html', context)


@login_required(login_url='/')
def add_hod(request):
    try:
        if request.method == 'POST':
            username = request.POST['username']
            email = request.POST['email']
            school_name = request.POST['school_name']
            password = request.POST['password']
            
            if len(password) <= 7:
                    messages.error(request, "Password must be more than 7 letters long!")
                    return render(request, 'admin/add_school.html', {
                        "entered_data": request.POST,
                    })
                
            if email=="" and CustomUser.objects.filter(email=""):
                    pass
            else:
                if CustomUser.objects.filter(email__iexact=email).exists():
                    messages.error(request, "Email already exists!")
                    return render(request, 'admin/add_school.html', {
                        "entered_data": request.POST,
                    })
            if CustomUser.objects.filter(username__iexact=username).exists():
                    messages.error(request, "Username already exists!")
                    return render(request, 'admin/add_school.html', {
                        "entered_data": request.POST,
                    })
            
            sch = School.objects.create(
                name=school_name,
            )
                
            CustomUser.objects.create_user(
                username=username,
                email=email,
                school=sch,
                password=password,
                user_type = "HOD"
            )
            
            
            sch.save()
            
            term = Term.objects.create(
                term="One",
                school=sch
            )
            term.save()
            
            messages.success(request, "HOD created successfully!")
            return redirect("add_hod")
    except:
        messages.error(request, "Error in creating HOD!")
        return render(request, 'admin/add_school.html', {
                        "entered_data": request.POST,
                    })
    return render(request, 'admin/add_school.html')




@login_required(login_url='/')
def deactivate_users_in_school(request, school):
    try:
        school = School.objects.get(pk=school)
        users = CustomUser.objects.filter(school=school)
        
        for user in users:
            user.is_active = False
            user.save()

        school.deactivate = True
        school.save()
        return JsonResponse({'message': "Successfully deactivated school!"})
    except Exception as e:
        return JsonResponse({'message': f"Error in deactivating school: {str(e)}"}, status=400)

@login_required(login_url='/')
def reactivate_users_in_school(request, school):
    try:
        school = School.objects.get(pk=school)
        users = CustomUser.objects.filter(school=school)
        
        for user in users:
            user.is_active = True
            user.save()

        school.deactivate = False
        school.save()
        return JsonResponse({'message': "Successfully reactivated school!"})
    except Exception as e:
        return JsonResponse({'message': f"Failed to reactivate school: {str(e)}"}, status=400)

@login_required(login_url='/')
def delete_users_in_school(request, school):
    try:
        school = School.objects.get(pk=school)
        users = CustomUser.objects.filter(school=school)
        
        for user in users:
            user.delete()

        school.delete()
        return JsonResponse({'message': "Successfully deleted school and its users!"})
    except Exception as e:
        return JsonResponse({'message': f"Failed to delete school and its users: {str(e)}"}, status=400)