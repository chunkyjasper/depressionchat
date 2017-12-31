from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    nickname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('nickname', 'email', 'id')

    def get_nickname(self, obj):
        return obj.profile.nickname


class FriendshipSerializer(serializers.ModelSerializer):

    most_recent_msg = serializers.SerializerMethodField()
    friendship_id = serializers.SerializerMethodField()
    friend = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ('friend', 'friendship_id', 'most_recent_msg')

    def get_friendship_id(self, obj):
        return obj.id

    def get_friend(self, obj):
        user_id = self.context.get("user_id")
        if obj.user1_id == user_id:
            return UserSerializer(obj.user2).data
        else:
            return UserSerializer(obj.user1).data

    def get_most_recent_msg(self, obj):
        msg = obj.get_most_recent_message()
        if msg:
            return MessageSerializer(msg).data
        else:
            return None


class UserRelationSerializer(serializers.Serializer):

    nickname = serializers.CharField()
    email = serializers.EmailField()
    friend_id = serializers.IntegerField()
    friendship_id = serializers.IntegerField()

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('timestamp', 'text', 'from_user', 'to_user')

class RegisterSerializer(serializers.Serializer):

    nickname = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()

    def create(self, validated_data):
        user = User.objects.create_user(username=validated_data['email'], **validated_data)
        user.profile.nickname = validated_data['nickname']

    def save(self):
        email = self.validated_data['email']
        password = self.validated_data['password']
        nickname = self.validated_data['nickname']
        user = User.objects.create_user(username=email, email=email, password=password)
        user.profile.nickname = nickname
        user.save()


class FriendshipSerializerV2(serializers.ModelSerializer):

    friendship_id = serializers.SerializerMethodField()
    most_recent_msg = MessageSerializer(read_only=True)
    class Meta:
        model = Friendship
        fields = ('friend', 'friendship_id', 'most_recent_msg')

    def get_friendship_id(self, obj):
        return obj.id

class FriendListSerializer(serializers.Serializer):

    friend = UserSerializer()
    most_recent_msg = MessageSerializer()
    friendship_id = serializers.IntegerField()

