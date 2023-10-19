from django.db import models
from datetime import datetime
from core.models import User, Post, Profile

# Create your models here.

class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    has_unread = models.BooleanField(default=False)


class UserMessage(models.Model):
    conversation = models.ForeignKey('Conversation', related_name='+', on_delete=models.CASCADE, blank=True, null=True)
    sender_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    receiver_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    message_text = models.CharField(max_length=600)
    message_image = models.ImageField(upload_to='', blank=True, null=True)
    message_date = models.DateTimeField(default=datetime.now())
    is_read = models.BooleanField(default=False)

class Notification(models.Model):
    # 1 = Like, 2 = Comment, 3 = Follow, 4 = DM
    notification_type = models.IntegerField(null=True, blank=True)
    to_user = models.ForeignKey(User, related_name='notification_to', on_delete=models.CASCADE, null=True)
    from_user = models.ForeignKey(User, related_name='notification_from', on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    date = models.DateTimeField(default=datetime.now)
    user_has_seen = models.BooleanField(default=False)