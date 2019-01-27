from django import forms
from account.models import *
from teacher.models import *
from student.models import *

# 新增一個課程表單
class AnnounceForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['title','content']

    def __init__(self, *args, **kwargs):
        super(AnnounceForm, self).__init__(*args, **kwargs)
        self.fields['title'].label = "公告主旨"
        self.fields['title'].widget.attrs['size'] = 50
        self.fields['content'].label = "公告內容"
        self.fields['content'].widget.attrs['cols'] = 50
        self.fields['content'].widget.attrs['rows'] = 20

# 新增一個作業
class WorkForm(forms.ModelForm):
    class Meta:
        model = TWork
        fields = ['title']

    def __init__(self, *args, **kwargs):
        super(WorkForm, self).__init__(*args, **kwargs)
        self.fields['title'].label = "作業名稱"

# 新增一個問題
class QuestionForm(forms.ModelForm):
    class Meta:
        model = Science1Question
        fields = ['question']

    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        self.fields['question'].label = "問題"