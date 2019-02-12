from django.shortcuts import render, redirect
from teacher.models import *
from student.models import *
from student.forms import *
from account.models import *
from django.views import generic
from django.contrib.auth.models import User, Group
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import IntegrityError
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from uuid import uuid4
from wsgiref.util import FileWrapper
from binascii import a2b_base64
from django.utils import timezone
import os

# 判斷是否為授課教師
def is_teacher(user, classroom_id):
    if Classroom.objects.filter(teacher_id=user.id, id=classroom_id).exists():
        return True
    elif Assistant.objects.filter(user_id=user.id, classroom_id=classroom_id).exists():
        return True
    return False

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


# 列出個人所有作業
def work_list(request, typing, lesson, classroom_id):
    classroom = Classroom.objects.get(id=classroom_id)
    lessons = []

    assignments = TWork.objects.filter(classroom_id=classroom_id).order_by("-id")
    work_dict = dict(((work.index, work) for work in Work.objects.filter(typing=typing, user_id=request.user.id, lesson_id=lesson)))

    for idx, assignment in enumerate(assignments):
        if typing == "0":
            index = idx+1
        elif typing == "1":
            index = assignment.id
        elif typing == "2":
            index = assignment.id
        else :
            index = assignment.id
        if not index in work_dict:
            lessons.append([assignment, None])
        else:
            lessons.append([assignment, work_dict[index]])
    return render(request, 'student/work_list.html', {'typing':typing, 'lesson':lesson, 'lessons':lessons, 'classroom':classroom})

