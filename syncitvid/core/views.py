import uuid

from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Room
from .serializers import RoomSerializer


class RoomViewset(viewsets.ModelViewSet):
    serializer_class=RoomSerializer
    queryset=Room.objects.prefetch_related("hosted_rooms","joined_rooms").all()



    def create(self, request, *args, **kwargs):
        alr_created_room=Room.objects.filter(host=request.user).first()
        if alr_created_room:
            return Response(
                {"error": f"You already created a room named {alr_created_room.name} created at {alr_created_room.room_created_at}. You can host only one."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer=self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(host=request.user,invite_code=str(uuid.uuid4()))
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    @action(methods=['POST'],detail=False)
    def join_room(self,request):
        invite_code=request.data.get('invite_code')
        if not invite_code:
            return Response({"error":"you should provide invite_code for getting room information"},status=status.HTTP_400_BAD_REQUEST)
        try:
            room = Room.objects.get(invite_code=invite_code)
        except Room.DoesNotExist:
            return Response({"error": "Room with this invite code not found"}, status=status.HTTP_404_NOT_FOUND)
        existing_room = Room.objects.filter(participant=request.user).first() 
        if existing_room:
            return Response(
                {"error": f"You already joined another room. named {existing_room.name} hosted by {existing_room.host.name}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if room.participant:
            if room.participant == request.user:
                return Response({"error":"You have already joined this room you can't join it again"})
            return Response({"error":"Someone has alr joined this group you can't join this group try another room."})
        room.participant=request.user
        room.participant_joined_at=timezone.now()
        room.save()
        return Response({"message":"Joined "},status=status.HTTP_200_OK)


        


