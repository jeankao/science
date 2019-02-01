# -*- coding: UTF-8 -*-
from django.db import models
from django.contrib.auth.models import User
from teacher.models import Classroom
from django.utils import timezone
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder

# 學生選課資料
class Enroll(models.Model):
    # 學生序號
    student_id = models.IntegerField(default=0)
    # 班級序號
    classroom_id = models.IntegerField(default=0)
    # 座號
    seat = models.IntegerField(default=0)

    @property
    def classroom(self):
        return Classroom.objects.get(id=self.classroom_id)

    @property
    def student(self):
        return User.objects.get(id=self.student_id)

def upload_path_handler(instance, filename):
    return "static/certificate/0/{filename}".format(filename=instance.id+".jpg")

class Work(models.Model):
    HELP_CHOICES = [
            (0, "全部靠自己想"),
            (1, "同學幫一點忙"),
            (2, "同學幫很多忙"),
            (3, "老師幫一點忙"),
            (4, "老師幫很多忙"),
		]

    user_id = models.IntegerField(default=0)
    lesson_id = models.IntegerField(default=0)
    typing = models.IntegerField(default=0)
    index = models.IntegerField()
    memo = models.TextField()
    memo_c = models.IntegerField(default=0)
    memo_e = models.IntegerField(default=0)
    publish = models.BooleanField(default=False)
    publication_date = models.DateTimeField(default=timezone.now)
    score = models.IntegerField(default=-2)
    scorer = models.IntegerField(default=0)
	# scratch, microbit
    file = models.FileField()
    #　python
    picture = models.ImageField(upload_to = upload_path_handler, default = '/static/python/null.jpg')
    code = models.TextField(default='')
    helps = models.IntegerField(default=0, choices=HELP_CHOICES)
    answer = models.BooleanField(default=False)
    youtube = models.TextField(default='')
    comment = models.TextField(default='')

    def __unicode__(self):
        user = User.objects.filter(id=self.user_id)[0]
        index = self.index
        return user.first_name+"("+str(index)+")"

    @property
    def user(self):
        return User.objects.get(id=self.user_id)

class WorkFile(models.Model):
    work_id = models.IntegerField(default=0)
    filename = models.TextField()
    upload_date = models.DateTimeField(default=timezone.now)

#Science1現象
class Science1Question(models.Model):
    work_id = models.IntegerField(default=0)
    question =  models.TextField(default='')

class Science1Work(models.Model):
    question_id = models.IntegerField(default=0)
    student_id = models.IntegerField(default=0)
    index = models.IntegerField(default=0)
    publication_date = models.DateTimeField(default=timezone.now)

    def __unicode__(self):
        user = User.objects.filter(id=self.student_id)[0]
        index = self.index
        return user.first_name+"("+str(index)+")"

class Science1Content(models.Model):
    work_id =  models.IntegerField(default=0)
    types = models.IntegerField(default=0)
    text = models.TextField(default='')
    pic = models.FileField(blank=True,null=True)
    picname = models.CharField(max_length=60,null=True,blank=True)
    deleted = models.BooleanField(default=False)
    edit_old = models.BooleanField(default=False)

#Science4解釋
class Science4Work(models.Model):
    student_id = models.IntegerField(default=0)
    index = models.IntegerField(default=0)
    memo = models.TextField(default='')
    publication_date = models.DateTimeField(default=timezone.now)

    def __unicode__(self):
        user = User.objects.filter(id=self.student_id)[0]
        index = self.index
        return user.first_name+"("+str(index)+")"

class Science4Debug(models.Model):
    BUG_CHOICES = [
        (0, "程式語法錯誤"),
        (1, "程式邏輯錯誤"),
        (2, "其它"),
    ]

    work3_id =  models.IntegerField(default=0)
    bug_types = models.IntegerField(default=0, choices=BUG_CHOICES)
    bug = models.TextField(default='')
    improve = models.TextField(default='')
    publication_date = models.DateTimeField(default=timezone.now)

    def get_choice(self):
        return dict(Science4Debug.BUG_CHOICES)[self.bug_types]

class Science3Work(models.Model):
    HELP_CHOICES = [
            (0, "全部靠自己想"),
            (1, "同學幫一點忙"),
            (2, "同學幫很多忙"),
            (3, "老師幫一點忙"),
            (4, "老師幫很多忙"),
		]
    student_id = models.IntegerField(default=0)
    lesson = models.IntegerField(default=0)
    typing = models.IntegerField(default=0)
    index = models.IntegerField()
    publication_date = models.DateTimeField(default=timezone.now)
    picture = models.ImageField()
    helps = models.IntegerField(default=0, choices=HELP_CHOICES)
    code = models.TextField(default='')


    def get_choice(self):
        return dict(Science3Work.HELP_CHOICES)[self.typing]


    def __unicode__(self):
        user = User.objects.filter(id=self.user_id)[0]
        index = self.index
        return user.first_name+"("+str(index)+")"

# 資料建模，流程建模
class Science2Json(models.Model):
    index = models.IntegerField(default=0)
    student_id = models.IntegerField(default=0)
    model_type = models.IntegerField(default=0) # 0: 資料建模, 1: 流程建模
    data = JSONField(encoder=DjangoJSONEncoder, default=dict)