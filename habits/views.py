from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny  
from .models import Habit
from rest_framework import status
from .serializers import HabitSerializer
from django.utils.timezone import now
import random

# List and Create Habits
class HabitListCreateView(generics.ListCreateAPIView):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [AllowAny]  

    def perform_create(self, serializer):
        serializer.save(user=None)  # Save without user

# Retrieve, Update, and Delete Habit
class HabitDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [AllowAny]  

# Daily Habit Reminder View
class DailyReminderView(APIView):
    permission_classes = [AllowAny]  

    def get(self, request):
        habits = Habit.objects.filter(reminder_time__isnull=False)  # Get only habits with reminders
        reminders = [
            {
                "habit": habit.name, 
                "reminder_time": habit.reminder_time.strftime("%H:%M") if habit.reminder_time else None,
                "message": "Don't forget to complete this habit today!"
            }
            for habit in habits
        ]
        return Response({"daily_reminders": reminders})

MOTIVATIONAL_QUOTES = [
    "Believe you can, and you're halfway there.",
    "Success is the sum of small efforts repeated daily.",
    "Don't watch the clock; do what it does. Keep going.",
    "The secret of getting ahead is getting started.",
    "Your only limit is your mind.",
    "Little by little, one travels far."
]

# Motivational Quote View
class MotivationalQuoteView(APIView):
    permission_classes = [AllowAny]  

    def get(self, request):
        random_quote = random.choice(MOTIVATIONAL_QUOTES)  # Pick a random quote
        return Response({"motivational_quote": random_quote})

class SetHabitGoalView(APIView):
    permission_classes = [AllowAny]  

    def post(self, request):
        habit_id = request.data.get("habit_id")
        goal = request.data.get("goal")
        
        if not habit_id or not goal:
            return Response({"error": "Both habit_id and goal are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            habit = Habit.objects.get(id=habit_id)
            habit.goal = goal
            habit.save()
            return Response({"message": "Goal set successfully!", "habit": HabitSerializer(habit).data})
        except Habit.DoesNotExist:
            return Response({"error": "Habit not found."}, status=status.HTTP_404_NOT_FOUND)

class CheckHabitCompletionView(APIView):
    permission_classes = [AllowAny]  # No authentication required

    def get(self, request):
        habit_name = request.query_params.get('habit')  # Get habit name from request
        if not habit_name:
            return Response({"error": "Habit name is required"}, status=400)

        today = now().date()  
        habit = Habit.objects.filter(name=habit_name, completed=True, completed_at=today).first()

        if habit:
            return Response({"message": f"You completed the '{habit.name}' habit today ✅"})
        else:
            return Response({"message": f"You have NOT completed the '{habit_name}' habit today ❌"})