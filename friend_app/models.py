from django.db import models
from django.conf import settings
from django.utils import timezone
from pnp_app.models import Profile
from django.contrib.auth.models import User

class FriendList(models.Model):
    user = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name="friend_list_user")
    friends = models.ManyToManyField(Profile, related_name="friends", blank=True)

    def __str__(self):
        profile = Profile.objects.get(id=self.user.id)
        return f'{profile.first_name}'
    
    def add_friend(self, account):
        # Add a new friend with this function
        # check if they are already friends
        if not account in self.friends.all():
            self.friends.add(account)
            self.save() # save may not be required
    
    def remove_friend(self, account):
        # Remove a friend with this function
        # if they are friends then we can remove them
        if account in self.friends.all():
            self.friends.remove(account)
            self.save()
    
    def unfriend(self, removed_acct):
        # this will unfriend someone from your account
        remover_friends_list = self # person terminating the friendship

        # now remove the friend from the remover's list
        remover_friends_list.remove_friend(removed_acct)

        # remove from the removed_acct list
        friends_list = FriendList.objects.get(user=removed_acct)
        friends_list.remove_friend(remover_friends_list.user) # could use self.user
    
    def is_mutual_friend(self, friend):
        # determine if friends
        if friend in self.friends.all():
            return True
        else:
            return False


class FriendRequest(models.Model):
    # this consists of two parts: Sender and receiver

    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="sender") # one user could send out many friend requests
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="receiver") # one user could receive many friend requests
    is_active = models.BooleanField(default=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender}'
    
    def accept(self):
        # accept the friend request
        # if accepted then add to both sender and receiver's friend list
        receiver_friend_list = FriendList.objects.get(user=self.receiver.id)
        if receiver_friend_list:
            receiver_friend_list.add_friend(self.sender)
            sender_friend_list = FriendList.objects.get(user=self.sender.id)
            if sender_friend_list:
                sender_friend_list.add_friend(self.receiver)
                self.is_active = False
                self.save()
    
    def decline(self):
        # decline the friend request
        # declined by setting is_active to false
        self.is_active = False
        self.save()
    
    def cancel(self):
        # this is canceled on the end of the person who sent the request
        # canceled by setting is_active to false
        # only different through notification
        self.is_active = False
        self.save()