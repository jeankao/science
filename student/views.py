from django.shortcuts import render
from teacher.models import Classroom
from student.models import Enroll
from student.forms import EnrollForm
from django.views import generic
from django.contrib.auth.models import User, Group
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import IntegrityError

class ClassroomList(generic.ListView):
    model = Classroom
    paginate_by = 3   
    template_name = 'student/classroom_list.html'
       
    def get_context_data(self, **kwargs):
        context = super(ClassroomList, self).get_context_data(**kwargs)
        queryset = []
        enrolls = Enroll.objects.filter(student_id=self.request.user.id)
        classroom_ids = list(map(lambda a: a.classroom_id, enrolls))        
        classroom_dict = dict((f.classroom_id, f) for f in enrolls)
        classrooms = Classroom.objects.filter(id__in=classroom_ids)
        for classroom in classrooms:
            queryset.append([classroom, classroom_dict[classroom.id]])
        context['queryset'] = queryset 
        return context 

class ClassroomJoinList(generic.ListView):
    model = Classroom
    template_name = 'student/classroom_join.html'    
    
    def get_context_data(self, **kwargs):
        context = super(ClassroomJoinList, self).get_context_data(**kwargs)
        queryset = []
        enrolls = Enroll.objects.filter(student_id=self.request.user.id)
        classroom_ids = list(map(lambda a: a.classroom_id, enrolls))        
        classrooms = Classroom.objects.all().order_by("-id")
        for classroom in classrooms:
            if classroom.id in classroom_ids:
                queryset.append([classroom, True])
            else:
                queryset.append([classroom, False])
        context['queryset'] = queryset 
        return context 

class ClassroomEnrollCreate(CreateView):
    model = Enroll
    form_class = EnrollForm    
    success_url = "/student/classroom"  
    template_name = "form.html"
    
    def form_valid(self, form):
        valid = super(ClassroomEnrollCreate, self).form_valid(form)
        if form.cleaned_data['password'] == Classroom.objects.get(id=self.kwargs['pk']).password:
            enrolls = Enroll.objects.filter(student_id=self.request.user.id, classroom_id=self.kwargs['pk'])
            if not enrolls.exists():
                enroll = Enroll(student_id=self.request.user.id, classroom_id=self.kwargs['pk'], seat=form.cleaned_data['seat'])
                enroll.save()
        return valid

class ClassmateList(generic.ListView):
    model = Enroll   
    template_name = 'student/classmate.html'
    
    def get_queryset(self):
        enrolls = Enroll.objects.filter(classroom_id=self.kwargs['pk'])
        return enrolls    
      
class ClassroomSeatUpdate(UpdateView):
    model = Enroll
    fields = ['seat']
    success_url = "/student/classroom/"      
    template_name = "form.html"