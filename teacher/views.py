from django.shortcuts import render
from teacher.models import Classroom
from student.models import Enroll
from django.views import generic
from django.contrib.auth.models import User, Group
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from account.models import Message, MessagePoll
from account.forms import LineForm
from django.contrib.auth.mixins import LoginRequiredMixin

class ClassroomList(generic.ListView):
    model = Classroom
    ordering = ['-id']
    paginate_by = 3   
    
class ClassroomCreate(CreateView):
    model =Classroom
    fields = ["name", "password"]
    success_url = "/teacher/classroom"   
    template_name = 'form.html'
      
    def form_valid(self, form):
        valid = super(ClassroomCreate, self).form_valid(form)
        classroom = form.save(commit=False)
        classroom.teacher_id = self.request.user.id
        classroom.save() 
        enroll = Enroll(classroom_id=classroom.id, student_id=classroom.teacher_id, seat=0)
        enroll.save()
        return valid
    
class ClassroomUpdate(UpdateView):
    model = Classroom
    fields = ["name", "password"]
    success_url = "/teacher/classroom"   
    template_name = 'form.html'

#新增一個公告
class AnnounceCreate(LoginRequiredMixin, CreateView):
    model = Message
    form_class = LineForm
    success_url = '/account/dashboard'    
    template_name = 'teacher/announce_form.html'     

    def form_valid(self, form):
        valid = super(AnnounceCreate, self).form_valid(form)
        self.object = form.save(commit=False)
        classroom = Classroom.objects.get(id=self.kwargs['classroom_id'])
        self.object.title = u"[公告]" + classroom.name + ":" + self.object.title
        self.object.author_id = self.request.user.id
        self.object.save()
        # 訊息
        enrolls = Enroll.objects.filter(classroom_id=self.kwargs['classroom_id'])
        for enroll in enrolls :
            messagepoll = MessagePoll(message_id=self.object.id, reader_id=enroll.student_id)
            messagepoll.save()              
        return valid
      
    # 限本班教師
    def render_to_response(self, context):
        teacher_id = Classroom.objects.get(id=self.kwargs['classroom_id']).teacher_id
        if not teacher_id == self.request.user.id:
            return redirect('/')
        return super(AnnounceCreate, self).render_to_response(context)       
      
    def get_context_data(self, **kwargs):
        context = super(AnnounceCreate, self).get_context_data(**kwargs)
        context['classroom'] = Classroom.objects.get(id=self.kwargs['classroom_id'])
        return context	    