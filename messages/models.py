from django.db import models
from datetime import timezone
from core.models import User

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
    message_date = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)