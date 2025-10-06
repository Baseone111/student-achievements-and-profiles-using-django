from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'adminpanel'

urlpatterns = [
    # Admin auth
    path('signup/', views.admin_signup, name='admin_signup'),
    path('login/', auth_views.LoginView.as_view(template_name='adminpanel/admin_login.html'), name='admin_login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='admin_logout'),

    # Admin dashboard
    path('', views.dashboard, name='dashboard'),  # /adminpanel/
    path('students/', views.student_list, name='student_list'),
    path('student/<int:pk>/', views.student_detail, name='student_detail'),
]
