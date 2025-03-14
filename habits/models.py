from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now, timedelta

class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # User is optional
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    reminder_time = models.TimeField(blank=True, null=True)  # Time for daily reminders
    completed = models.BooleanField(default=False)
    completed_at = models.DateField(blank=True, null=True)  # Last completed date
    created_at = models.DateTimeField(auto_now_add=True)
    goal = models.CharField(max_length=255, blank=True, null=True)  # Habit goal
    progress = models.IntegerField(default=0)  # Progress tracking
    streak = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def calculate_streak(self):
        """
        Calculate the streak of consecutive days this habit was completed.
        """
        habit_entries = Habit.objects.filter(user=self.user, name=self.name, completed=True).order_by('-completed_at')
        if not habit_entries:
            return 0  # No completed habits

        streak = 1  # Start at 1 (counting today)
        previous_date = habit_entries[0].completed_at  # Most recent completion date

        for habit in habit_entries[1:]:
            if (previous_date - habit.completed_at).days == 1:
                streak += 1
                previous_date = habit.completed_at
            else:
                break  # Streak is broken

        return streak
    
class HabitTimeLog(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(default=now)
    time_spent = models.PositiveIntegerField(help_text="Time spent in minutes")

    def __str__(self):
        return f"{self.habit.name} - {self.time_spent} min on {self.date}"
