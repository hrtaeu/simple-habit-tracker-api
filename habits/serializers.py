from rest_framework import serializers
from .models import Habit
from .models import HabitTimeLog


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = '__all__'

class HabitTimeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitTimeLog
        fields = '__all__'
