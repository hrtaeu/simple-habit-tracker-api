from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Sum
from django.utils.timezone import now, timedelta
from django.contrib.auth.models import User
from .serializers import RegisterSerializer
import random

from .models import Habit, HabitTimeLog
from .serializers import HabitSerializer, HabitTimeLogSerializer, ResetStreakSerializer

# Public view (anyone can access)
class PublicView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"message": "This is a public endpoint!"})

# Protected view (only authenticated users)
class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "You must be logged in to see this!"})


# List and Create Habits
class HabitListCreateView(generics.ListCreateAPIView):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]  

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# Retrieve, Update, and Delete Habit
class HabitDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]  

# Daily Habit Reminder View
class DailyReminderView(APIView):
    permission_classes = [IsAuthenticated]  

    def get(self, request):
        habits = Habit.objects.filter(user=request.user, reminder_time__isnull=False)
        reminders = [{
            "habit": habit.name, 
            "reminder_time": habit.reminder_time.strftime("%H:%M"),
            "message": "Don't forget to complete this habit today!"
        } for habit in habits]
        return Response({"daily_reminders": reminders})

# Motivational Quotes
MOTIVATIONAL_QUOTES = [
    "Believe you can, and you're halfway there.",
    "Success is the sum of small efforts repeated daily.",
    "Don't watch the clock; do what it does. Keep going.",
    "The secret of getting ahead is getting started.",
    "Your only limit is your mind.",
    "Little by little, one travels far."
]

class MotivationalQuoteView(APIView):
    permission_classes = [AllowAny]  

    def get(self, request):
        return Response({"motivational_quote": random.choice(MOTIVATIONAL_QUOTES)})

# Set Habit Goal
class SetHabitGoalView(APIView):
    permission_classes = [IsAuthenticated]  

    def post(self, request):
        habit_id = request.data.get("habit_id")
        goal = request.data.get("goal")
        if not habit_id or not goal:
            return Response({"error": "habit_id and goal are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            habit = Habit.objects.get(id=habit_id, user=request.user)
            habit.goal = goal
            habit.save()
            return Response({"message": "Goal set successfully!", "habit": HabitSerializer(habit).data})
        except Habit.DoesNotExist:
            return Response({"error": "Habit not found."}, status=status.HTTP_404_NOT_FOUND)

# Check Habit Completion
class CheckHabitCompletionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        habit_name = request.query_params.get('habit')
        if not habit_name:
            return Response({"error": "Habit name is required"}, status=400)

        today = now().date()
        habit = Habit.objects.filter(name=habit_name, user=request.user, completed=True, completed_at=today).first()

        if habit:
            return Response({"message": f"You completed '{habit.name}' today ✅"})
        return Response({"message": f"You have NOT completed '{habit_name}' today ❌"})

# Habit Streaks
class HabitStreakView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        habits = Habit.objects.filter(user=request.user, completed=True)
        streaks = {habit.name: habit.calculate_streak() for habit in habits}
        return Response({"habit_streaks": streaks})

# Weekly Summary
class WeeklySummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        past_week = now().date() - timedelta(days=7)
        habits = Habit.objects.filter(user=request.user)
        summary = [{
            "habit": habit.name,
            "days_completed": Habit.objects.filter(user=request.user, id=habit.id, completed_at__gte=past_week).count()
        } for habit in habits]
        return Response({"weekly_summary": summary})

# Habit Completion Report
class CompletionReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = now().date()
        start_of_month = today.replace(day=1)
        total_habits = Habit.objects.filter(user=request.user, created_at__date__gte=start_of_month).count()
        completed_habits = Habit.objects.filter(user=request.user, completed=True, completed_at__gte=start_of_month).count()
        completion_percentage = (completed_habits / total_habits) * 100 if total_habits else 0
        return Response({
            "message": f"You've completed {completion_percentage:.2f}% of your habits this month.",
            "total_habits": total_habits,
            "completed_habits": completed_habits,
            "completion_percentage": round(completion_percentage, 2)
        })

# Reset Streak
class ResetStreakView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ResetStreakSerializer(data=request.data)
        if serializer.is_valid():
            habit_id = serializer.validated_data['habit_id']
            try:
                habit = Habit.objects.get(id=habit_id, user=request.user)
                habit.streak = 0
                habit.save()
                return Response({"message": "Habit streak reset successfully!"})
            except Habit.DoesNotExist:
                return Response({"error": "Habit not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SetCustomReminderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        habit_id = request.data.get("habit_id")
        reminder_time = request.data.get("reminder_time")

        if not habit_id or not reminder_time:
            return Response({"error": "habit_id and reminder_time are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            habit = Habit.objects.get(id=habit_id, user=request.user)
            habit.reminder_time = reminder_time
            habit.save()
            return Response({"message": "Reminder set successfully!", "habit": HabitSerializer(habit).data})
        except Habit.DoesNotExist:
            return Response({"error": "Habit not found."}, status=status.HTTP_404_NOT_FOUND)

# Habit Milestone Reward View
class HabitMilestoneRewardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        habits = Habit.objects.filter(user=request.user)
        rewards = []

        for habit in habits:
            if habit.streak and habit.streak % 10 == 0:  # Reward for every 10-day streak
                rewards.append({
                    "habit": habit.name,
                    "message": f"Congratulations! You've reached a {habit.streak}-day streak 🎉"
                })

        return Response({"milestone_rewards": rewards})

# Habit Reinforcement View
class HabitReinforcementView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        habit_id = request.data.get("habit_id")
        reinforcement_message = request.data.get("reinforcement_message")

        if not habit_id or not reinforcement_message:
            return Response({"error": "habit_id and reinforcement_message are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            habit = Habit.objects.get(id=habit_id, user=request.user)
            habit.reinforcement_message = reinforcement_message
            habit.save()
            return Response({"message": "Reinforcement message updated successfully!", "habit": HabitSerializer(habit).data})
        except Habit.DoesNotExist:
            return Response({"error": "Habit not found."}, status=status.HTTP_404_NOT_FOUND)

# Habit Time Spent View
class HabitTimeSpentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        habits = Habit.objects.filter(user=request.user)
        time_spent = []

        for habit in habits:
            total_time = HabitTimeLog.objects.filter(habit=habit).aggregate(Sum('time_spent'))['time_spent__sum'] or 0
            time_spent.append({
                "habit": habit.name,
                "total_time_spent": total_time,
                "message": f"You've spent {total_time} minutes on '{habit.name}' so far."
            })

        return Response({"habit_time_spent": time_spent})

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)
