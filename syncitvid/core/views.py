import uuid

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Room
from .serializers import RoomSerializer


class RoomViewset(viewsets.ModelViewSet):
    serializer_class = RoomSerializer
    queryset = Room.objects.prefetch_related("hosted_rooms", "joined_rooms").all()

    def create(self, request, *args, **kwargs):
        alr_created_room = Room.objects.filter(host=request.user).first()
        if alr_created_room:
            return Response(
                {
                    "error": f"You already created a room named {alr_created_room.name} created at {alr_created_room.room_created_at}. You can host only one."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(host=request.user, invite_code=str(uuid.uuid4()))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["POST"], detail=False)
    def join_room(self, request):
        invite_code = request.data.get("invite_code")
        if not invite_code:
            return Response(
                {
                    "error": "you should provide invite_code for getting room information"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            room = Room.objects.get(invite_code=invite_code)
        except Room.DoesNotExist:
            return Response(
                {"error": "Room with this invite code not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        alr_joined = Room.objects.filter(participant=request.user).first()
        if alr_joined:
            return Response(
                {
                    "error": f"You already joined another room. named {alr_joined.name} hosted by {alr_joined.host.name}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if room.participant:
            if room.participant == request.user:
                return Response(
                    {
                        "error": "You have already joined this room you can't join it again"
                    }
                )
            return Response(
                {
                    "error": "Someone has alr joined this group you can't join this group try another room."
                }
            )
        if request.user == room.host:
            return Response(
                {"message": "You can't join your own created room"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        room.participant = request.user
        room.participant_joined_at = timezone.now()
        room.room_status="active"
        room.save()
        return Response({"message": "Joined "}, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        # only return my created and join rooms
        rooms = Room.objects.filter(
            Q(host=request.user) | Q(participant=request.user)
        ).distinct()
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):
        try:
            room = Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            return Response(
                {"error": "This room doesn't exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not room.participant and room.host == request.user:
            return Response(
                {"message": "You should share invite code to add participant"}
            )
        if room.host == request.user or room.participant == request.user:
            serializer = RoomSerializer(room)
            response = {"message": "ok", "room": serializer.data}
            return Response(response)

        return Response(
            {
                "error": "You are not associated with this room so you can't access this room"
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    @action(methods=["GET"], detail=True)
    def leave_room(self, request, pk=None):
        # now if user wanted to leave the room
        # so what happens is it takes the pk
        try:
            room = Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            return Response(
                {"error": "This room doesn't exist, Invalid leave request"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if room.host == request.user:
            room.room_status="closed"
            room.save()
            room.delete()
            return Response(
                {"message": "Room leaved and deleted successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        elif room.participant == request.user:
            room.participant = None
            room.last_participant_leaved_at = timezone.now()
            room.last_participant_name = request.user.name
            room.room_status="waiting"
            room.save()
        else:
            return Response(
                {"error": "You are not part of this room"},
                status=status.HTTP_403_FORBIDDEN,
            )

    @action(methods=["GET"], detail=True)
    def kick_participant(self, request, pk=None):
        room = get_object_or_404(Room, pk=pk)
        if room.host == request.user:
            if room.participant:
                room.last_participant_name = room.participant.name
                room.last_participant_leaved_at = timezone.now()
                room.participant = None
                room.room_status="waiting"
                room.save()
                return Response({"message": "success"}, status=status.HTTP_200_OK)
            return Response(
                {"error": "there is no participant to kick"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"error": "You can't kick participant , you are not creator of this room"},
            status=status.HTTP_403_FORBIDDEN,
        )
