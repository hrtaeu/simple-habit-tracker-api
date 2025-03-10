from django.contrib.auth.models import User
from django.db import models

class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # User is optional
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    reminder_time = models.TimeField(blank=True, null=True)  # Time for daily reminders
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
