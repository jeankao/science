from django.shortcuts import render
from teacher.models import Classroom
from student.models import Enroll
from django.views import generic
from django.contrib.auth.models import User, Group
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from account.models import Message, MessagePoll
from account.forms import LineForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, user_passes_test

def filename_browser(request, filename):
	browser = request.META['HTTP_USER_AGENT'].lower()
	if 'edge' in browser:
		response['Content-Disposition'] = 'attachment; filename='+urlquote(filename)+'; filename*=UTF-8\'\'' + urlquote(filename)
		return response			
	elif 'webkit' in browser:
		# Safari 3.0 and Chrome 2.0 accepts UTF-8 encoded string directly.
		filename_header = 'filename=%s' % filename.encode('utf-8').decode('ISO-8859-1')
	elif 'trident' in browser or 'msie' in browser:
		# IE does not support internationalized filename at all.
		# It can only recognize internationalized URL, so we do the trick via routing rules.
		filename_header = 'filename='+filename.encode("BIG5").decode("ISO-8859-1")					
	else:
		# For others like Firefox, we follow RFC2231 (encoding extension in HTTP headers).
		filename_header = 'filename*="utf8\'\'' + str(filename.encode('utf-8').decode('ISO-8859-1')) + '"'
	return filename_header		

# 判斷是否為同班同學
def is_classmate(user, classroom_id):
    enroll_pool = [enroll for enroll in Enroll.objects.filter(classroom_id=classroom_id).order_by('seat')]
    student_ids = map(lambda a: a.student_id, enroll_pool)
    if user.id in student_ids:
        return True
    else:
        return False	

# 判斷是否為授課教師
def is_teacher(user, classroom_id):
    if Classroom.objects.filter(teacher_id=user.id, id=classroom_id).exists():
        return True
    elif Assistant.objects.filter(user_id=user.id, classroom_id=classroom_id).exists():
        return True
    return False

def in_teacher_group(user):
    if not user.groups.filter(name='teacher').exists():
        if not Assistant.objects.filter(user_id=user.id).exists():
            return False
    return True
	
	
class ClassroomTeacherRequiredMixin(object):	
    def dispatch(self, request, *args, **kwargs):
        if 'classroom_id' in kwargs:
            classroom_id = self.kwargs['classroom_id']
        else:
            classroom_id = self.kwargs['pk']
        user = self.request.user
        jsonDec = json.decoder.JSONDecoder()	
        classroom_list = []
        profile = Profile.objects.get(user=user)
        if len(profile.classroom) > 0 :		
            classroom_list = jsonDec.decode(profile.classroom)
        if str(classroom_id) in classroom_list:
            if not user.groups.filter(name='teacher').exists():
                if not Assistant.objects.filter(user_id=user.id).exists():		
                    return redirect("/")
            return super(ClassroomTeacherRequiredMixin, self).dispatch(request,*args, **kwargs)
        else :
            return redirect('/')
			
class TeacherRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        if not user.groups.filter(name='teacher').exists():
            if not Assistant.objects.filter(user_id=user.id).exists():		
                return redirect("/")
        return super(TeacherRequiredMixin, self).dispatch(request,
            *args, **kwargs)	

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

# 設定班級助教
@login_required
def classroom_assistant(request, classroom_id):
    if not is_teacher(request.user, classroom_id):
        return redirect("/")
		
    assistants = Assistant.objects.filter(classroom_id=classroom_id).order_by("-id")
    classroom = Classroom.objects.get(id=classroom_id)

    return render(request, 'teacher/assistant.html',{'assistants': assistants, 'classroom':classroom})

