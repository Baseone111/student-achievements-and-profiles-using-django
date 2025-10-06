from django import forms
from .models import Student, Skill, Project, Award, PortfolioItem

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['bio', 'is_public']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us about yourself...'}),
        }

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name']

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description']

class AwardForm(forms.ModelForm):
    class Meta:
        model = Award
        fields = ['title', 'description']

class PortfolioItemForm(forms.ModelForm):
    class Meta:
        model = PortfolioItem
        fields = ['title', 'file', 'url', 'screenshot']
