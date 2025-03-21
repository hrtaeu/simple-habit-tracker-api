from rest_framework import generics, status, permissions
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView, exception_handler
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Sum
from django.utils.timezone import now, timedelta
from django.contrib.auth.models import User
from .serializers import RegisterSerializer
from collections import Counter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from datetime import datetime
from io import BytesIO
from .models import Habit
from calendar import monthrange
from collections import defaultdict
from rest_framework import status
from django.http import JsonResponse
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from .models import UserProfile
from django.urls import path 
import random
import json

from .models import Habit, HabitTimeLog
from .serializers import HabitSerializer, HabitTimeLogSerializer, ResetStreakSerializer


class CustomLoginView(ObtainAuthToken):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)  # Call default login
        token = Token.objects.get(key=response.data['token'])  # Fetch user token
        return Response({
            'token': token.key,
            'message': "Good day! For your guide, input /habit/guide/"
        })

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None and "Invalid token header" in str(exc):
        response.data = {"Please provide a username and password to create your account and get started.",
                         "username:",
                         "password:",
                         "password2"}
    

    return response

def custom_404_view(request, exception=None):
    return JsonResponse(
        {"error": "The URL was not found. Try using the guide feature to see what you're trying to get.",
         "url": "http://127.0.0.1:8000/habit/guide/"
        },
        status=404
    )

def api_guide_view(request):
    """
    Returns a list of available API endpoints with descriptions.
    """
    api_endpoints = {
        "Authentication & User Management": {
            "Register": "/register/",
            "Login": "/login/",
            "View Profile": "/profile/view/",
            "Update Profile": "/profile/update/",
        },
        "Habit Management": {
            "List & Create Habits": "/habits/",
            "Habit Detail (Retrieve, Update, Delete)": "/habits/<int:pk>/",
            "Set Habit Goals": "/habits/set-goals/<int:pk>/",
            "Reset Habit Streak": "/habits/reset-streak/<int:pk>/",
        },
        "Habit Tracking & Completion": {
            "Track Completion": "/habits/track-completion/",
            "Check Completion": "/check-completion/<int:pk>/",
            "Habit Streaks": "/habits/streaks/",
            "Time Spent on Habit": "/habits/time-spent/<int:pk>/",
            "Frequency Over Time": "/habits/frequency-over-time/<int:pk>/",
            "Log in Time Spent on Habit": "habits/time-spent-log/",
        },
        "Progress & Reports": {
            "Weekly Summary": "/progress/weekly-summary/",
            "Completion Report": "/progress/completion-report/",
            "Generate Reports": "/reports/generate/",
            "Progress Calendar": "/habits/progress-calendar/",
        },
        "Motivation & Suggestions": {
            "Motivational Quotes": "/motivation/quotes/",
            "Suggest New Habit": "/habits/suggest-new/<int:pk>/",
            "Personalized Habit Suggestions": "/habits/suggest-personalized/",
        },
        "Other Features": {
            "Milestone Rewards": "/habits/milestones/rewards/",
            "Reinforcement Messages": "/habits/reinforce/<int:pk>/",
            "Daily Habit Reminders": "/habits/daily-reminders/",
            "Scale Habit Difficulty": "/habits/scale-difficulty/",
            "Suggest Tracking Methods": "/habits/suggest-tracking-methods/",
        }
    }
    
    return JsonResponse({"message": "API Guide", "endpoints": api_endpoints}, status=200)

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


class HabitListCreateView(generics.ListCreateAPIView):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]  

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

# Retrieve, Update, and Delete Habit
class HabitDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]  

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user) 


