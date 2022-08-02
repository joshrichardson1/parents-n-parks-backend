from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework import viewsets
from functools import wraps
import jwt
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
import requests
from serpapi import GoogleSearch
import json


@permission_classes([AllowAny])
class UsersViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    
    # def create(self, request, *args, **kwargs): 
    #     print(self.request.user)
    #     serializer = self.get_serializer(data={'token_username': f'{self.request.user}'}) 
    #     serializer.is_valid(raise_exception=True) 
    #     if User.objects.filter(token_username=self.request.user):
    #         return JsonResponse({'error': 'user already exists'})
    #     self.perform_create(serializer) 
    #     headers = self.get_success_headers(serializer.data) 
    #     return Response( serializer.data, status=status.HTTP_201_CREATED, headers=headers ) 

    def get_queryset(self):
        print(self.request.user)
        return User.objects.filter(username=self.request.user)

@permission_classes([AllowAny])
class ProfilesViewSet(viewsets.ModelViewSet):
    # delete and put require profile_id in url
    serializer_class = ProfileSerializer
    


    def create(self, request, *args, **kwargs):

        user = User.objects.filter(username=self.request.user)[0]
        # print("user: ", user)
        # print(user.__dict__) 
        # serializer = self.get_serializer(data={'user': f'{user.__dict__["id"]}'}) 
        serializer = self.get_serializer(data=request.data) 
        request.data['user'] = user.id

        # serializer.is_valid(raise_exception=True) 
        serializer.is_valid() 

        self.perform_create(serializer) 
        headers = self.get_success_headers(serializer.data) 
        return Response( serializer.data, status=status.HTTP_201_CREATED, headers=headers ) 

    def get_queryset(self):
        
        qry = self.request.query_params.get('all')
        if qry is None:
            profile = Profile.objects.filter(user__username=self.request.user)
        else:
            if self.request.query_params['all'] == 'true':
                profile = Profile.objects.all()
        print(profile)
        return profile


@permission_classes([AllowAny])
class KidsViewSet(viewsets.ModelViewSet):
    serializer_class = KidSerializer
    http_method_names= ['get','post','head','options','delete']
     
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data) 
        serializer.is_valid(raise_exception=True) 
        serializer.is_valid() 
        self.perform_create(serializer) 
        headers = self.get_success_headers(serializer.data) 
        return Response( serializer.data, status=status.HTTP_201_CREATED, headers=headers ) 
    
    def delete(self, request, pk=None, *args, **kwargs):      
        qryParm = self.request.query_params.get('pk') 
        try:
            qryBody = self.request.data['kidId']
        except:
            qryBody = None

        if qryParm is not None:
            kidsDelete = Kid.objects.filter(id=qryParm)
            kidsDelete.delete()
            response = JsonResponse({'message': 'Child deleted'}) 
            return response
        elif qryBody is not None:
            kidsDelete = Kid.objects.filter(id=qryBody)
            kidsDelete.delete()
            response = JsonResponse({'message': 'Child deleted'})         
            return response
        else:
            response = JsonResponse({'message': 'Error on child deleted'})         
            return response
        
    def get_queryset(self):
        qry = self.request.query_params.get('all')
        friendQry = self.request.query_params.get('friend')
        if qry is None and friendQry is None:
            refID = Profile.objects.filter(user__username=self.request.user)[0].id
            kids = Kid.objects.filter(profile_id=refID)
        else:
            if self.request.query_params.get('all') == 'true':
                kids = Kid.objects.all()
            elif self.request.query_params['friend'] == 'true':
                kids = Kid.objects.filter(profile_id_id=self.request.data["profile_id"]).values()
        return kids

