from django import template
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from account.models import MessagePoll

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
    classroom = Classroom.object.get(id=classroom_id)
    if classroom.teacher_id == user_id:
        return True
    else:
        return False    

@register.filter(takes_context=True)
def read_already(message_id, user_id):
    try:
        messagepoll = MessagePoll.objects.get(message_id=message_id, reader_id=user_id)
    except ObjectDoesNotExist:
        messagepoll = MessagePoll()
    return messagepoll.read            