from app.models import *
from  django import forms 
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import UserCreationForm
class Signupform(forms.ModelForm):
    class Meta:
        model=User
        fields=['username','email','password','role','skills','bio','rating']
        widgets = {
            'password': forms.PasswordInput(),
        }
    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
class jobform(forms.ModelForm):
    class Meta:
        model=Jobs
        exclude = ['posted_by']
class Bidform(forms.ModelForm):
    class Meta:
        model=Bids
        exclude = ['freelancer', 'job','status']
        fields='__all__'
class Feedbackform(forms.ModelForm):
    class Meta:
        model=Ratings
        exclude = ['rated_by_user_id', 'rated_user_id']
        fields='__all__'
class Tasksform(forms.ModelForm):
    class Meta:
        model=Tasks
        fields="__all__"
