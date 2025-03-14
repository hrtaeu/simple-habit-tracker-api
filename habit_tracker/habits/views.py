from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny  
from django.db.models import Sum
from .models import HabitTimeLog
from .models import Habit
from rest_framework import status
from .serializers import HabitSerializer
from .serializers import HabitTimeLogSerializer
from django.utils.timezone import now, timedelta
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

class HabitStreakView(APIView):
    def get(self, request):
        """
        Get streaks for all habits.
        """
        habits = Habit.objects.filter(completed=True)  # Get only completed habits
        streaks = {
            habit.name: habit.calculate_streak() for habit in habits
        }
        return Response({"habit_streaks": streaks})
    
class WeeklySummaryView(APIView):
    def get(self, request):
        past_week = now().date() - timedelta(days=7)  # Get the date 7 days ago
        habits = Habit.objects.all()

        summary = []
        for habit in habits:
            completed_days = Habit.objects.filter(
                id=habit.id,
                completed_at__gte=past_week  # Filter habits completed in the last 7 days
            ).count()
            
            summary.append({
                "habit": habit.name,
                "days_completed": completed_days
            })

        return Response({"weekly_summary": summary})
    
class CompletionReportView(APIView):
    def get(self, request):
        today = now().date()
        start_of_month = today.replace(day=1)  # First day of the current month

        total_habits = Habit.objects.filter(created_at__date__gte=start_of_month).count()
        completed_habits = Habit.objects.filter(completed=True, completed_at__gte=start_of_month).count()

        if total_habits == 0:
            completion_percentage = 0
        else:
            completion_percentage = (completed_habits / total_habits) * 100

        return Response({
            "message": f"You've completed {completion_percentage:.2f}% of your habits this month.",
            "total_habits": total_habits,
            "completed_habits": completed_habits,
            "completion_percentage": round(completion_percentage, 2)
        })
        
class SetCustomReminderView(APIView):
    def post(self, request):
        habit_id = request.data.get('habit_id')
        reminder_time = request.data.get('reminder_time')

        if not habit_id or not reminder_time:
            return Response({"error": "habit_id and reminder_time are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            habit = Habit.objects.get(id=habit_id)
            habit.reminder_time = reminder_time
            habit.save()
            return Response({"message": "Reminder set successfully", "habit": HabitSerializer(habit).data}, status=status.HTTP_200_OK)
        except Habit.DoesNotExist:
            return Response({"error": "Habit not found"}, status=status.HTTP_404_NOT_FOUND) 

def get_milestone_reward(streak):
    if streak == 7:
        return "🥉 Bronze Badge - 7-Day Streak!"
    elif streak == 30:
        return "🥈 Silver Badge - 30-Day Streak!"
    elif streak == 100:
        return "🥇 Gold Badge - 100-Day Streak!"
    elif streak == 365:
        return "🏆 Platinum Badge - 1 Year Streak!"
    return None

class HabitMilestoneRewardView(APIView):
    def get(self, request):
        habits = Habit.objects.filter(streak__gte=7)  # Get all habits with streaks

        rewards = []
        for habit in habits:
            reward = get_milestone_reward(habit.streak)
            if reward:
                rewards.append({
                    "habit": habit.name,
                    "streak": habit.streak,
                    "reward": reward
                })

        if not rewards:
            return Response({"message": "No milestones reached yet. Keep going!"}, status=200)

        return Response({"milestone_rewards": rewards}, status=200)

class HabitReinforcementView(APIView):
    def get(self, request):
        completed_habits = Habit.objects.filter(completed=True)  # Get completed habits

        reinforcement_messages = []
        for habit in completed_habits:
            message = self.get_encouraging_message(habit)
            reinforcement_messages.append({
                "habit": habit.name,
                "message": message
            })

        if not reinforcement_messages:
            return Response({"message": "No habits completed yet. Keep going!"}, status=200)

        return Response({"positive_reinforcement": reinforcement_messages}, status=200)

    def get_encouraging_message(self, habit):
        if habit.streak >= 30:
            return f"🌟 Amazing! You've kept {habit.name} for {habit.streak} days!"
        elif habit.streak >= 14:
            return f"💪 Keep going! 14 days straight of {habit.name}!"
        elif habit.streak >= 7:
            return f"🔥 One week done! {habit.name} is now a strong habit!"
        else:
            return f"✅ Great job on completing {habit.name} today! Stay consistent!"

class HabitTimeSpentView(APIView):
    permission_classes = [AllowAny]  # No authentication required

    def get(self, request):
        habit_id = request.query_params.get('habit_id')
        start_date = request.query_params.get('start_date', now().replace(day=1))  # Default: start of the month
        end_date = request.query_params.get('end_date', now().date())  # Default: today

        if habit_id:
            time_logs = HabitTimeLog.objects.filter(habit_id=habit_id, date__range=[start_date, end_date])
            total_time = time_logs.aggregate(Sum('time_spent'))['time_spent__sum'] or 0
            habit_name = Habit.objects.get(id=habit_id).name
            return Response({
                "habit": habit_name,
                "total_time_spent": f"{total_time} minutes",
                "time_period": f"{start_date} to {end_date}"
            })
        else:
            return Response({"error": "Please provide a habit_id"}, status=400)

    def post(self, request):
        serializer = HabitTimeLogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetStreakView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetStreakSerializer(data=request.data)
        if serializer.is_valid():
            habit_id = serializer.validated_data['habit_id']
            try:
                habit = Habit.objects.get(id=habit_id, user=request.user)
                habit.streak = 0
                habit.save()
                return Response({"message": "Habit streak reset successfully!"}, status=status.HTTP_200_OK)
            except Habit.DoesNotExist:
                return Response({"error": "Habit not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
