from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import HabitSerializer

class TrackCompletion(APIView):
    def post(self, request):
        # Logic to mark habit as completed
        data = request.data
        habit = HabitSerializer(data=data)
        if habit.is_valid():
            # Save the habit completion data
            return Response({"status": "success", "data": habit.validated_data})
        return Response({"status": "error", "message": "Invalid data"}, status=400)


# Create your views here.
