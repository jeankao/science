from django import forms
from django.contrib.auth.models import User, Group
from account.models import Message

class UserRegistrationForm(forms.ModelForm): 
    error_messages = {
        'duplicate_username': ("此帳號已被使用")
    }
    
    username = forms.RegexField(
        label="User name", max_length=30, regex=r"^[\w.@+-]+$",
        error_messages={
            'invalid': ("帳號名稱無效")
        }
    )
    
    password = forms.CharField(label='Password', 
                               widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password', 
                                widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']
            
    def clean_username(self):
        username = self.cleaned_data["username"]
        if self.instance.username == username:
            return username
        try:
            User._default_manager.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(
            self.error_messages['duplicate_username'],
            code='duplicate_username',
        )

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = "帳號"
        self.fields['first_name'].label = "姓名"
        self.fields['email'].label = "電子郵件"
        self.fields['password'].label = "密碼"
        self.fields['password2'].label = "再次確認密碼"    

class UserUpdateForm(forms.ModelForm): 
    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = "帳號"
        self.fields['first_name'].label = "真實姓名"
        self.fields['email'].label = "電子郵件"         

class UserPasswordForm(forms.ModelForm): 
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('password',)
        
    def __init__(self, *args, **kwargs):
        super(UserPasswordForm, self).__init__(*args, **kwargs)  
        self.fields['password'].label = "密碼"
        
class UserTeacherForm(forms.Form):    
    teacher = forms.BooleanField(required=False)
       
    def __init__(self, *args, **kwargs):
        user_id = kwargs.pop('pk', None)
        super(UserTeacherForm, self).__init__(*args, **kwargs)  
        self.fields['teacher'].label = "教師"  
        self.fields['teacher'].initial = User.objects.get(id=user_id).groups.filter(name='teacher').exists()
        
# 新增一個私訊表單
class LineForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['title','content',]
       
    def __init__(self, *args, **kwargs):
        super(LineForm, self).__init__(*args, **kwargs)
        self.fields['title'].label = "主旨"
        self.fields['title'].widget.attrs['size'] = 50
        self.fields['content'].label = "內容"
        self.fields['content'].required = False            
        self.fields['content'].widget.attrs['cols'] = 50
        self.fields['content'].widget.attrs['rows'] = 20           