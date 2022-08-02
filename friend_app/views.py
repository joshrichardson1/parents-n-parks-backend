from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json
from pnp_app.models import Profile
from friend_app.models import FriendRequest, FriendList
from rest_framework import viewsets
from .models import FriendList
from .serializers import *
from .serializers import FriendRequestSerializer
# from django.views.decorators.csrf import ensure_csrf_cookie
# from django.utils.decorators import method_decorator
# from django.views.decorators.csrf import csrf_exempt


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response
from friend_app.forms import *


def get_token_auth_header(request):
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.META.get("HTTP_AUTHORIZATION", None)
    parts = auth.split()
    token = parts[1]

    return token

class FriendsListViewSet(viewsets.ModelViewSet):
    serializer_class = FriendListSerializer

    def get_queryset(self):
        friends = FriendList.objects.filter(user__user_id__username=self.request.user)
        print(friends.values('friends'))
        return friends

    def create(self, request, *args, **kwargs):
        user = Profile.objects.filter(user_id__username=self.request.user)[0]
        serializer = self.get_serializer(data=request.data) 
        request.data['user'] = user.id
        serializer.is_valid() 
        self.perform_create(serializer) 
        headers = self.get_success_headers(serializer.data) 
        return Response( serializer.data, status=status.HTTP_201_CREATED, headers=headers )

class FriendRequestViewSet(viewsets.ModelViewSet):
    
    serializer_class = FriendRequestSerializer

    def get_queryset(self):
        user = Profile.objects.filter(user_id=self.request.user.id)[0]
        print(user)
        return FriendRequest.objects.filter(receiver=user, is_active=True)
    # def get_queryset(self):
    #     print(self.__getattribute__)
    #     user = self.request.user
    #     # user = Profile.objects.filter(user=self.user.id)[0].id
    #     print("user: ", user)
    #     return FriendRequest.objects.filter(receiver=user)


@api_view(['GET','POST'])
def send_friend_request(self, *args, **kwargs):
    user = Profile.objects.get(user_id=self.user.id)
    payload = {}

    print(self.data)
    user_id = self.data['receiver_user_id'] # person you are adding as a friend
    # print(user_id)
    if user_id:
        # not needed because it is not being used at later steps
        # receiver = Profile.objects.get(pk=user_id)
        try:
            # get any friend requests active and not active
            friend_request = FriendRequest.objects.filter(sender=user, receiver=user_id)
            # find active requests
            try:
                for request in friend_request:
                    if request.is_active:
                        raise Exception('You already have a pending friend request')
                # if non are actice then create new request
                data = {'sender': user, 'receiver': user_id, 'is_active': True}
                friend_request = FriendRequestForm(data)
                if friend_request.is_valid():
                    friend_request.save()
                    payload['response'] = 'Friend request sent'
            except Exception as e:
                payload['response'] = str(e)
        except FriendRequest.DoesNotExist:
            # there is no request so create one
            friend_request = FriendRequest(sender=user, is_active=True, receiver=user_id)
            friend_request.save()
            payload['response'] = 'Friend request sent'

        if not 'response' in payload.keys():
            payload['response'] = 'Something went wrong'
    else:
        payload['response'] = 'unable to send friend request'

    return HttpResponse(json.dumps(payload), content_type='application/json')

@api_view(['GET', 'POST'])
def accept(self, *args, **kwargs):
    payload = {}
    request_id = self.data['request_id']
    
    # the id of the request itself
    if request_id:
        print(request_id)
        try:
            current_request = FriendRequest.objects.filter(id=request_id) #request id passed in http request 
            print(current_request)
            try: 
                for request in current_request:
                        request.accept()
                        payload['response'] = 'Friend request accepted!'
            except Exception as e:
                payload['response'] = str(e)
        except FriendRequest.DoesNotExist:
            payload['response'] = 'Supplied Friend Request Does Not Exist'

        if not 'response' in payload.keys():
            payload['response'] = 'Something went wrong'
    else:
        payload['response'] = 'Unable to accept or deny request'
    
    return HttpResponse(json.dumps(payload), content_type='application/json')

@api_view(['GET', 'POST'])
def decline(self, *args, **kwargs):
    payload = {}

    print(self.data)
    request_id = self.data['request_id']
    if request_id:
        try:
            current_request = FriendRequest.objects.filter(id=request_id) #request id passed in http request 
            try: 
                for request in current_request:
                        request.decline()
                        payload['response'] = 'Friend request declined!'
            except Exception as e:
                payload['response'] = str(e)
        except FriendRequest.DoesNotExist:
            payload['response'] = 'Supplied Friend Request Does Not Exist'

        if not 'response' in payload.keys():
            payload['response'] = 'Something went wrong'
    else:
        payload['response'] = 'Unable to accept or deny request'
    
    return HttpResponse(json.dumps(payload), content_type='application/json')

@api_view(['GET'])
def get_friend_info(self, *args, **kwargs):
    payload = {}

    # profile_id = self.data['profile_id']

    # if profile_id:
    try:
        friends_queryset = FriendList.objects.filter(user__user_id__username=self.user)
        try:
            friend_data = []
            for friend_obj in friends_queryset.values('friends'):
                friend_profile_id = friend_obj['friends']
                friend_profile = Profile.objects.get(id=friend_profile_id)
                print([field.name for field in friend_profile._meta.get_fields(include_parents=False) if field.concrete])
                friend_dict = {key: getattr(friend_profile, key) for key in [field.name for field in friend_profile._meta.get_fields(include_parents=False) if (field.concrete and (field.name != 'user' and field.name != 'birthdate'))]}
                friend_data.append(friend_dict)
            payload['response'] = friend_data
        except Exception as e:
            payload['response'] = str(e)
    except FriendList.DoesNotExist:
        payload['response'] = 'Supplied Profile Friends List Does Not Exist'

    return HttpResponse(json.dumps(payload), content_type='application/json')





