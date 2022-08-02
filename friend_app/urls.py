from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'friend_requests_view', views.FriendRequestViewSet, basename="friend_requests_view")
router.register(r'friends_list', views.FriendsListViewSet, basename="friends_list")

urlpatterns = [
    path('', include(router.urls)),
    path('friend_request/', views.send_friend_request, name='friend_request'),
    path('accept_request/', views.accept, name='accept_request'),
    path('decline_request/', views.decline, name='decline_request'),
    path('friend_info/', views.get_friend_info, name='friend_info'),
]