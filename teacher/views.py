from django.shortcuts import render, redirect
from teacher.models import *
from student.models import *
from django.views import generic
from django.contrib.auth.models import User, Group
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from account.models import Message, MessagePoll
from account.forms import LineForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.http import JsonResponse
from teacher.forms import *
from django.core.files.storage import FileSystemStorage
from wsgiref.util import FileWrapper
from uuid import uuid4
import os

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
    fields = ["lesson", "name", "password"]
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
    fields = ["lesson", "name", "password"]
    success_url = "/teacher/classroom"
    template_name = 'form.html'

# 列出所有公告
class AnnounceListView(ListView):
    model = Message
    context_object_name = 'messages'
    template_name = 'teacher/announce_list.html'
    paginate_by = 20
    def dispatch(self, *args, **kwargs):
        if not in_teacher_group(self.request.user):
            raise PermissionDenied
        else :
            return super(AnnounceListView, self).dispatch(*args, **kwargs)
    def get_queryset(self):
        queryset = Message.objects.filter(classroom_id=self.kwargs['classroom_id'], author_id=self.request.user.id).order_by("-id")
        return queryset

    def get_context_data(self, **kwargs):
        context = super(AnnounceListView, self).get_context_data(**kwargs)
        context['classroom'] = Classroom.objects.get(id=self.kwargs['classroom_id'])
        return context

    # 限本班任課教師
    def render(request, self, context):
        if not is_teacher(self.request.user, self.kwargs['classroom_id']) and not is_assistant(self.request.user, self.kwargs['classroom_id']):
            return redirect('/')
        return super(AnnounceListView, self).render(request, context)

#新增一個公告
class AnnounceCreateView(CreateView):
    model = Message
    form_class = AnnounceForm
    template_name = 'teacher/announce_form.html'
    def dispatch(self, *args, **kwargs):
        if not in_teacher_group(self.request.user):
            raise PermissionDenied
        else :
            return super(AnnounceCreateView, self).dispatch(*args, **kwargs)
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.title = u"[公告]" + self.object.title
        self.object.author_id = self.request.user.id
        self.object.classroom_id = self.kwargs['classroom_id']
        self.object.type = 1
        self.object.save()
        self.object.url = "/teacher/announce/detail/" + str(self.object.id)
        self.object.save()

        #附件
        files = []
        if self.request.FILES.getlist('files'):
             for file in self.request.FILES.getlist('files'):
                fs = FileSystemStorage()
                filename = uuid4().hex
                fs.save("static/attach/"+str(self.request.user.id)+"/"+filename, file)
                files.append([filename, file.name])
        if files:
            for file, name in files:
                content = MessageContent()
                content.title = name
                content.message_id = self.object.id
                content.filename = str(self.request.user.id)+"/"+file
                content.save()
        # 班級學生訊息
        enrolls = Enroll.objects.filter(classroom_id=self.kwargs['classroom_id'])
        for enroll in enrolls:
            messagepoll = MessagePoll(message_id=self.object.id, reader_id=enroll.student_id)
            messagepoll.save()
        return redirect("/teacher/announce/"+str(self.kwargs['classroom_id']))

    def get_context_data(self, **kwargs):
        context = super(AnnounceCreateView, self).get_context_data(**kwargs)
        context['classroom'] = Classroom.objects.get(id=self.kwargs['classroom_id'])
        return context


# 公告
def announce_detail(request, message_id):
    message = Message.objects.get(id=message_id)
    files = MessageContent.objects.filter(message_id=message_id)
    classroom = Classroom.objects.get(id=message.classroom_id)

    announce_reads = []

    messagepolls = MessagePoll.objects.filter(message_id=message_id)
    for messagepoll in messagepolls:
        try:
            enroll = Enroll.objects.get(classroom_id=message.classroom_id, student_id=messagepoll.reader_id)
            announce_reads.append([enroll.seat, enroll.student.first_name, messagepoll])
        except ObjectDoesNotExist:
            pass

    def getKey(custom):
        return custom[0]
    announce_reads = sorted(announce_reads, key=getKey)
    return render(request, 'teacher/announce_detail.html', {'files':files,'message':message, 'classroom':classroom, 'announce_reads':announce_reads})


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

