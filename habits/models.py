from django.db import models

class Habit(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.name
