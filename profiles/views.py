from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db.models import Count, F
from django.db.models.functions import Coalesce
from django.http import JsonResponse, Http404
from django.views.generic import TemplateView, ListView, DetailView
from .models import Student, Skill, Project, Award, PortfolioItem, Endorsement
from .forms import StudentForm, SkillForm, ProjectForm, AwardForm, PortfolioItemForm
from django.contrib.auth.forms import UserCreationForm
from .decorators import admin_required

# ------------------- Landing & Home -------------------
def landing(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.is_staff:
        return redirect('adminpanel:dashboard')
    return redirect('profile_edit')


class HomeView(TemplateView):
    template_name = 'pages/home.html'


# ------------------- Public Profiles -------------------
class PublicStudentListView(ListView):
    model = Student
    template_name = 'pages/student_list.html'
    context_object_name = 'students'

    def get_queryset(self):
        return Student.objects.filter(is_public=True).annotate(
            num_skills=Count('skills'),
            num_projects=Count('projects'),
            num_awards=Count('awards'),
            total_endorsements=Coalesce(Count('skills__endorsements'), 0)
        )


class StudentDetailView(DetailView):
    model = Student
    template_name = 'pages/student_detail.html'
    context_object_name = 'student_obj'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        if not obj.is_public and (not user.is_authenticated or getattr(user, 'student_profile', None) != obj):
            raise Http404("This profile is private.")
        return obj


# ------------------- Leaderboard -------------------
class LeaderboardView(ListView):
    model = Student
    template_name = 'pages/leader_board.html'
    context_object_name = 'students'

    def get_queryset(self):
        by = self.request.GET.get('by', 'overall')
        qs = Student.objects.filter(is_public=True).annotate(
            num_skills=Count('skills', distinct=True),
            num_projects=Count('projects', distinct=True),
            num_awards=Count('awards', distinct=True),
            total_endorsements=Coalesce(Count('skills__endorsements', distinct=True), 0),
        )

        if by == 'projects':
            return qs.order_by('-num_projects', '-num_skills', '-num_awards')
        elif by == 'skills':
            return qs.order_by('-num_skills', '-num_projects', '-num_awards')
        elif by == 'awards':
            return qs.order_by('-num_awards', '-num_projects', '-num_skills')
        elif by == 'endorsements':
            return qs.order_by('-total_endorsements', '-num_projects')
        else:
            qs = qs.annotate(
                overall_score=F('num_projects')*3 + F('num_skills')*2 + F('num_awards') + F('total_endorsements')
            )
            return qs.order_by('-overall_score', '-num_projects')


# ------------------- Profile Edit -------------------
@login_required
def profile_edit(request):
    student, _ = Student.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        sform = StudentForm(request.POST, instance=student)
        skform = SkillForm(request.POST, prefix='skill')
        prform = ProjectForm(request.POST, prefix='project')
        awform = AwardForm(request.POST, prefix='award')
        pform = PortfolioItemForm(request.POST, request.FILES, prefix='portfolio')

        if sform.is_valid():
            sform.save()
            messages.success(request, 'Profile updated.')

        if skform.is_valid() and skform.cleaned_data.get('name'):
            Skill.objects.get_or_create(student=student, name=skform.cleaned_data['name'])
            messages.success(request, 'Skill added.')

        if prform.is_valid() and prform.cleaned_data.get('title'):
            Project.objects.create(student=student, **prform.cleaned_data)
            messages.success(request, 'Project added.')

        if awform.is_valid() and awform.cleaned_data.get('title'):
            Award.objects.create(student=student, **awform.cleaned_data)
            messages.success(request, 'Award added.')

        if pform.is_valid() and pform.cleaned_data.get('title'):
            PortfolioItem.objects.create(student=student, **pform.cleaned_data)
            messages.success(request, 'Portfolio item added.')

        return redirect('profile_edit')
    else:
        sform = StudentForm(instance=student)
        skform = SkillForm(prefix='skill')
        prform = ProjectForm(prefix='project')
        awform = AwardForm(prefix='award')
        pform = PortfolioItemForm(prefix='portfolio')

    context = {
        'student': student,
        'sform': sform, 'skform': skform,
        'prform': prform, 'awform': awform,
        'pform': pform
    }
    return render(request, 'pages/profile_edit.html', context)


# ------------------- Endorse Skills -------------------
@login_required
def endorse_skill(request, skill_id):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'POST required'}, status=405)

    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key

    skill = get_object_or_404(Skill, id=skill_id)

    # Private profile restriction
    if not skill.student.is_public:
        if not (request.user.is_authenticated and (getattr(request.user, 'student_profile', None) == skill.student or request.user.is_staff)):
            return JsonResponse({'ok': False, 'error': 'Profile is private.'}, status=403)

    try:
        Endorsement.objects.create(
            skill=skill,
            session_key=session_key,
            endorser=request.user if request.user.is_authenticated else None
        )
        Skill.objects.filter(pk=skill.pk).update(endorsement_count=F('endorsement_count') + 1)
        skill.refresh_from_db()
        return JsonResponse({'ok': True, 'count': skill.endorsement_count})
    except Exception:
        return JsonResponse({'ok': False, 'error': 'Already endorsed from this browser.'}, status=400)


# ------------------- Admin Actions for Profiles -------------------
@login_required
@admin_required
def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.user.delete()
    messages.success(request, f'{student.user.username} deleted successfully.')
    return redirect('student_list')


@login_required
@admin_required
def endorse_any_student(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id)
    skill.endorsement_count += 1
    skill.save()
    messages.success(request, f'{skill.name} endorsed successfully.')
    return redirect('student_detail', pk=skill.student.id)


# ------------------- Signup -------------------
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile_edit')
    else:
        form = UserCreationForm()
    return render(request, 'pages/signup.html', {'form': form})
