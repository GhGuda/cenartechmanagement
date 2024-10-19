from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
# Register your models here.

# class UserModel(UserAdmin):
#     list_display = ['username', "user_type", "profile_pic"]

admin.site.register(CustomUser)
admin.site.register(StudentClasses)
admin.site.register(Class_Form)
admin.site.register(Student)
admin.site.register(Staff)
admin.site.register(Term)
admin.site.register(Subject)
admin.site.register(StudentResult)
admin.site.register(PassedStudents)
admin.site.register(YearlyPassedStudents)
admin.site.register(AdmittedStudents)
admin.site.register(YearlyAdmittedStudents)
admin.site.register(School)