# 設定班級助教
@login_required
@user_passes_test(in_teacher_group, login_url='/')
def classroom_assistant(request, classroom_id):
    assistants = Assistant.objects.filter(classroom_id=classroom_id).order_by("-id")
    classroom = Classroom.objects.get(id=classroom_id)

    return render(request, 'teacher/assistant.html',{'assistants': assistants, 'classroom':classroom})

# 教師可以查看所有帳號
class AssistantListView(ListView):
    context_object_name = 'users'
    paginate_by = 20
    template_name = 'teacher/assistant_user.html'
    def dispatch(self, *args, **kwargs):
        if not in_teacher_group(self.request.user):
            raise PermissionDenied
        else :
            return super(AssistantListView, self).dispatch(*args, **kwargs)
    def get_queryset(self):
        if self.request.GET.get('account') != None:
            keyword = self.request.GET.get('account')
            queryset = User.objects.filter(Q(username__icontains=keyword) | Q(first_name__icontains=keyword)).order_by('-id')
        else :
            queryset = User.objects.all().order_by('-id')
        return queryset

    def get_context_data(self, **kwargs):
        context = super(AssistantListView, self).get_context_data(**kwargs)
        context['classroom'] = Classroom.objects.get(id=self.kwargs['classroom_id'])
        assistant_list = []
        assistants = Assistant.objects.filter(classroom_id=self.kwargs['classroom_id'])
        for assistant in assistants:
            assistant_list.append(assistant.user_id)
        context['assistants'] = assistant_list
        return context

# 列出所有助教課程
class AssistantClassroomListView(ListView):
    model = Classroom
    context_object_name = 'classrooms'
    template_name = 'teacher/assistant_list.html'
    paginate_by = 20
    def dispatch(self, *args, **kwargs):
        if not in_teacher_group(self.request.user):
            raise PermissionDenied
        else :
            return super(AssistantClassroomListView, self).dispatch(*args, **kwargs)
    def get_queryset(self):
        assistants = Assistant.objects.filter(user_id=self.request.user.id)
        classroom_list = []
        for assistant in assistants:
            classroom_list.append(assistant.classroom_id)
        queryset = Classroom.objects.filter(id__in=classroom_list).order_by("-id")
        return queryset

# Ajax 設為助教、取消助教
def assistant_make(request):
    classroom_id = request.POST.get('classroomid')
    user_id = request.POST.get('userid')
    action = request.POST.get('action')
    if user_id and action :
        if action == 'set':
            try :
                assistant = Assistant.objects.get(classroom_id=classroom_id, user_id=user_id)
            except ObjectDoesNotExist :
                assistant = Assistant(classroom_id=classroom_id, user_id=user_id)
                assistant.save()
            # 將教師設為0號學生
            enroll = Enroll(classroom_id=classroom_id, student_id=user_id, seat=0)
            enroll.save()
        else :
            try :
                assistant = Assistant.objects.get(classroom_id=classroom_id, user_id=user_id)
                assistant.delete()
                enroll = Enroll.objects.filter(classroom_id=classroom_id, student_id=user_id)
                enroll.delete()
            except ObjectDoesNotExist :
                pass
        return JsonResponse({'status':'ok'}, safe=False)
    else:
        return JsonResponse({'status':'fail'}, safe=False)

# 列出所有課程
class WorkList(ListView):
    model = TWork
    context_object_name = 'works'
    template_name = 'teacher/work_list.html'
    paginate_by = 20

    def get_queryset(self):
        queryset = TWork.objects.filter(classroom_id=self.kwargs['classroom_id']).order_by("-id")
        return queryset

    def get_context_data(self, **kwargs):
        context = super(WorkList, self).get_context_data(**kwargs)
        context['classroom'] = Classroom.objects.get(id=self.kwargs['classroom_id'])
        context['lesson'] = self.kwargs['lesson']
        return context

#新增一個作業
qType = [
    {'type': 'qStatus', 'label': '現象問題'},
    {'type': 'qData', 'label': '資料建模問題'},
    {'type': 'qFlow', 'label': '流程建模問題'},
]

