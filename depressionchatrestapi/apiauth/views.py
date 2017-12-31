from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, renderer_classes, permission_classes
from django.contrib import auth
from rest_framework.response import Response
from django.core import serializers
from django.db.utils import IntegrityError
import json
from .serializers import *
from rest_framework.permissions import AllowAny
from .models import *
from datetime import datetime
from django.db import connection

@permission_classes([AllowAny,])
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


@api_view(['POST'])
@permission_classes([AllowAny,])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    try:
        serializer.save()
    except IntegrityError:
        return Response({'msg': 'Email already registered!'}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'email': request.data['email']}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny,])
def login(request):
    user = auth.authenticate(username=request.data['email'], password=request.data['password'])
    if user is not None:
        serializer = UserSerializer(user)
        return JsonResponse(serializer.data, safe=False)
    else:
        return Response(data={'msg': 'Login information is incorrect!'},status=status.HTTP_400_BAD_REQUEST)

#TODO: fix oauth2 slow
@api_view(['GET','POST'])
@permission_classes([AllowAny,])
def friends(request, user_id):
    user_id = int(user_id)
    #TODO: optimize get friend query, using raw query maybe?
    if request.method == 'GET':
        user = User.objects.get(id=user_id)
        friendship_relations = user.profile.get_friendship_relations()
        serializer = FriendshipSerializer(friendship_relations, many=True, context={"user_id": int(user_id)})
        return JsonResponse(serializer.data, safe=False)
    # Add friend
    if request.method == 'POST':
        friend_id = request.POST.get('friend_id', None)
        friend_email = request.POST.get('email', None)
        if friend_email:
            try:
                friend_id = User.objects.filter(email=friend_email)[0].id
            except IndexError:
                return Response(data={"msg": "User does not exist!"}, status=status.HTTP_400_BAD_REQUEST)
        if friend_id > user_id:
            user1 = user_id
            user2 = friend_id
        else:
            user1 = friend_id
            user2 = user_id
        try:
            friendship = Friendship(user1_id=user1, user2_id=user2, status=Friendship.ACCEPTED, action_user_id=user_id)
            friendship.save()
        except IntegrityError:
            return Response(data={"msg": "You are already friends!"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = FriendshipSerializer(friendship, context={"user_id" : int(user_id)})
        return JsonResponse(serializer.data, safe=False)


@api_view(['GET','POST'])
@permission_classes([AllowAny,])
def messages(request, user1_id, user2_id):
    # Get messages between user with pk1 and user with pk2
    if request.method == 'GET':
        msg_list = Message.objects.filter((Q(to_user=user1_id)&Q(from_user=user2_id))|
                                          (Q(to_user=user2_id)&Q(from_user=user1_id)))
        serializer = MessageSerializer(msg_list, many=True)
        return JsonResponse(serializer.data, safe=False)

    # From user1 to user2
    if request.method == 'POST':
        # timestamp = request.data['timestamp']
        timestamp = datetime.now()
        text = request.data['text']
        serializer = MessageSerializer(data={"timestamp":timestamp, "text":text, "from_user":user1_id, "to_user":user2_id})
        if (serializer.is_valid()):
            serializer.save()
        else:
            raise Exception("Error in data")
        return JsonResponse(serializer.data)



