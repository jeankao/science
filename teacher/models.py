# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.postgres.fields import JSONField, ArrayField

# 班級
class Classroom(models.Model):
    Lesson_CHOICES = [
        (1, 'Science科學運算：使用Python3'),
	]

    LessonShort_CHOICES = [
        (1, 'Science'),
	]

    # 課程名稱
    lesson = models.IntegerField(default=0, choices=Lesson_CHOICES, verbose_name='課程名稱')
    # 班級名稱
    name = models.CharField(max_length=30, verbose_name='班級名稱')
    # 選課密碼
    password = models.CharField(max_length=30, verbose_name='選課密碼')
    # 授課教師
    teacher_id = models.IntegerField(default=0)

    @property
    def teacher(self):
        return User.objects.get(id=self.teacher_id)

    def lesson_choice(self):
        return dict(Classroom.LessonShort_CHOICES)[self.lesson]

#班級助教
class Assistant(models.Model):
    classroom_id = models.IntegerField(default=0)
    user_id = models.IntegerField(default=0)

#自訂作業
def work_json_default():
    return dict({'qStatus': [], 'qData': [], 'qFlow': []})

class TWork(models.Model):
    title = models.CharField("作業名稱", max_length=250)
    classroom_id = models.IntegerField(default=0)
    time = models.DateTimeField(default=timezone.now)
    description = JSONField("作業說明", default=work_json_default)