# Daily Habit Reminder View
class DailyReminderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        habits = Habit.objects.filter(user=request.user)

        if not habits.exists():
            return Response({"message": "You have no habits added yet."}, status=200)

        reminders = []
        for habit in habits:
            if habit.completed:
                reminders.append({
                    "habit": habit.name,
                    "message": f"🎉 Congrats! You've completed '{habit.name}' today!"
                })
            else:
                reminders.append({
                    "habit": habit.name,
                    "message": f"⏰ Reminder: Don't forget to complete '{habit.name}' today!"
                })

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

    def post(self, request, pk):  # Accept pk from URL
        goal = request.data.get("goal")
        if not goal:
            return Response({"error": "Goal is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            habit = Habit.objects.get(id=pk, user=request.user)  # Use pk instead of habit_id
            habit.goal = goal
            habit.save()
            return Response({"message": "Goal set successfully!", "habit": HabitSerializer(habit).data})
        except Habit.DoesNotExist:
            return Response({"error": "Habit not found."}, status=status.HTTP_404_NOT_FOUND)

# Check Habit Completion
class CheckHabitCompletionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            habit = Habit.objects.get(id=pk, user=request.user)
        except Habit.DoesNotExist:
            return Response({"error": "Habit not found."}, status=404)

        today = now().date()
        if habit.completed and habit.completed_at == today:
            return Response({"message": f"You completed '{habit.name}' today ✅"})
        
        return Response({"message": f"You have NOT completed '{habit.name}' today ❌"})

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

    def post(self, request, pk):  # Accept pk from URL
        try:
            habit = Habit.objects.get(id=pk, user=request.user)  # Use pk instead of habit_id
            habit.streak = 0
            habit.save()
            return Response({"message": "Habit streak reset successfully!"})
        except Habit.DoesNotExist:
            return Response({"error": "Habit not found"}, status=status.HTTP_404_NOT_FOUND)


class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Retrieve the authenticated user's profile."""
        user = request.user
        profile, _ = UserProfile.objects.get_or_create(user=user)  # Ensure profile exists
        
        data = {
            "username": user.username,  # Username is retrieved but not required for updates
            "date_joined": user.date_joined,
            "bio": profile.bio,
        }
        return Response(data, status=status.HTTP_200_OK)

    def patch(self, request):
        """Update the authenticated user's bio."""
        user = request.user
        profile, _ = UserProfile.objects.get_or_create(user=user)  # Ensure profile exists

        bio = request.data.get("bio", "")
        profile.bio = bio
        profile.save()

        return Response(
            {"message": "Profile updated successfully", "bio": profile.bio},
            status=status.HTTP_200_OK
        )

# Habit Milestone Reward View
class HabitMilestoneRewardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        habits = Habit.objects.filter(user=request.user)
        rewards = []
        no_streaks = True  # Flag to check if any habit has a streak

        # Medal tiers based on streak
        medals = {
            10: "🥉 Bronze Medal",
            20: "🥈 Silver Medal",
            30: "🥇 Gold Medal",
            50: "🏆 Platinum Trophy",
        }

        for habit in habits:
            if habit.streak and habit.streak > 0:
                no_streaks = False  # At least one habit has a streak

                # Determine the highest earned medal
                earned_medal = None
                for days, medal in sorted(medals.items()):
                    if habit.streak >= days:
                        earned_medal = medal
                
                rewards.append({
                    "habit": habit.name,
                    "streak": habit.streak,
                    "message": f"🎉 Congrats! You've reached a {habit.streak}-day streak!",
                    "medal": earned_medal if earned_medal else "🎖 Keep going!"
                })

        # If no streaks found, encourage the user
        if no_streaks:
            return Response({
                "message": "🚀 Keep going to unlock streaks and earn rewards!"
            }, status=status.HTTP_200_OK)

        return Response({"milestone_rewards": rewards}, status=status.HTTP_200_OK)

# Habit Reinforcement View
class HabitReinforcementView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):  # Use pk from URL
        habit = get_object_or_404(Habit, id=pk, user=request.user)

        # Example reinforcement messages based on streaks
        messages = {
            7: "💪 One week down! Keep it up!",
            14: "🔥 Two weeks strong! You're on fire!",
            30: "🎉 One month of consistency! Amazing job!",
        }
        message = messages.get(habit.streak, "👏 Keep going! Every small step counts!")

        return Response({
            "message": message,
            "habit": {
                "name": habit.name,
                "streak": habit.streak
            }
        }, status=status.HTTP_200_OK)

# Habit Time Spent View
class HabitTimeSpentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """Retrieve total time spent on a habit"""
        try:
            habit = Habit.objects.get(id=pk, user=request.user)
        except Habit.DoesNotExist:
            return Response({"error": "Habit not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if logs exist
        logs = HabitTimeLog.objects.filter(habit=habit)
        if not logs.exists():
            return Response({
                "habit": habit.name,
                "total_time_spent": 0,
                "message": f"No time logs found for '{habit.name}'."
            }, status=status.HTTP_200_OK)

        # Calculate total time spent
        total_time = logs.aggregate(Sum('time_spent'))['time_spent__sum'] or 0

        return Response({
            "habit": habit.name,
            "total_time_spent": total_time,
            "message": f"You've spent {total_time} minutes on '{habit.name}' so far."
        }, status=status.HTTP_200_OK)
    
class LogHabitTimeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        """Log time spent on a habit separately"""
        try:
            habit = Habit.objects.get(id=pk, user=request.user)
        except Habit.DoesNotExist:
            return Response({"error": "Habit not found."}, status=status.HTTP_404_NOT_FOUND)

        time_spent = request.data.get("time_spent")
        if not time_spent or not isinstance(time_spent, int) or time_spent <= 0:
            return Response({"error": "Invalid time_spent value."}, status=status.HTTP_400_BAD_REQUEST)

        # Save the time log
        HabitTimeLog.objects.create(habit=habit, time_spent=time_spent)

        return Response({"message": f"Logged {time_spent} minutes for '{habit.name}'."}, status=status.HTTP_201_CREATED)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

def create(self, request, *args, **kwargs):
    print("Request Headers:", request.headers)
    print("Request Data:", request.data)
    serializer = self.get_serializer(data=request.data)
    if not serializer.is_valid():
        print("Errors:", serializer.errors)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)
class ScaleHabitDifficultyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_habits = Habit.objects.filter(user=request.user)
        if not user_habits.exists():
            return Response({"message": "Track some habits first to get difficulty scaling suggestions!"})

        difficulty_suggestions = []

        for habit in user_habits:
            if habit.progress >= 80 and habit.streak >= 14:  # Strong consistency
                difficulty_suggestions.append(f"You're mastering {habit.name}! Try increasing difficulty, like extending duration or frequency.")
            elif habit.progress >= 50 and habit.streak >= 7:  # Moderate consistency
                difficulty_suggestions.append(f"You're progressing well in {habit.name}. Consider a small challenge, like adding intensity or variation.")
            else:  # Low consistency
                difficulty_suggestions.append(f"Keep building consistency in {habit.name}. Focus on maintaining a steady routine first.")

        return Response({"difficulty_suggestions": difficulty_suggestions})
    
class SuggestPersonalizedHabitView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_habits = Habit.objects.filter(user=request.user)
        if not user_habits.exists():
            return Response({"message": "Track some habits to get personalized suggestions!"})

        personalized_suggestions = []
        habit_names = [habit.name.lower() for habit in user_habits]  # Convert all habit names to lowercase

        # Mapping of habit categories to related keywords
        habit_categories = {
            "Sleep & Relaxation": ["sleep", "bedtime", "relaxation", "rest"],
            "Fitness & Exercise": ["exercise", "workout", "run", "yoga", "cardio", "strength training", "gym", "jog"],
            "Mental Wellness": ["meditation", "mindfulness", "journaling", "gratitude", "reflection"],
            "Social & Relationships": ["socializing", "friends", "family", "networking", "community"],
            "Health & Hydration": ["hydration", "water", "caffeine", "diet", "nutrition", "meal"],
            "Learning & Productivity": ["read", "study", "learn", "write", "skill-building"],
        }

        # Define suggestions for each category
        category_suggestions = {
            "Sleep & Relaxation": [
                "Try a relaxing bedtime routine like stretching or reading.",
                "Consider using a sleep tracker to monitor your rest patterns.",
            ],
            "Fitness & Exercise": [
                "Consider adding strength training or yoga to balance your routine.",
                "Try setting step-count goals for daily movement.",
            ],
            "Mental Wellness": [
                "Since you focus on mindfulness, try deep breathing exercises.",
                "Try tracking your mood daily along with your journal entries.",
            ],
            "Social & Relationships": [
                "Schedule weekly check-ins with family or friends.",
                "Try joining a local club or social group to build new connections.",
            ],
            "Health & Hydration": [
                "Since you track hydration, consider monitoring your caffeine intake.",
                "Explore meal prepping to improve your nutrition.",
            ],
            "Learning & Productivity": [
                "Since you enjoy learning, try setting monthly book or course goals.",
                "Experiment with the Pomodoro technique to improve focus.",
            ],
        }

        # Check which categories the user's habits match
        matched_categories = set()
        for category, keywords in habit_categories.items():
            for habit_name in habit_names:
                if any(keyword in habit_name.split() for keyword in keywords):  # Splitting ensures full words are checked
                    matched_categories.add(category)
                    break  # Avoid checking further if already matched

        # Add one suggestion per matched category
        for category in matched_categories:
            personalized_suggestions.append(category_suggestions[category][0])  # Pick the first suggestion

        if not personalized_suggestions:
            personalized_suggestions.append("Keep exploring new habits!")

        return Response({"suggestions": personalized_suggestions})
    
class SuggestNewHabitView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        habit = get_object_or_404(Habit, id=pk, user=request.user)
        suggestions = []

        habit_name = habit.name.lower()  # Normalize to lowercase

        # Keyword-based categories for flexible matching
        habit_keywords = {
            "hydration": ["water", "hydration", "drink", "fluid"],
            "fitness": ["exercise", "workout", "gym", "run", "training", "cardio", "lifting"],
            "reading": ["read", "books", "literature", "novel", "study"],
            "mental_wellness": ["meditation", "mindfulness", "breathe", "relax", "calm", "reflect"],
        }

        # Mapping categories to habit suggestions
        habit_suggestions = {
            "hydration": "Since you stay hydrated, try tracking your daily caffeine intake.",
            "fitness": "Try meal prepping to support your fitness goals.",
            "reading": "You might enjoy listening to audiobooks or joining a book club.",
            "mental_wellness": "You might benefit from journaling your daily thoughts.",
        }

        # Check which category the habit belongs to
        for category, keywords in habit_keywords.items():
            if any(keyword in habit_name for keyword in keywords):  # Match any keyword
                suggestions.append(habit_suggestions[category])

        # If no matches, provide a general message
        if not suggestions:
            suggestions.append("No direct suggestions for this habit. Keep exploring new habits!")

        return Response({"habit": habit.name, "suggestions": suggestions})
    
class SuggestTrackingMethodsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        preference = request.query_params.get("preference", "").lower()

        tracking_methods = {
            "digital": [
                {"name": "Habitica", "description": "Gamifies habit tracking with rewards."},
                {"name": "Loop Habit Tracker", "description": "Simple, free, and effective habit tracking app."},
                {"name": "Notion", "description": "Customizable habit tracker with templates."},
                {"name": "Google Calendar", "description": "Schedule daily habits as recurring events."},
            ],
            "manual": [
                {"name": "Bullet Journal", "description": "Manually track habits using a journal."},
                {"name": "Wall Calendar", "description": "Mark habit completions with checkmarks or stickers."},
                {"name": "Sticky Notes", "description": "Place reminders in visible locations."},
            ],
            "hybrid": [
                {"name": "Trello", "description": "Create habit tracking boards with digital and physical tasks."},
                {"name": "Excel/Google Sheets", "description": "Use spreadsheets for tracking progress."},
            ],
        }

        if preference not in tracking_methods:
            return Response({
                "message": "Please specify a preference: 'digital', 'manual', or 'hybrid'.",
                "example_usage": "/habits/suggest-tracking-methods/?preference=digital"
            }, status=400)

        return Response({
            "message": f"Here are some recommended {preference} habit-tracking methods!",
            "methods": tracking_methods[preference]
        })
class HabitFrequencyOverTimeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        days = int(request.query_params.get("days", 30))  # Default to last 30 days

        try:
            habit = Habit.objects.get(id=pk, user=request.user)
        except Habit.DoesNotExist:
            return Response({"error": "Habit not found."}, status=404)

        start_date = now().date() - timedelta(days=days)
        completed_dates = list(Habit.objects.filter(
            user=request.user, 
            id=pk, 
            completed=True, 
            completed_at__gte=start_date
        ).values_list("completed_at", flat=True))

        # Fix: Use Counter to count occurrences
        frequency_counter = Counter(completed_dates)
        frequency_data = {str(date): count for date, count in frequency_counter.items()}

        return Response({
            "habit": habit.name,
            "period": f"Last {days} days",
            "frequency": frequency_data
        })
    
class GenerateHabitReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        report_type = request.query_params.get("type", None)

        # Check if the report_type is not provided in the query
        if not report_type:
            return Response({
                "error": "Please specify the report type. Use 'daily' or 'weekly' as the type.",
                "example_url": "Example: /reports/generate/?type=daily or /reports/generate/?type=weekly"
            }, status=status.HTTP_400_BAD_REQUEST)

        report_type = report_type.lower()
        if report_type not in ["daily", "weekly"]:
            return Response({
                "error": "Invalid report type. Use 'daily' or 'weekly'.",
                "example_url": "Example: /reports/generate/?type=daily or /reports/generate/?type=weekly"
            }, status=400)

        today = now().date()
        start_date = today if report_type == "daily" else today - timedelta(days=7)

        # Filter habits based on completion date
        habits = Habit.objects.filter(user=request.user, completed_at=today) if report_type == "daily" else Habit.objects.filter(user=request.user, completed_at__gte=start_date)

        # Generate PDF
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer)
        pdf.setTitle(f"Habit Report - {report_type.capitalize()}")

        # Header
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(100, 800, f"Habit Report ({report_type.capitalize()})")
        pdf.setFont("Helvetica", 12)
        pdf.drawString(100, 780, f"User: {request.user.username}")
        pdf.drawString(100, 765, f"Period: {start_date} to {today}")

        y_position = 740  # Initial Y position for listing habits

        if not habits.exists():
            pdf.setFont("Helvetica", 12)
            pdf.drawString(100, y_position, "No habits found for this period. Keep going! 🚀")
        else:
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(100, y_position, "Habit Progress:")
            y_position -= 20

            pdf.setFont("Helvetica", 11)
            for habit in habits:
                status_str = "✅ Completed" if habit.completed else "❌ Not Completed"
                streak_str = f"🔥 Streak: {habit.streak} days" if habit.streak else "No streak yet"
                progress = f"📊 Progress: {habit.progress}%" if hasattr(habit, "progress") else ""

                pdf.drawString(100, y_position, f"- {habit.name}: {status_str}")
                pdf.drawString(120, y_position - 15, f"{streak_str} {progress}")
                y_position -= 40

                # Prevent text from going off-page
                if y_position < 50:
                    pdf.showPage()  # Add a new page
                    y_position = 800  # Reset position

        pdf.save()
        buffer.seek(0)

        # Create downloadable file response
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="habit_report_{report_type}.pdf"'
        return response
    

class HabitProgressCalendarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Returns a structured calendar-like format of habit completion for a selected month and year."""
        user = request.user

        # Get query parameters (default to the current month & year)
        try:
            month = int(request.query_params.get("month", now().month))
            year = int(request.query_params.get("year", now().year))
        except ValueError:
            return Response({"error": "Invalid month or year"}, status=400)

        # Ensure valid month range (1-12)
        if not (1 <= month <= 12):
            return Response({"error": "Month must be between 1 and 12"}, status=400)

        # Get the number of days in the selected month
        _, last_day = monthrange(year, month)

        # Start and end of the selected month
        start_date = now().replace(year=year, month=month, day=1)
        end_date = start_date.replace(day=last_day)

        # Get completed habits for the user in the selected month and year
        habits = Habit.objects.filter(
            user=user,
            completed=True,
            completed_at__range=[start_date, end_date]
        )

        # Initialize a calendar-like structure
        calendar_data = {str(day): [] for day in range(1, last_day + 1)}

        for habit in habits:
            day = str(habit.completed_at.day)  # Convert to string for JSON keys
            calendar_data[day].append(habit.name)

        return Response({
            "month": start_date.strftime("%B"),  # Convert month number to name
            "year": year,
            "calendar": calendar_data
        })
