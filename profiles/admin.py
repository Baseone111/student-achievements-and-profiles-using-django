from django.contrib import admin

from .models import Student, Skill, Project, Award, PortfolioItem, Endorsement

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_public')

admin.site.register(Skill)
admin.site.register(Project)
admin.site.register(Award)
admin.site.register(PortfolioItem)
admin.site.register(Endorsement)