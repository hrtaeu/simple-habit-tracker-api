from rest_framework import serializers

class HabitSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=255)
    is_completed = serializers.BooleanField(default=False)
