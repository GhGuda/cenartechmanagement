from . import views
from django.urls import path



urlpatterns = [
    path('enartech_admin_home', views.enartech_admin_home, name="enartech_admin_home"),
    path('add_hod', views.add_hod, name="add_hod"),
    path('deactivate_users_in_school/<int:school>', views.deactivate_users_in_school, name="deactivate_users_in_school"),
    path('reactivate_users_in_school/<int:school>', views.reactivate_users_in_school, name="reactivate_users_in_school"),
    path('delete_users_in_school/<int:school>', views.delete_users_in_school, name="delete_users_in_school"),
]