class WorkCreate(CreateView):
    model = TWork
    #form_class = WorkForm
    fields = ['title']        # 指定要顯示的欄位
    template_name = 'teacher/assignment_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["qType"] = qType
        return context

    def form_valid(self, form):
        testf = self.request.POST
        self.object = form.save(commit=False)
        self.object.description = {'qStatus': self.request.POST.getlist('qStatus'), 'qData': self.request.POST.getlist('qData'), 'qFlow': self.request.POST.getlist('qFlow')}
        self.object.teacher_id = self.request.user.id
        self.object.classroom_id = self.kwargs['classroom_id']
        self.object.save()
        return redirect("/teacher/work/"+str(self.kwargs['lesson'])+"/"+str(self.kwargs['classroom_id']))

# 修改作業標題
class WorkUpdate(UpdateView):
    model = TWork
    fields = ['title']        # 指定要顯示的欄位
    template_name = 'teacher/assignment_form.html' # 要使用的頁面範本

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["qType"] = qType
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.description = {'qStatus': self.request.POST.getlist('qStatus'), 'qData': self.request.POST.getlist('qData'), 'qFlow': self.request.POST.getlist('qFlow')}
        self.object.save()
        return redirect('/teacher/work/'+str(self.kwargs['lesson'])+"/"+str(self.kwargs['classroom_id']))

    # 成功新增選項後要導向其所屬的投票主題檢視頁面
    def get_success_url(self):
        return '/teacher/work/'+str(self.kwargs['lesson'])+"/"+str(self.kwargs['classroom_id'])

# 科學運算現象描述問題
class Science1QuestionList(ListView):
    model = Science1Question
    context_object_name = 'questions'
    template_name = 'teacher/question_list.html'

    def get_queryset(self):
        queryset = Science1Question.objects.filter(work_id=self.kwargs['work_id']).order_by("-id")
        return queryset

    def get_context_data(self, **kwargs):
        context = super(Science1QuestionList, self).get_context_data(**kwargs)
        context['classroom'] = Classroom.objects.get(id=self.kwargs['classroom_id'])
        context['lesson'] = self.kwargs['lesson']
        context['work_id'] = self.kwargs['work_id']
        return context

# 科學運算現象描述問題
class Science1QuestionAnswer(ListView):
    model = Science1Work
    context_object_name = 'works'
    template_name = 'teacher/question_answer.html'

    def get_queryset(self):
        questions = Science1Question.objects.filter(work_id=self.kwargs['work_id'])
        if self.kwargs['q_id'] == 0:
            if len(questions) > 0:
                q_id = questions[0].id
            else :
                q_id = 0
        else :
            q_id = self.kwargs['q_id']
        enroll_pool = [enroll for enroll in Enroll.objects.filter(classroom_id=self.kwargs['classroom_id'], seat__gt=0).order_by('seat')]
        student_ids = map(lambda a: a.student_id, enroll_pool)
        work_pool = Science1Work.objects.filter(student_id__in=student_ids, question_id=q_id)
        work_ids = map(lambda a: a.id, work_pool)
        content_pool = Science1Content.objects.filter(work_id__in=work_ids)
        queryset = []
        for enroll in enroll_pool:
            works = filter(lambda w: w.student_id==enroll.student_id, work_pool)
            if works:
                contents = filter(lambda w: w.work_id==works[0].id, content_pool)
            else :
                contents = []
            queryset.append([enroll, contents])
        return queryset

    def get_context_data(self, **kwargs):
        context = super(Science1QuestionAnswer, self).get_context_data(**kwargs)
        context['classroom'] = Classroom.objects.get(id=self.kwargs['classroom_id'])
        context['lesson'] = self.kwargs['lesson']
        context['work_id'] = self.kwargs['work_id']
        questions = Science1Question.objects.filter(work_id=self.kwargs['work_id'])
        if self.kwargs['q_id'] == 0:
            if len(questions) > 0:
                q_id = questions[0].id
            else :
                q_id = 0
        else :
            q_id = self.kwargs['q_id']
        if q_id > 0 :
            context['question'] = Science1Question.objects.get(id=q_id)
        else :
            context['question'] = None
        context['questions'] = questions
        return context

#新增一個問題
class Science1QuestionCreate(CreateView):
    model = Science1Question
    form_class = QuestionForm
    template_name = 'form.html'
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.work_id = self.kwargs['work_id']
        self.object.save()
        return redirect("/teacher/work/question/"+str(self.kwargs['lesson'])+"/"+str(self.kwargs['classroom_id'])+"/"+str(self.kwargs['work_id']))

