
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('students/', views.PublicStudentListView.as_view(), name='student_list'),
    path('leaderboard/', views.LeaderboardView.as_view(), name='leaderboard'),
    path('profile/<int:pk>/', views.StudentDetailView.as_view(), name='student_detail'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('endorse/<int:skill_id>/', views.endorse_skill, name='endorse_skill'),

     path('login/', auth_views.LoginView.as_view(template_name='pages/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    
]