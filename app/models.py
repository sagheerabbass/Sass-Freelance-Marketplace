from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Authentication system
class CustomUser(AbstractUser):
    ROLE_CHOICES=(
        ('admin','Admin'),
        ('freelancer','Freelancer')
    )
    role=models.CharField(max_length=30,choices=ROLE_CHOICES)
    def is_admin(self):
        return self.role=='admin'
    def is_freelancer(self):
        return self.role=='freelancer'
#job posting
class Job(models.Model):
    title=models.TextField(max_length=30)
    description=models.TextField(max_length=30)
    posted_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    deadline=models.DateField()
    budget=models.DecimalField(max_digits=10,decimal_places=2)
    created_at=models.DateTimeField(auto_now_add=True)
    freelancer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_jobs')
class Bid(models.Model):
    job=models.ForeignKey(Job,on_delete=models.CASCADE)
    freelancer=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    bid_amount=models.DecimalField(max_digits=10,decimal_places=2)
    delivery_time=models.DateField()
    message=models.TextField(max_length=50,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    accepted_at=models.BooleanField(default=False)
class Feedback(models.Model):
    job=models.ForeignKey(Job,on_delete=models.CASCADE)
    freelancer=models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="received_feedback")
    rating=models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    feedback=models.TextField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    Given_by=models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="feedback_given")
    class Meta:
        unique_together=('job','Given_by')

class Milestones(models.Model):
    title=models.CharField(max_length=30)
    description=models.CharField(max_length=100)
    job=models.ForeignKey(Job,on_delete=models.CASCADE)
    is_completed=models.BooleanField(default=False)
    due_date=models.DateField(blank=True,null=True)
    is_approved_by_client=models.BooleanField(default=False)
class Messages(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="received_messages")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="messages", null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    

# Create your models here.
