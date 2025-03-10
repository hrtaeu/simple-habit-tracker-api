from django.contrib.auth.models import User
from django.db import models

class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # User is optional
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    reminder_time = models.TimeField(blank=True, null=True)  # Time for daily reminders
    completed = models.BooleanField(default=False)
    completed_at = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    goal = models.CharField(max_length=255, blank=True, null=True)
    progress = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name