def submit(request, classroom_id, typing, lesson, index, user_id):
    work_dict = {}
    form = None
    work_dict = dict(((int(work.index), [work, WorkFile.objects.filter(work_id=work.id).order_by("-id")]) for work in Work.objects.filter(typing=typing, lesson_id=lesson, user_id=user_id)))
    assignment = TWork.objects.get(id=index)

    if lesson == 1:
        if request.method == 'POST':
            if typing == 1:
                types = request.POST.get('types')
                question_id = request.POST.get('q_index')
                if types == "11" or types == "12":
                    form = SubmitF1Form(request.POST, request.FILES)
                    if form.is_valid():
                        obj = form.save(commit=False)
                        try:
                            work = Science1Work.objects.get(student_id=user_id, index=index, question_id=question_id)
                        except ObjectDoesNotExist:
                            work = Science1Work(student_id=user_id, index=index, question_id=question_id)
                        except MultipleObjectsReturned:
                            works = Science1Work.objects.filter(student_id=user_id, index=index, question_id=question_id).order_by("-id")
                            work = work[0]
                        work.publication_date = timezone.now()
                        work.save()
                        obj.work_id=work.id
                        if types == "11":
                            # 記錄事件
                            log = Log(user_id=user_id, event='<'+assignment.title+'>現象描述<'+question_id+'>新增文字')
                            log.save()
                        if types == "12":
                            myfile = request.FILES['pic']
                            fs = FileSystemStorage(settings.BASE_DIR+"/static/upload/"+str(request.user.id)+"/")
                            filename = uuid4().hex
                            obj.picname = str(request.user.id)+"/"+filename
                            fs.save(filename, myfile)
                            # 記錄事件
                            log = Log(user_id=user_id, event='<'+assignment.title+'>現象描述<'+question_id+'>新增圖片')
                            log.save()
                        obj.pic = ""
                        obj.save()
                        obj.edit_id = obj.id
                        obj.save()
                        return redirect("/student/work/submit/"+str(classroom_id)+"/"+str(typing)+"/"+str(lesson)+"/"+str(index)+"/"+str(user_id)+"/#question"+str(question_id))
                elif types in ["21", "22"]: # 資料建模, 流程建模
                    form = SubmitF2Form(request.POST)
                    model_type = int(types == "22")
                    if form.is_valid():
                        jsonid = request.POST['jsonid']
                        qid = request.POST['qid']
                        if jsonid:
                            try:
                                json = Science2Json.objects.get(id=jsonid)
                            except ObjectDoesNotExist:
                                json = Science2Json(index=index, student_id=request.user.id, model_type=model_type)
                        else:
                            json = Science2Json(index=index, student_id=request.user.id, model_type=model_type)
                        if 'q'+qid not in json.data:
                            json.data['q'+qid] = []
                        json.data['q'+qid].insert(0, {'expr': request.POST['jsonstr'], 'created': timezone.now()})
                        json.save()
                        if types == "21":
                            # 記錄事件
                            log = Log(user_id=user_id, event='<'+assignment.title+'>資料建模<'+str(qid)+'>')
                            log.save()
                        else:
                            # 記錄事件
                            log = Log(user_id=user_id, event='<'+assignment.title+'>流程建模<'+str(qid)+'>')
                            log.save()
                        return redirect("/student/work/submit/{}/{}/{}/{}/{}/#tab{}".format(classroom_id, typing, lesson, index, user_id, types))
                elif types == "3":
                    form = SubmitF3Form(request.POST, request.FILES)
                    if form.is_valid():
                        work = Science3Work(index=index, student_id=request.user.id)
                        work.save()

                        dataURI = form.cleaned_data['screenshot']
                        try:
                            head, data = dataURI.split(',', 1)
                            mime, b64 = head.split(';', 1)
                            mtype, fext = mime.split('/', 1)
                            binary_data = a2b_base64(data)

                            prefix = 'static/work/science'
                            directory = "{prefix}/{uid}/{index}".format(prefix=prefix, uid=request.user.id, index=index)
                            image_file = "{path}/{id}.jpg".format(path=directory, id=work.id)

                            if not os.path.exists(settings.BASE_DIR + "/" + directory):
                                os.makedirs(settings.BASE_DIR + "/" + directory)
                            with open(settings.BASE_DIR + "/" + image_file, 'wb') as fd:
                                fd.write(binary_data)
                                fd.close()
                            work.picture=image_file
                        except ValueError:
                             path = dataURI.split('/', 3)
                             work.picture=path[3]

                        work.code=form.cleaned_data['code']
                        work.helps=form.cleaned_data['helps']
                        work.save()
                        # 記錄事件
                        log = Log(user_id=user_id, event='<'+assignment.title+'>程式化')
                        log.save()
                        return redirect("/student/work/submit/"+str(classroom_id)+"/"+str(typing)+"/"+str(lesson)+"/"+str(index)+"/"+str(user_id)+"/#tab3")
                elif types == "41":
                    form = SubmitF4Form(request.POST)
                    if form.is_valid():
                        work = Science4Work(student_id=user_id, index=index, memo=form.cleaned_data['memo'])
                        work.save()
                        # 記錄事件
                        log = Log(user_id=user_id, event='<'+assignment.title+'>觀察與除錯:心得')
                        log.save()
                        return redirect("/student/work/submit/"+str(classroom_id)+"/"+str(typing)+"/"+str(lesson)+"/"+str(index)+"/"+str(user_id)+"/#tab4")
                elif types == "42":
                    form = SubmitF4BugForm(request.POST)
                    if form.is_valid():
                        form.save()
                        # 記錄事件
                        log = Log(user_id=user_id, event='<'+assignment.title+'>觀察與除錯:新增錯誤')
                        log.save()
                        return redirect("/student/work/submit/"+str(classroom_id)+"/"+str(typing)+"/"+str(lesson)+"/"+str(index)+"/"+str(user_id)+"/#tab4")
        else:
            if not is_teacher(request.user, classroom_id) and not user_id == request.user.id:
                return redirect("/")
            contents1 = [[]]
            works_pool = Science1Work.objects.filter(student_id=user_id, index=index).order_by("-id")
            if 'qStatus' in assignment.description:
                questions = assignment.description['qStatus']
            else :
                questions = []
            for qid in range(1, len(questions)+1):
                works = list(filter(lambda w: w.question_id==qid, works_pool))
                if len(works)>0:
                    work_id = works[0].id
                else:
                    work_id = 0
                content_list = []
                for work in works:
                    contents = Science1Content.objects.filter(work_id=work.id, edit_old=False, deleted=False).order_by("publication_date_old")
                    history_list = []
                    for content in contents:
                        history = Science1Content.objects.filter(work_id=work.id, edit_id=content.edit_id, edit_old=True, deleted=False).order_by("-id")
                        history_list.append([content, history])
                    content_list.append([work, history_list])
                contents1.append([works, content_list])
            works3 = Science3Work.objects.filter(student_id=user_id, index=index).order_by("id")
            work3_ids = [work.id for work in works3]
            if works3.exists():
                work3 = works3[0]
            else :
                work3 = Science3Work(student_id=user_id, index=index)
            work4 = Science4Work.objects.filter(student_id=user_id, index=index).order_by("-id")
            contents4 = Science4Debug.objects.filter(work3_id__in=work3_ids).order_by("-id")
            try:
                expr = Science2Json.objects.get(student_id=user_id, index=index, model_type=0)
            except ObjectDoesNotExist:
                expr = Science2Json(student_id=user_id, index=index, model_type=0)
            except MultipleObjectsReturned:
                expr = Science2Json.objects.filter(student_id=user_id, index=index, model_type=0)[0]
            try:
                flow = Science2Json.objects.get(student_id=user_id, index=index, model_type=1)
            except ObjectDoesNotExist:
                flow = Science2Json(student_id=user_id, index=index, model_type=1)
            questions = Science1Question.objects.filter(work_id=index)
            return render(request, 'student/submit.html', {'user_id': user_id, 'form':form, 'work_id':work_id, 'assignment': assignment, 'questions':questions, 'typing':typing, 'lesson': lesson, 'index':index, 'contents1':contents1, 'contents4':contents4, 'work3':work3, 'works3':works3, 'work3_ids':work3_ids, 'work4': work4, 'expr': expr, 'flow': flow, 'classroom_id':classroom_id})


