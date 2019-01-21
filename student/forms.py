from django import forms
from student.models import Enroll

class EnrollForm(forms.ModelForm): 
    password = forms.CharField()

    class Meta:
        model = Enroll
        fields = ('seat',)
        
    def __init__(self, *args, **kwargs):
        super(EnrollForm, self).__init__(*args, **kwargs)  
        self.fields['password'].label = "選課密碼"
        self.fields['seat'].label = "座號"