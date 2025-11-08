# rooms/models.py
import uuid

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Room(models.Model):
    STATUS_CHOICES = [
        ("waiting", "Waiting for participant"),
        ("active", "Active"),
        ("closed", "Closed"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    host = models.ForeignKey(
        User, related_name="hosted_rooms", on_delete=models.CASCADE
    )
    participant = models.ForeignKey(
        User,
        related_name="joined_rooms",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    invite_code = models.CharField(max_length=20, unique=True, blank=True)
    participant_joined_at = models.DateTimeField(blank=True, null=True)
    last_participant_name = models.CharField(max_length=100, blank=True)
    last_participant_leaved_at = models.DateTimeField(blank=True, null=True)
    room_created_at = models.DateTimeField(auto_now_add=True)
    room_status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="waiting"
    )

    def __str__(self):
        return f"{self.name} ({self.invite_code})"
