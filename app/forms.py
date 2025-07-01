from app.models import *
from  django import forms 
from django.contrib.auth.forms import UserCreationForm
class signupform(UserCreationForm):
    class Meta:
        model=CustomUser
        fields=['username','email','password1','password2','role']
class jobform(forms.ModelForm):
    class Meta:
        model=Job
        fields=['title','description','budget','deadline']
class Bidform(forms.ModelForm):
    class Meta:
        model=Bid
        fields=['bid_amount','message','delivery_time']
class Feedbackform(forms.ModelForm):
    class Meta:
        model=Feedback
        fields=['feedback','rating']
class Milestonesform(forms.ModelForm):
    class Meta:
        model=Milestones
        fields=['title','description','due_date','is_completed','is_approved_by_client']
