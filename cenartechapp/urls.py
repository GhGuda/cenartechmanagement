from django.urls import path
from . import views, hod_views, staff_view, student_view

urlpatterns = [
    path('', views.Login, name="login"),
    path('doLogout', views.doLogout, name="logout"),
    path('doLogin', views.doLogin, name="doLogin"),
    
    
    
    
    path('profile/update', views.profile, name="profile"),
    
    
    
    
    
    # HODVIEWS 
    path('HOD/home', hod_views.home, name="hod_home"),
    
    path('HOD/add/student', hod_views.add_student, name="add_student"),
    path('HOD/view/student', hod_views.view_student, name="view_student"),
    path('HOD/view/old/students', hod_views.old_student, name="old_student"),
    path('HOD/edit/student/<user_name>', hod_views.edit_student, name="edit_student"),
    path('HOD/delete/student/<user_name>', hod_views.delete_student, name="delete_student"),
    path('HOD/delete/old/student/<user_name>', hod_views.delete_old_student, name="delete_old_student"),
    path('HOD/student/details/<user_name>', hod_views.student_details, name="student_details"),
    
    
    # path('HOD/add/course', hod_views.add_course, name="add_course"),
    
    path('HOD/add/staff', hod_views.add_staff, name="add_staff"),
    path('HOD/view/staffs', hod_views.view_staffs, name="view_staffs"),
    path('HOD/assign/staff/to_class', hod_views.assign_staffs, name="assign_staffs"),
    path('HOD/edit/staff/<staff>', hod_views.edit_staff, name="edit_staff"),
    path('HOD/delete/staff/<staff>', hod_views.delete_staff, name="delete_staff"),
    path('HOD/view/staff/details/<staffname>', hod_views.view_staff_details, name="view_staff_details"),
    
    
    path('HOD/add/term', hod_views.add_term, name="add_term"),
    path('HOD/run/search', hod_views.search, name="search"),
    path('HOD/activate/<user_name>/activate_user', hod_views.activate_user, name="activate_user"),
    
    
    
    
    path('Staff/home', staff_view.staff_home, name="staff_home"),
    path('Staff/add_marks/<class_id>', staff_view.add_marks, name="add_marks"),

    path("Staff/see_results", staff_view.see_results, name="see_results"),
    # path("Staff/single_card/<student>", staff_view.single_card, name="single_card"),
    path("Staff/send_all_results/<class_id>", staff_view.send_all_results, name="send_all_results"),

    
    
    path('student/student_home', student_view.student_home, name="student_home"),
    path('student/display_student_results', student_view.display_student_results, name="display_student_results"),
    path('student/display_student_results', student_view.display_student_results, name="display_student_results"),
    
    
    
]
