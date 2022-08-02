from rest_framework import serializers
from .models import *
from pnp_app.models import Profile

class FriendListSerializer(serializers.ModelSerializer):

    class Meta:
        model = FriendList
        fields = '__all__'

class SenderInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'preferred_name','first_name',  'last_name','profile_pic', 'intro', 'zip_code', 'email']

class FriendRequestSerializer(serializers.ModelSerializer):
    sender = SenderInfoSerializer()
    class Meta:
        model = FriendRequest
        fields = ['id', 'sender', 'receiver', 'is_active', 'created_on']
