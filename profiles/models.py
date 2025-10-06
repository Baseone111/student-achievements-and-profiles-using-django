from django.db import models

from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint

User = settings.AUTH_USER_MODEL

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    bio = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)  # Public/Private toggle

    def __str__(self):
        return self.user.get_username()

class Skill(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)
    endorsement_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('student', 'name')

    def __str__(self):
        return f'{self.name} ({self.student})'

class Project(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    def __str__(self):
        return f'{self.title} - {self.student}'

class Award(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='awards')
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    def __str__(self):
        return f'{self.title} - {self.student}'

class PortfolioItem(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='portfolio')
    title = models.CharField(max_length=150)
    file = models.FileField(upload_to='portfolio/', blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    screenshot = models.ImageField(upload_to='portfolio/screens/', blank=True, null=True)

    def __str__(self):
        return f'{self.title} - {self.student}'

class Endorsement(models.Model):
    """
    Links a browser session (or optionally a user) to a Skill.
    Ensures one endorsement per skill per session_key.
    """
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='endorsements')
    session_key = models.CharField(max_length=40)  # browser-session based dedupe
    endorser = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['skill', 'session_key'], name='unique_endorse_per_session')
        ]

    def __str__(self):
        who = self.endorser or self.session_key
        return f'{who} -> {self.skill}'

# Create your models here.
