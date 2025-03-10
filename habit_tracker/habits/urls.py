from django.urls import path
from .views import HabitListCreateView, HabitDetailView, DailyReminderView

urlpatterns = [
    path('habits/', HabitListCreateView.as_view(), name='habit-list'),
    path('habits/<int:pk>/', HabitDetailView.as_view(), name='habit-detail'),
    path('habits/daily-reminders/', DailyReminderView.as_view(), name='habit-reminders'),
]
