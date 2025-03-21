from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now

class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # User is optional
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateField(blank=True, null=True)  # Last completed date
    created_at = models.DateTimeField(auto_now_add=True)
    goal = models.CharField(max_length=255, blank=True, null=True)  # Habit goal
    progress = models.IntegerField(default=0)  # Progress tracking
    streak = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        """ Automatically update completed_at and streak when completed is set to True. """
        if self.completed:
            if not self.completed_at:  # Set completed_at only if it's not already set
                self.completed_at = now().date()
            self.streak = self.calculate_streak()  # Recalculate streak when habit is completed
        else:
            self.completed_at = None  # Reset completed_at if marked incomplete
            self.streak = 0  # Reset streak
        
        super().save(*args, **kwargs)

    def calculate_streak(self):
        """
        Calculate the streak of consecutive days this habit was completed.
        """
        habit_entries = Habit.objects.filter(
            user=self.user, name=self.name, completed=True
        ).order_by("-completed_at")

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

    def __str__(self):
        return f"{self.name} - {'Completed' if self.completed else 'Pending'}"

class HabitTimeLog(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(default=now)
    time_spent = models.PositiveIntegerField(help_text="Time spent in minutes")

    def __str__(self):
        return f"{self.habit.name} - {self.time_spent} min on {self.date}"
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username