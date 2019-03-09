from django import template
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from account.models import MessagePoll
from teacher.models import Assistant
import re
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
import json
import datetime
from django.utils import timezone

register = template.Library()

@register.filter(takes_context=True)
def realname(user_id):
    try:
        user = User.objects.get(id=user_id)
        return user.first_name
    except :
        pass
    return ""

@register.filter(name='has_group')
def has_group(user, group_name):
    try:
        group =  Group.objects.get(name=group_name)
    except ObjectDoesNotExist:
        group = None
    return group in user.groups.all()

from teacher.models import Classroom

@register.filter
def teacher_classroom(user_id, classroom_id):
    classroom = Classroom.objects.get(id=classroom_id)
    if classroom.teacher_id == user_id:
        return True
    else:
        assistants = Assistant.objects.filter(user_id=user_id, classroom_id=classroom_id)
        if assistants.exist():
            return True
        return False

@register.filter(takes_context=True)
def read_already(message_id, user_id):
    try:
        messagepoll = MessagePoll.objects.get(message_id=message_id, reader_id=user_id)
    except ObjectDoesNotExist:
        messagepoll = MessagePoll()
    return messagepoll.read

@register.filter(name='unread')
def unread(user_id):
    return MessagePoll.objects.filter(reader_id=user_id, read=False).count()

@register.filter(name='assistant')
def assistant(user_id):
    assistants = Assistant.objects.filter(user_id=user_id)
    if assistants:
      return True
    return False

@register.filter()
def is_pic(title):
    if title[-3:].upper() == "PNG":
        return True
    if title[-3:].upper() == "JPG":
        return True
    if title[-3:].upper() == "GIF":
        return True
    return False

@register.filter
def code_highlight(code):
    html_code = highlight(code, PythonLexer(), HtmlFormatter(linenos=True))
    return html_code

@register.filter
def get_at_index(list, index):
    return list.index(index)+1

@register.filter()
def list_item(list, index):
    try:
        return list[index]
    except TypeError:
        return None
    except KeyError:
        return None

@register.filter()
def memo(text):
  memo = re.sub(r"\n", r"<br/>", re.sub(r"\[m_(\d+)#(\d\d:\d\d:\d\d)\]", r"<button class='btn btn-default btn-xs btn-marker' data-mid='\1' data-time='\2'><span class='badge'>\1</span> \2</button>",text))
  return memo

@register.filter()
def toDate(str):
    utc = timezone.datetime.strptime(str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
    return timezone.localtime(utc)

@register.filter()
def flowType(tid):
    typeStr = ["輸入", "輸出", "迴圈", "判斷", "處理"]
    return typeStr[tid]