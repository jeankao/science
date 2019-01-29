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

class MessageFile(models.Model):
    message_id = models.IntegerField(default=0) 
    filename = models.TextField()
    before_name = models.TextField()
    upload_date = models.DateTimeField(default=timezone.now)

class MessageContent(models.Model):
    message_id =  models.IntegerField(default=0)
    user_id = models.IntegerField(default=0)
    title =  models.CharField(max_length=250,null=True,blank=True)
    filename = models.CharField(max_length=250,null=True,blank=True)    
    publication_date = models.DateTimeField(default=timezone.now)
    
# 系統記錄
class Log(models.Model):
    # 使用者序號
    user_id = models.IntegerField(default=0)
    # 事件內容
    event = models.CharField(max_length=100)
    # 事件內容
    url = models.CharField(max_length=100)    
	# 發生時間 
    publish = models.DateTimeField(default=timezone.now)

    @property
    def user(self):
        return User.objects.get(id=self.user_id)

    def __unicode__(self):
        return str(self.user_id) + "--" + self.event