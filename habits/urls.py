from django.urls import path
from . import views
from .views import TrackCompletion

urlpatterns = [
    path('track-completion/', TrackCompletion.as_view(), name='track-completion'),
]
