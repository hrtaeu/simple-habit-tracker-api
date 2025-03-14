from django.urls import path
from .views import HabitListCreateView, HabitDetailView, DailyReminderView, MotivationalQuoteView, SetHabitGoalView, CheckHabitCompletionView, HabitStreakView, WeeklySummaryView, CompletionReportView, SetCustomReminderView, HabitMilestoneRewardView, HabitReinforcementView, HabitReinforcementView 
from .views import HabitTimeSpentView, ResetStreakView
urlpatterns = [
    path('habits/', HabitListCreateView.as_view(), name='habit-list'),
    path('habits/<int:pk>/', HabitDetailView.as_view(), name='habit-detail'),
    path('habits/daily-reminders/', DailyReminderView.as_view(), name='habit-reminders'),
    path('motivation/quotes/', MotivationalQuoteView.as_view(), name='motivation-quotes'),
    path('habits/set-goals/', SetHabitGoalView.as_view(), name='set-habit-goals'),
    path('check-completion/', CheckHabitCompletionView.as_view(), name='check-habit-completion'),
    path('habits/streaks/', HabitStreakView.as_view(), name='habit-streaks'),
    path('progress/weekly-summary/', WeeklySummaryView.as_view(), name='weekly-summary'),
    path('progress/completion-report/', CompletionReportView.as_view(), name='completion-report'),
    path('habits/set-custom-reminder/', SetCustomReminderView.as_view(), name='set-custom-reminder'),
    path('habits/milestones/rewards/', HabitMilestoneRewardView.as_view(), name='habit-milestone-rewards'),
    path('habits/reinforce/', HabitReinforcementView.as_view(), name='habit-reinforce'),
    path('habits/time-spent/', HabitTimeSpentView.as_view(), name='habit-time-spent'),
    path('habits/reset-streak/', ResetStreakView.as_view(), name='reset-streak'),
]

