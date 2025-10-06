from django.urls import path
from . import views
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('', views.landing, name='landing'),
    path('students/', views.PublicStudentListView.as_view(), name='student_list'),
    path('leaderboard/', views.LeaderboardView.as_view(), name='leaderboard'),
    path('profile/<int:pk>/', views.StudentDetailView.as_view(), name='student_detail'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),

    path('endorse/<int:skill_id>/', views.endorse_skill, name='endorse_skill'),

    # Admin actions
    path('admin/delete_student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('admin/endorse_any/<int:skill_id>/', views.endorse_any_student, name='endorse_any_student'),

    # Auth
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='pages/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='landing'), name='logout'),
]
