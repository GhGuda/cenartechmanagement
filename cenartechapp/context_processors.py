from datetime import datetime

def current_year(request):
    return {'current_year': datetime.now().year}




from .models import CustomUser, School

def school_info(request):
    if request.user.is_authenticated:
        try:
            user = CustomUser.objects.get(username=request.user.username)
            school = School.objects.get(id=user.school.id)
        except (CustomUser.DoesNotExist, School.DoesNotExist, AttributeError):
            school = None
    else:
        school = None
    return {"school": school}