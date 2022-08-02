from django.contrib import admin
from friend_app.models import FriendList, FriendRequest

class FriendListAdmin(admin.ModelAdmin):
    list_filter = ['user']
    list_display = ['user']
    search_fields = ['user']
    readonly_fields = ['user']
    list_per_page = 25

    class Meta:
        model = FriendList

admin.site.register(FriendList, FriendListAdmin)

class FriendRequestAdmin(admin.ModelAdmin):
    list_filter = ['sender', 'receiver']
    list_display = ['sender', 'receiver']
    search_fields = ['sender__email', 'receiver__email']
    readonly_fields = ['sender', 'receiver']
    list_per_page = 25

    class Meta:
        model = FriendRequest

admin.site.register(FriendRequest, FriendRequestAdmin)
