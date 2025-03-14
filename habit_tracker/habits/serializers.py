from rest_framework import serializers
from .models import Habit
from .models import HabitTimeLog
from django.contrib.auth.models import User


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = '__all__'

class HabitTimeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitTimeLog
        fields = '__all__'

class ResetStreakSerializer(serializers.Serializer):
    habit_id = serializers.IntegerField()

class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user
