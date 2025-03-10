from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny  
from .models import Habit
from .serializers import HabitSerializer

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
