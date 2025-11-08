from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Room

User = get_user_model()


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"
        read_only_fields = ["id", "room_created_at"]
