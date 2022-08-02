from django.forms import ModelForm
from friend_app.models import *

class FriendListForm(ModelForm):
    class Meta: 
        model = FriendList
        fields = '__all__'

class FriendRequestForm(ModelForm):
    class Meta: 
        model = FriendRequest
        fields = '__all__'