
from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(blank=True, max_length=255)
    middle_name = models.CharField(max_length=255 , blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    preferred_name = models.CharField(max_length=255, blank=True)
    birthdate = models.DateField(blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True)
    email = models.EmailField(max_length=255, blank=True)
    intro = models.TextField(blank=True)
    profile_pic = models.CharField(max_length=255, blank=True)
    full_bio = models.TextField(blank=True)
    personal_interests = models.TextField(blank=True)
    family_interests = models.TextField(blank=True)
    available_times = models.TextField(blank=True)
    

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)

class Kid(models.Model):
    AGE_GROUP_CHOICES = [
        ('0-12 mos' , '0-12 mos'),
        ('1-3 yrs' , '1-3 yrs'),
        ('3-5 yrs' , '3-5 yrs'),
        ('elementary' , 'elementary'),
        ('middle school' , 'middle school'),
        ('high school' , 'high school'),
    ]

    GENDER_CHOICES = [
        ('Female', 'Female'),
        ('Male', 'Male'),
        ('Prefer not to answer', 'Prefer not to answer')
    ]

    profile_id = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="kids")
    age_group = models.CharField(choices=AGE_GROUP_CHOICES, max_length=255)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=255)

    def __str__(self):
        return str(self.profile_id.id)

class Event(models.Model):
    title = models.CharField(max_length=255, null=True)
    address = models.CharField(max_length=255)
    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    attendees = models.ManyToManyField(Profile)


class Messages(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="messages")
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="messages_received")
    subject = models.CharField(max_length=255)
    message = models.TextField()
    date_time = models.DateTimeField(auto_now_add=True)
    unread = models.BooleanField(default=True)

