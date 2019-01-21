from django.shortcuts import render
from django.views import generic
from django.contrib.auth.models import User, Group
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, FormView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, RedirectView
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.shortcuts import render
from django.views import generic
from django.contrib.auth.models import User, Group
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, RedirectView
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from .forms import UserRegistrationForm, UserUpdateForm, UserPasswordForm, UserTeacherForm
from student.models import Enroll
from account.models import Message, MessagePoll
from account.forms import LineForm

class Login(FormView):
    success_url = '/'
    form_class = AuthenticationForm
    template_name = "login.html"

    @method_decorator(sensitive_post_parameters('password'))
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        # Sets a test cookie to make sure the user has cookies enabled
        request.session.set_test_cookie()

        return super(Login, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        auth_login(self.request, form.get_user())
        if form.get_user().id == 1 and form.get_user().first_name == "":
            user = User.objects.get(id=1)
            user.first_name = "管理員"
            user.save()
          
        # If the test cookie worked, go ahead and
        # delete it since its no longer needed
        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()

        return super(Login, self).form_valid(form)

class Logout(RedirectView):
    url = '/account/login/'

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return super(Logout, self).get(request, *args, **kwargs)

          
class SuperUserRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect("/account/login")
        return super(SuperUserRequiredMixin, self).dispatch(request,
            *args, **kwargs)

class UserList(SuperUserRequiredMixin, generic.ListView):
    model = User
    ordering = ['-id']

class UserDetail(LoginRequiredMixin, generic.DetailView):
    model = User
    
class UserCreate(CreateView):
    model = User
    form_class = UserRegistrationForm
    success_url = "/account/login"   
    template_name = 'form.html'
      
    def form_valid(self, form):
        valid = super(UserCreate, self).form_valid(form)
        new_user = form.save(commit=False)
        new_user.set_password(form.cleaned_data.get('password'))
        new_user.save()  
        return valid

class UserUpdate(SuperUserRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    success_url = "/account/user"   
    template_name = 'form.html'
    
class UserPasswordUpdate(SuperUserRequiredMixin, UpdateView):
    model = User
    form_class = UserPasswordForm
    success_url = "/account/user"   
    template_name = 'form.html'
    
    def form_valid(self, form):
        valid = super(UserPasswordUpdate, self).form_valid(form)
        new_user = form.save(commit=False)
        new_user.set_password(form.cleaned_data.get('password'))
        new_user.save()  
        return valid   

class UserTeacher(SuperUserRequiredMixin, FormView):
    success_url = '/account/user'
    form_class = UserTeacherForm
    template_name = "form.html"
      
    def form_valid(self, form):
        valid = super(UserTeacher, self).form_valid(form)
        user = User.objects.get(id=self.kwargs['pk'])
        try :
            group = Group.objects.get(name="teacher")	
        except ObjectDoesNotExist :
            group = Group(name="teacher")
            group.save()        
        if form.cleaned_data.get('teacher') :
            group.user_set.add(user)
        else: 
            group.user_set.remove(user)
        return valid  
      
    def get_form_kwargs(self):
        kwargs = super(UserTeacher, self).get_form_kwargs()
        kwargs.update({'pk': self.kwargs['pk']})
        return kwargs

class UserList(SuperUserRequiredMixin, generic.ListView):
    model = User
    ordering = ['-id']
    paginate_by = 3 

# 判斷是否為本班同學
def is_classmate(user_id, classroom_id):
    return Enroll.objects.filter(student_id=user_id, classroom_id=classroom_id).exists()

# 判斷可否觀看訊息
def line_can_read(message_id, user_id):
    if MessagePoll.objects.filter(message_id=message_id, reader_id=user_id).exists():
        return True
    elif Message.objects.filter(id=message_id, author_id=user_id).exists():
        return True
    else:
        return False

# 訊息(儀表板)
class LineList(LoginRequiredMixin, generic.ListView):
    model = MessagePoll
    paginate_by = 3
    template_name = 'account/dashboard.html'
        
    def get_queryset(self, **kwargs):
        messagepolls = MessagePoll.objects.filter(reader_id=self.request.user.id).order_by('-id')
        return messagepolls           
      
# 列出同學以私訊
class LineClassmateList(LoginRequiredMixin, generic.ListView):
    model = Enroll
    template_name = 'account/line_classmate.html'   
    
    def get_queryset(self):     
        queryset = Enroll.objects.filter(classroom_id=self.kwargs['classroom_id']).order_by("seat")
        return queryset
        
    # 限本班同學
    def render_to_response(self, context):
        if not is_classmate(self.request.user.id, self.kwargs['classroom_id']):
            return redirect('/')
        return super(LineClassmateListView, self).render_to_response(context)            
                
#新增一個私訊
class LineCreate(LoginRequiredMixin, CreateView):
    model = Message
    form_class = LineForm
    success_url = '/account/dashboard'    
    template_name = 'account/line_form.html'     

    def form_valid(self, form):
        valid = super(LineCreate, self).form_valid(form)
        self.object = form.save(commit=False)
        user_name = User.objects.get(id=self.request.user.id).first_name
        self.object.title = u"[私訊]" + user_name + ":" + self.object.title
        self.object.author_id = self.request.user.id
        self.object.save()
        # 訊息
        messagepoll = MessagePoll(message_id=self.object.id, reader_id=self.kwargs['user_id'])
        messagepoll.save()              
        return valid
      
    # 限本班同學
    def render_to_response(self, context):
        if not is_classmate(self.request.user.id, self.kwargs['classroom_id']):
            return redirect('/')
        return super(LineCreate, self).render_to_response(context)       
      
    def get_context_data(self, **kwargs):
        context = super(LineCreate, self).get_context_data(**kwargs)
        context['user_id'] = self.kwargs['user_id']
        messagepolls = MessagePoll.objects.filter(reader_id=self.kwargs['user_id'])
        message_ids = list(map(lambda a: a.message_id, messagepolls))
        context['messages']  = Message.objects.filter(id__in=message_ids, author_id=self.request.user.id).order_by("-id")
        return context	       

# 訊息內容
class LineDetail(generic.DetailView):
    model = Message
    template_name = "account/line_detail.html"
    
    def get_context_data(self, **kwargs):
        context = super(LineDetail, self).get_context_data(**kwargs)
        try: 
            messagepoll = MessagePoll.objects.get(message_id=self.kwargs['pk'], reader_id=self.request.user.id)
            messagepoll.read = True
            messagepoll.save()
        except ObjectDoesNotExist:
            pass
        context['can_read'] = line_can_read(self.kwargs['pk'], self.request.user.id)      
        return context