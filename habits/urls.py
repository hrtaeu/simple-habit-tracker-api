from django.urls import path
from .views import HabitListCreateView, HabitDetailView, DailyReminderView, MotivationalQuoteView, SetHabitGoalView, CheckHabitCompletionView

urlpatterns = [
    path('habits/', HabitListCreateView.as_view(), name='habit-list'),
    path('habits/<int:pk>/', HabitDetailView.as_view(), name='habit-detail'),
    path('habits/daily-reminders/', DailyReminderView.as_view(), name='habit-reminders'),
    path('motivation/quotes/', MotivationalQuoteView.as_view(), name='motivation-quotes'),
    path('habits/set-goals/', SetHabitGoalView.as_view(), name='set-habit-goals'),
    path('check-completion/', CheckHabitCompletionView.as_view(), name='check-habit-completion'),
]