def content_edit(request, types, typing, lesson, index, question_id, content_id, classroom_id):
    assignment = TWork.objects.get(id=index)
    if request.method == 'POST':
        x = request.POST['content_id']
        try:
            obj = Science1Content.objects.get(id=x)
            obj.edit_old = True
            #obj.publication_date = request.POST['content_date']
            obj.save()
            content = Science1Content()
            content.work_id = obj.work_id
            content.types = obj.types
            content.text = request.POST['text']
            content.edit_id = obj.edit_id
            content.publication_date_old = obj.publication_date_old            
            content.publication_date = timezone.now()
            content.save()
        except ObjectDoesNotExist:
            pass
        # 記錄事件
        log = Log(user_id=request.user.id, event='<'+assignment.title+'>現象描述<'+str(question_id)+'>修改文字')
        log.save()
        return redirect("/student/work/submit/"+str(classroom_id)+"/"+str(typing)+"/"+str(lesson)+"/"+str(index)+"/"+str(request.user.id) + "/#question"+str(question_id))
    else:
        instance = Science1Content.objects.get(id=content_id)
        return render(request, 'student/submitF1E.html', {'instance':instance, 'q_index':question_id})

def content_delete(request, types, typing, lesson, index, question_id, content_id, classroom_id):
  assignment = TWork.objects.get(id=index)
  if types == 11 or types == 12:
    instance = Science1Content.objects.get(id=content_id)
    instance.deleted = True
    instance.save()
    if types == 11:
        # 記錄事件
        log = Log(user_id=request.user.id, event='<'+assignment.title+'>現象描述<'+str(question_id)+'>刪除文字')
        log.save()
    else:
        # 記錄事件
        log = Log(user_id=request.user.id, event='<'+assignment.title+'>現象描述<'+str(question_id)+'>刪除圖片')
        log.save()
        
    return redirect("/student/work/submit/"+str(classroom_id)+"/"+str(typing)+"/"+str(lesson)+"/"+str(index)+"/"+str(request.user.id) + "/#question"+str(question_id))

def content1_history(request, typing, lesson, index, question_id, user_id):
    contents1 = [[]]
    works_pool = Science1Work.objects.filter(student_id=user_id, index=index).order_by("-id")
    works = list(filter(lambda w: w.question_id==question_id, works_pool))
    content_list = []
    for work in works:
        contents = Science1Content.objects.filter(work_id=work.id, edit_old=False)
        history_list = []
        for content in contents:
            history = Science1Content.objects.filter(work_id=work.id, edit_id=content.edit_id, edit_old=True).order_by("-id")
            history_list.append([content, history])
        content_list.append([work, history_list])
    contents1.append([works, content_list])
    return render(request, 'student/content1_history.html', {'contents1':contents1, 'q_index':question_id})

# 評分所有心得
class WorkMemoList(ListView):
    model = Enroll
    context_object_name = 'memos'
    template_name = 'student/work_memo.html'
    paginate_by = 50

    def get_queryset(self):
        enrolls = Enroll.objects.filter(classroom_id=self.kwargs['classroom_id']).order_by("-seat")
        enroll_ids = list(map(lambda a: a.student_id, enrolls))
        queryset = []
        memo_pool = Science4Work.objects.filter(student_id__in=enroll_ids, index=self.kwargs['index']).order_by("-id")
        for enroll in enrolls :
            memo = list(filter(lambda w: w.student_id==enroll.student_id, memo_pool))
            if len(memo)>0:
                queryset.append([enroll, memo[0]])
            else:
                queryset.append([enroll, None])
        return queryset

    def get_context_data(self, **kwargs):
        context = super(WorkMemoList, self).get_context_data(**kwargs)
        context['classroom'] = Classroom.objects.get(id=self.kwargs['classroom_id'])
        context['lesson'] = self.kwargs['lesson']
        context['index'] = self.kwargs['index']
        return context