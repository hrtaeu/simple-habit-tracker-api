from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import HabitListCreateView, HabitDetailView, DailyReminderView, MotivationalQuoteView, SetHabitGoalView, CheckHabitCompletionView, HabitStreakView, WeeklySummaryView, CompletionReportView, SetCustomReminderView, HabitMilestoneRewardView, HabitReinforcementView
from .views import HabitTimeSpentView, ResetStreakView, RegisterView, GenerateHabitReportView, HabitFrequencyOverTimeView, SuggestTrackingMethodsView, SuggestNewHabitView, SuggestPersonalizedHabitView, ScaleHabitDifficultyView, HabitProgressCalendarView

urlpatterns = [
    path('habits/', HabitListCreateView.as_view(), name='habit-list'),
    path('habits/<int:pk>/', HabitDetailView.as_view(), name='habit-detail'),
    path('habits/daily-reminders/', DailyReminderView.as_view(), name='habit-reminders'),
    path('motivation/quotes/', MotivationalQuoteView.as_view(), name='motivation-quotes'),
    path('habits/set-goals/<int:pk>/', SetHabitGoalView.as_view(), name='set-habit-goals'),
    path('check-completion/<int:pk>/', CheckHabitCompletionView.as_view(), name='check-habit-completion'),
    path('habits/streaks/', HabitStreakView.as_view(), name='habit-streaks'),
    path('progress/weekly-summary/', WeeklySummaryView.as_view(), name='weekly-summary'),
    path('progress/completion-report/', CompletionReportView.as_view(), name='completion-report'),
    path('habits/set-custom-reminder/', SetCustomReminderView.as_view(), name='set-custom-reminder'),
    path('habits/milestones/rewards/', HabitMilestoneRewardView.as_view(), name='habit-milestone-rewards'),
    path('habits/reinforce/', HabitReinforcementView.as_view(), name='habit-reinforce'),
    path('habits/time-spent/<int:pk>/', HabitTimeSpentView.as_view(), name='habit-time-spent'),
    path('habits/reset-streak/<int:pk>/', ResetStreakView.as_view(), name='reset-streak'),
    path("reports/generate/", GenerateHabitReportView.as_view(), name="generate-habit-report"),
    path('habits/frequency-over-time/<int:pk>/', HabitFrequencyOverTimeView.as_view(), name='habit-frequency-over-time'),
    path('habits/suggest-tracking-methods/', SuggestTrackingMethodsView.as_view(), name='suggest-tracking-methods'),
    path('habits/suggest-new/<int:pk>/', SuggestNewHabitView.as_view(), name='suggest-new-habit'),
    path('habits/suggest-personalized/', SuggestPersonalizedHabitView.as_view(), name='suggest-personalized-habit'),
    path('habits/scale-difficulty/', ScaleHabitDifficultyView.as_view(), name='scale-habit-difficulty'),
    path('habits/progress-calendar/', HabitProgressCalendarView.as_view(), name='habit-progress-calendar'),

    path('register/', RegisterView.as_view(), name='register'),
    path('login/', obtain_auth_token, name='login'),
]