# 修改問題
class Science1QuestionUpdate(UpdateView):
    model = Science1Question
    fields = ['question']        # 指定要顯示的欄位
    template_name = 'form.html' # 要使用的頁面範本

    # 成功新增選項後要導向其所屬的投票主題檢視頁面
    def get_success_url(self):
        return "/teacher/work/question/"+str(self.kwargs['lesson'])+"/"+str(self.kwargs['classroom_id'])+"/"+str(self.kwargs['work_id'])

# 列出所有記錄
class LogList(ListView):
    model = Log
    context_object_name = 'logs'
    template_name = 'teacher/log_list.html'
    paginate_by = 50

    def get_queryset(self):
        enroll_pool = [enroll for enroll in Enroll.objects.filter(classroom_id=self.kwargs['classroom_id']).order_by('seat')]
        student_ids = map(lambda a: a.student_id, enroll_pool)
        queryset = Log.objects.filter(user_id__in=student_ids).order_by("-id")
        return queryset

    def get_context_data(self, **kwargs):
        context = super(LogList, self).get_context_data(**kwargs)
        return context

# 評分所有同學
class WorkScoreList(ListView):
    model = Enroll
    context_object_name = 'enrolls'
    template_name = 'teacher/work_score.html'
    paginate_by = 50

    def get_queryset(self):
        queryset = Enroll.objects.filter(classroom_id=self.kwargs['classroom_id']).order_by("seat")
        return queryset

    def get_context_data(self, **kwargs):
        context = super(WorkScoreList, self).get_context_data(**kwargs)
        context['classroom'] = Classroom.objects.get(id=self.kwargs['classroom_id'])
        context['lesson'] = self.kwargs['lesson']
        context['index'] = self.kwargs['index']
        return context

class AssignmentSubmissions(ListView):
    model = TWork
    context_object_name = 'submissions'

    def get_queryset(self):
        q_type = self.kwargs['type']
        assignment_id = self.kwargs['assignment_id']
        students = Enroll.objects.filter(classroom_id=self.kwargs['classroom_id'], seat__gt=0).values('student_id', 'seat').order_by('seat')
        sids = [stu['student_id'] for stu in students]
        submissions = []
        if q_type == 1:
            works = Science1Work.objects.filter(student_id__in=sids, index=assignment_id).values('id', 'question_id', 'student_id').order_by('id', 'question_id')
            wids = [w['id'] for w in works]
            work_pool = Science1Content.objects.filter(work_id__in=wids, deleted=False, edit_old=False).values('work_id', 'types', 'text', 'picname', 'publication_date').order_by('-publication_date_old')
            for stu in students:
                sid = stu['student_id']
                sworks = list(filter(lambda w: w['student_id'] == sid, works))
                data = {}
                for sw in sworks:
                    qid = 'q'+str(sw['question_id'])
                    items = list(filter(lambda w: w['work_id'] == sw['id'], work_pool))
                    data[qid] = {
                        'count': len(items),
                        'latest': items[0],
                    }
                submissions.append({
                    'stu': stu,
                    'data': data,
                })
        elif q_type in [2, 3]:
            data2 = Science2Json.objects.filter(student_id__in=sids, index=assignment_id, model_type=q_type-2).values('student_id', 'data')
            for stu in students:
                sid = stu['student_id']
                sworks = list(filter(lambda w: w['student_id'] == sid, data2))
                data = {}
                if sworks:
                    for q in sworks[0]['data']:
                        data[q] = {
                            'count': len(sworks[0]['data'][q]),
                            'latest': sworks[0]['data'][q][0],
                        }

                submissions.append({
                    'stu': stu,
                    'data': data,
                })
        return submissions

    def get_context_data(self, **kwargs):
        typename = ['', 'qStatus', 'qData', 'qFlow']
        ctx = super().get_context_data(**kwargs)
        ctx['assignment'] = TWork.objects.get(id=self.kwargs['assignment_id'])
        ctx['qlist'] = ctx['assignment'].description[typename[self.kwargs['type']]]
        ctx['qidx'] = list(map(lambda i: 'q'+str(i), range(1, len(ctx['qlist'])+1)))
        ctx['qtype'] = self.kwargs['type']
        ctx['subtemplate'] = 'teacher/assignment_type{}.html'.format(ctx['qtype'])
        return ctx

    def get_template_names(self):
        qtype = self.kwargs['type']
        return ['teacher/submission_list'+str(qtype)+'.html']