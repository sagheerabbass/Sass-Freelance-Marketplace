from app.models import *
from  django import forms 
class Signupform(forms.ModelForm):
    class Meta:
        model=User
        fields=['name','email','password','role','skills','bio','rating']
        widegets={
            'password':forms.PasswordInput(),
        }
class jobform(forms.ModelForm):
    class Meta:
        model=Jobs
        fields=['title','description','budget','deadline']
class Bidform(forms.ModelForm):
    class Meta:
        model=Bids
        fields='__all__'
class Feedbackform(forms.ModelForm):
    class Meta:
        model=Ratings
        fields='__all__'
class Tasksform(forms.ModelForm):
    class Meta:
        model=Tasks
        fields="__all__"
