from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import AdminSignUpForm
from profiles.models import Student  # import Student model from profiles

def is_staff_user(user):
    return user.is_authenticated and user.is_staff

def admin_signup(request):
    """Allow creation of admin accounts (is_staff=True)"""
    if request.method == 'POST':
        form = AdminSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # log in immediately
            messages.success(request, 'Admin account created and logged in.')
            return redirect('adminpanel:dashboard')
    else:
        form = AdminSignUpForm()
    return render(request, 'adminpanel/admin_signup.html', {'form': form})

@user_passes_test(is_staff_user, login_url='adminpanel:admin_login')
def dashboard(request):
    """Simple admin dashboard landing"""
    total_students = Student.objects.count()
    total_public = Student.objects.filter(is_public=True).count()
    context = {
        'total_students': total_students,
        'total_public': total_public
    }
    return render(request, 'adminpanel/dashboard.html', context)

@user_passes_test(is_staff_user, login_url='adminpanel:admin_login')
def student_list(request):
    students = Student.objects.select_related('user').all().order_by('user__username')
    return render(request, 'adminpanel/student_list.html', {'students': students})

@user_passes_test(is_staff_user, login_url='adminpanel:admin_login')
def student_detail(request, pk):
    student = get_object_or_404(Student.objects.select_related('user').prefetch_related('skills', 'projects', 'awards', 'portfolio'), pk=pk)
    return render(request, 'adminpanel/student_detail.html', {'student': student})
