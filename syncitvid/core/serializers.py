from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Room

User = get_user_model()


class RoomSerializer(serializers.ModelSerializer):
    hosted_by_me=serializers.SerializerMethodField()
    class Meta:
        model = Room
        fields = "__all__"
        read_only_fields = ["id","host","room_created_at","hosted_by_me"]

    def get_hosted_by_me(self,obj):
        request=self.context.get("request")
        if obj.host==request.user:
            return True
        return False