# 教師可以查看所有帳號
class AssistantListView(ClassroomTeacherRequiredMixin, ListView):
    context_object_name = 'users'
    paginate_by = 20
    template_name = 'teacher/assistant_user.html'

    def get_queryset(self):
        if self.request.GET.get('account') != None:
            keyword = self.request.GET.get('account')
            if self.kwargs['group'] == 1:
                queryset = User.objects.filter(Q(groups__name='apply') & (Q(username__icontains=keyword) | Q(first_name__icontains=keyword))).order_by("-id")
            else :
                queryset = User.objects.filter(Q(username__icontains=keyword) | Q(first_name__icontains=keyword)).order_by('-id')		
        else :
            if self.kwargs['group'] == 1:
                queryset = User.objects.filter(groups__name='apply').order_by("-id")
            else :
                queryset = User.objects.all().order_by('-id')
        return queryset

    def get_context_data(self, **kwargs):
        context = super(AssistantListView, self).get_context_data(**kwargs)
        context['classroom'] = Classroom.objects.get(id=self.kwargs['classroom_id'])
        context['group'] = self.kwargs['group']
        assistant_list = []
        assistants = Assistant.objects.filter(classroom_id=self.kwargs['classroom_id'])
        for assistant in assistants:
            assistant_list.append(assistant.user_id)
        context['assistants'] = assistant_list
        return context

# 列出所有助教課程
class AssistantClassroomListView(TeacherRequiredMixin, ListView):
    model = Classroom
    context_object_name = 'classrooms'
    template_name = 'teacher/assistant_list.html'
    paginate_by = 20

    def get_queryset(self):
        assistants = Assistant.objects.filter(user_id=self.request.user.id)
        classroom_list = []
        for assistant in assistants:
            classroom_list.append(assistant.classroom_id)
        queryset = Classroom.objects.filter(id__in=classroom_list).order_by("-id")
        return queryset

# Ajax 設為助教、取消助教
def assistant_make(request):
    if not in_teacher_group(request.user):
        return JsonResponse({'status':'fail'}, safe=False)
		
    classroom_id = request.POST.get('classroomid')
    user_id = request.POST.get('userid')
    action = request.POST.get('action')
    user = User.objects.get(id=user_id)
    if user_id and action :
        if action == 'set':
            try :
                assistant = Assistant.objects.get(classroom_id=classroom_id, user_id=user_id)
            except ObjectDoesNotExist :
                assistant = Assistant(classroom_id=classroom_id, user_id=user_id)
                assistant.save()
            # 將助教設為0號學生
            enrolls = Enroll.objects.filter(classroom_id=classroom_id, student_id=user_id)
            if len(enrolls) == 0:
                enroll = Enroll(classroom_id=classroom_id, student_id=user_id, seat=0)
                enroll.save()
            try :
                group = Group.objects.get(name="class"+classroom_id)	
            except ObjectDoesNotExist :
                group = Group(name="class"+classroom_id)
                group.save()     
            group.user_set.add(request.user)	
            jsonDec = json.decoder.JSONDecoder()	
            classroom_list = []
            profile = Profile.objects.get(user=user)
            if len(profile.classroom) > 0 :		
                classroom_list = jsonDec.decode(profile.classroom)
            classroom_list.append(str(classroom_id))
            profile.classroom = json.dumps(classroom_list)
            profile.save()	
        else :
            try :
                assistant = Assistant.objects.get(classroom_id=classroom_id, user_id=user_id)
                assistant.delete()
                enroll = Enroll.objects.filter(classroom_id=classroom_id, student_id=user_id)
                enroll.delete()
            except ObjectDoesNotExist :
                pass
            try :
                group = Group.objects.get(name="class"+classroom_id)	
            except ObjectDoesNotExist :
                group = Group(name="class"+classroom_id)
                group.save()     
            group.user_set.remove(request.user)
            jsonDec = json.decoder.JSONDecoder()	
            classroom_list = []
            profile = Profile.objects.get(user=user)
            if len(profile.classroom) > 0 :		
                classroom_list = jsonDec.decode(profile.classroom)
                classroom_list.remove(str(classroom_id))
            profile.classroom = json.dumps(classroom_list)
            profile.save()				
        return JsonResponse({'status':'ok'}, safe=False)
    else:
        return JsonResponse({'status':'fail'}, safe=False)        