@permission_classes([AllowAny])
class EventViewset(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    def get_queryset(self):
        refID = Profile.objects.filter(user__username=self.request.user)[0].id
        return Event.objects.filter(attendees=refID).order_by('date')


@permission_classes([AllowAny])
class MessageListViewSet(viewsets.ModelViewSet):
    serializer_class = MessageListSerializer
    def get_queryset(self):
        print(self.request.user.id)
        profile_id = Profile.objects.filter(user_id=self.request.user.id)[0].id
        messages = Messages.objects.filter(receiver_id=profile_id)
        print(messages)
        return messages



@permission_classes([AllowAny])
class MessagesViewSet(viewsets.ModelViewSet):
    # delete and put require profile_id in url
    serializer_class = MessageSerializer
    queryset = Messages.objects.all()

    def create(self, request, *args, **kwargs):

        sender = Profile.objects.filter(user_id=self.request.user.id)[0]
        receiver = Profile.objects.filter(user_id=request.data['receiver'])[0]
        
        request.data['sender'] = sender.id
        request.data['receiver'] = receiver.id
        print(request.data)
        serializer = self.get_serializer(data=request.data) 
 
        serializer.is_valid() 
        print(serializer.errors)
        self.perform_create(serializer) 
        headers = self.get_success_headers(serializer.data) 
        return Response( serializer.data, status=status.HTTP_201_CREATED, headers=headers ) 

    def put(self, request, *args, **kwargs):  
        return self.partial_update(request, *args, **kwargs)


def get_token_auth_header(request):
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.META.get("HTTP_AUTHORIZATION", None)
    parts = auth.split()
    token = parts[1]

    return token

def requires_scope(required_scope):
    """Determines if the required scope is present in the Access Token
    Args:
        required_scope (str): The scope required to access the resource
    """
    def require_scope(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = get_token_auth_header(args[0])
            decoded = jwt.decode(token, verify=False)
            if decoded.get("scope"):
                token_scopes = decoded["scope"].split()
                for token_scope in token_scopes:
                    if token_scope == required_scope:
                        return f(*args, **kwargs)
            response = JsonResponse({'message': 'You don\'t have access to this resource'})
            response.status_code = 403
            return response
        return decorated
    return require_scope

# @api_view(['GET'])
# def fetch_local_events(request, location):
#     KEY = 'e96f00d013861615c3732975d2215fa059e6ad92740195fb5498df8de6fd9f06'
#     url = f'https://serpapi.com/search.json?engine=google_events&q=Family+Events+in+{location}&api_key={KEY}'
#     response = requests.get(url)
#     data = response.json()
#     return Response(data)

# @api_view(['GET'])
# def fetch_weather(request, zipcode):
#     KEY = '1b801810edf2f965e69f04b8e2c365a4'
#     url = f'https://api.openweathermap.org/data/2.5/weather?zip={zipcode},us&APPID={KEY}'
#     response = requests.get(url)
#     data = response.json()
#     return Response(data)


@api_view(['GET'])
@permission_classes([AllowAny])
def public(request):
    return JsonResponse({'message': 'Hello from a public endpoint! You don\'t need to be authenticated to see this.' + request.user.username})


@api_view(['GET'])
def private(request):

    return JsonResponse({'message': 'Hello from a private endpoint! You need to be authenticated to see this.' + request.user.username})

@permission_classes([AllowAny])
class serpapi(APIView):

    def get(self, *args, **kwargs):
        zip = self.request.query_params.get('zip')
        events_results = self.serpapiData(zip)
        return JsonResponse(events_results, safe=False)

    def serpapiData(self, zip):
        params = {
        "engine": "google_events",
        "q": f'Family Events in {zip}',
        "hl": "en",
        "gl": "us",
        "api_key": "e96f00d013861615c3732975d2215fa059e6ad92740195fb5498df8de6fd9f06"
        }

        search = GoogleSearch(params)
        results = search.get_dict()
        events_results = results["events_results"]
        return events_results

@permission_classes([AllowAny])
class fetch_weather(APIView):

    def get(self, *args, **kwargs):
        zip = self.request.query_params.get('zip')
        weatherData = self.fetchWeather(zip)
        return JsonResponse(weatherData, safe=False)

    def fetchWeather(self, zip):
        KEY = '1b801810edf2f965e69f04b8e2c365a4'
        url = f'https://api.openweathermap.org/data/2.5/weather?zip={zip},us&APPID={KEY}'
        response = requests.get(url)
        data = response.json()
        return data
