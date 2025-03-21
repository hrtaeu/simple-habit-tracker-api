from django.urls import path, re_path
from rest_framework.authtoken.views import obtain_auth_token
from .views import HabitListCreateView, HabitDetailView, DailyReminderView, MotivationalQuoteView, SetHabitGoalView, CheckHabitCompletionView, HabitStreakView, WeeklySummaryView, CompletionReportView, UserProfileView, HabitMilestoneRewardView, HabitReinforcementView, LogHabitTimeView
from .views import HabitTimeSpentView, ResetStreakView, RegisterView, GenerateHabitReportView, HabitFrequencyOverTimeView, SuggestTrackingMethodsView, SuggestNewHabitView, SuggestPersonalizedHabitView, ScaleHabitDifficultyView, HabitProgressCalendarView, api_guide_view 

urlpatterns = [
   # Authentication & User Management
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', obtain_auth_token, name='login'),
    path('profile/view/', UserProfileView.as_view(), name="profile-view"),
    path('profile/update/', UserProfileView.as_view(), name="profile-update"),

    # Habit Management
    path('habits/', HabitListCreateView.as_view(), name='habit-list'),
    path('habits/<int:pk>/', HabitDetailView.as_view(), name='habit-detail'),
    path('habits/set-goals/<int:pk>/', SetHabitGoalView.as_view(), name='set-habit-goals'),
    path('habits/reset-streak/<int:pk>/', ResetStreakView.as_view(), name='reset-streak'),

    # Habit Tracking & Completion
    path('check-completion/<int:pk>/', CheckHabitCompletionView.as_view(), name='check-habit-completion'),
    path('habits/streaks/', HabitStreakView.as_view(), name='habit-streaks'),
    path('habits/time-spent/<int:pk>/', HabitTimeSpentView.as_view(), name='habit-time-spent'),
    path('habits/frequency-over-time/<int:hab>/', HabitFrequencyOverTimeView.as_view(), name='habit-frequency-over-time'),
    path('habits/time-spent-log/<int:pk>/', LogHabitTimeView.as_view(), name='log-habit-time'),

    # Progress & Reports
    path('progress/weekly-summary/', WeeklySummaryView.as_view(), name='weekly-summary'),
    path('progress/completion-report/', CompletionReportView.as_view(), name='completion-report'),
    path('reports/generate/', GenerateHabitReportView.as_view(), name="generate-habit-report"),
    path('habits/progress-calendar/', HabitProgressCalendarView.as_view(), name='habit-progress-calendar'),

    # Motivation & Rewards
    path('habits/milestones/rewards/', HabitMilestoneRewardView.as_view(), name='habit-milestone-rewards'),
    path('habits/reinforce/<int:pk>/', HabitReinforcementView.as_view(), name='habit-reinforce'),
    path('motivation/quotes/', MotivationalQuoteView.as_view(), name='motivation-quotes'),

    # Habit Suggestions & Tracking Methods
    path('habits/suggest-tracking-methods/', SuggestTrackingMethodsView.as_view(), name='suggest-tracking-methods'),
    path('habits/suggest-new/<int:pk>/', SuggestNewHabitView.as_view(), name='suggest-new-habit'),
    path('habits/suggest-personalized/', SuggestPersonalizedHabitView.as_view(), name='suggest-personalized-habit'),
    path('habits/scale-difficulty/', ScaleHabitDifficultyView.as_view(), name='scale-habit-difficulty'),

    # Habit Reminders
    path('habits/daily-reminders/', DailyReminderView.as_view(), name='habit-reminders'),

    # API Guide
    path('habits/guide/', api_guide_view, name='api-guide'),
]

