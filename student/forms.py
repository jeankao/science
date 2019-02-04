from django import forms
from student.models import *

class EnrollForm(forms.ModelForm): 
    password = forms.CharField()

    class Meta:
        model = Enroll
        fields = ('seat',)
        
    def __init__(self, *args, **kwargs):
        super(EnrollForm, self).__init__(*args, **kwargs)  
        self.fields['password'].label = "選課密碼"
        self.fields['seat'].label = "座號"

# 新增一個作業
class SubmitF1Form(forms.ModelForm):
    class Meta:
        model = Science1Content
        fields = ['work_id', 'types', 'text', 'pic']

    def __init__(self, *args, **kwargs):
        super(SubmitF1Form, self).__init__(*args, **kwargs)
        self.fields['work_id'].required = True
        self.fields['types'].required = False
        self.fields['text'].required = False
        self.fields['pic'].required = False

# 資料建模，流程建模
class SubmitF2Form(forms.Form):
    jsonstr = forms.CharField(widget=forms.Textarea)

class SubmitF3Form(forms.Form):
    code = forms.CharField(widget=forms.Textarea)
    helps = forms.IntegerField()   
    screenshot = forms.CharField(widget=forms.HiddenInput())

# 新增一個作業
class SubmitF4Form(forms.Form):
    index = forms.IntegerField(widget=forms.HiddenInput())   
    memo = forms.CharField()

# 新增一個作業
class SubmitF4BugForm(forms.ModelForm):
    class Meta:
        model = Science4Debug
        fields = ['work3_id', 'bug_types', 'bug', 'improve']

    def __init__(self, *args, **kwargs):
        super(SubmitF4BugForm, self).__init__(*args, **kwargs)
        self.fields['work3_id'].required = False
        self.fields['bug_types'].required = False
        self.fields['bug'].required = False
        self.fields['improve'].required = False  

class SubmitGForm(forms.Form):
    memo =  forms.CharField(required=False)
    memo_e =  forms.IntegerField(required=False)
    memo_c =  forms.IntegerField(required=False)

    def __init__(self, *args, **kwargs):
        super(SubmitGForm, self).__init__(*args, **kwargs)
        self.fields['memo'].label = "心得感想"
        self.fields['memo_e'].label = "英文"
        self.fields['memo_c'].label = "中文"                      