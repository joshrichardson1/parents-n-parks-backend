from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'

class KidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kid
        fields = ['id', 'profile_id_id', 'age_group', 'gender']

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'address', 'date', 'time', 'attendees']

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id','first_name', 'middle_name', 'last_name', 'preferred_name', 'birthdate', 'zip_code', 'email', 'user', 'intro', 'profile_pic', 'full_bio', 'personal_interests', 'family_interests', 'available_times']

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messages
        fields = ['id', 'sender', 'receiver', 'subject', 'message', 'date_time','unread'] 

class MessageListSerializer(serializers.ModelSerializer):
    sender = ProfileSerializer(read_only=True)
    class Meta:
        model = Messages
        fields = ['id', 'sender', 'receiver', 'subject', 'message', 'date_time', 'unread'] 