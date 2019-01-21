from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User

# 訊息
class Message(models.Model):
    author_id = models.IntegerField(default=0)
    classroom_id = models.IntegerField(default=0)
    title = models.CharField(max_length=250)
    content = models.TextField(default='')
    url = models.CharField(max_length=250)
    publication_date = models.DateTimeField(auto_now_add=True)
			
# 訊息池    
class MessagePoll(models.Model):
    message_id = models.IntegerField(default=0)
    reader_id = models.IntegerField(default=0) 
    read = models.BooleanField(default=False)
    
    @property
    def message(self):
        return Message.objects.get(id=self.message_id)