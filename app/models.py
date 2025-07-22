from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
ROLE_CHOICES=(
        ('admin','Admin'),
        ('freelancer','Freelancer')
    )
class User(AbstractUser):
    role=models.CharField(max_length=30,choices=ROLE_CHOICES)
    skills=models.CharField(max_length=30,blank=True)
    bio=models.TextField(blank=True)
    rating=models.IntegerField(choices=[(i,i) for i in range(1,6)],null=True)

    
    def is_admin(self):
        return self.role=='admin'
    def is_freelancer(self):
        return self.role=='freelancer'
#job posting
CATEGORY_CHOICES=[
    ('Web','Web Development'),
    ('design','Graphic Designing'),
    ('data','Data Entry'),
    ('marketing','Digital Marketing')
]
STATUS_CHOICES=[
    ('open','Open'),
    ('assigned','Assigned'),
    ('completed','Completed')
]
class Jobs(models.Model):
    title=models.CharField(max_length=30)
    description=models.CharField(max_length=250)
    deadline=models.DateField()
    category=models.CharField(max_length=100,choices=CATEGORY_CHOICES)
    budget=models.DecimalField(max_digits=10,decimal_places=2)
    status=models.CharField(max_length=100,choices=STATUS_CHOICES,default='open')
    poster = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='posted_jobs')
    freelancer = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name='assigned_jobs',
        limit_choices_to={'role': 'freelancer'})
class Bids(models.Model):
    job=models.ForeignKey(Jobs,on_delete=models.CASCADE)
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_amount=models.DecimalField(max_digits=10,decimal_places=2)
    message=models.TextField(max_length=50,blank=True)
    timeline=models.DateField()
    status=models.CharField(max_length=20,choices=STATUS_CHOICES,default='open')

    class Meta:
        unique_together = ('job', 'freelancer')


class Messages(models.Model):
    job_id = models.ForeignKey(Jobs, on_delete=models.CASCADE, related_name="messages", null=True, blank=True)
    from_user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    to_user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    content = models.TextField()
    file_url=models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
TASK_STATUS=[
    ('todo','Todo'),
    ('doing','Doing'),
    ('done','Done')
]
class Tasks(models.Model):
    job_id=models.ForeignKey(Jobs,on_delete=models.CASCADE)
    title=models.CharField(max_length=30)
    status=models.CharField(max_length=20,choices=TASK_STATUS,default='todo')
    assigned_user_id=models.ForeignKey(User,on_delete=models.CASCADE)

class Ratings(models.Model):
    job_id=models.ForeignKey(Jobs,on_delete=models.CASCADE)
    rated_by_user_id=models.ForeignKey(User,on_delete=models.CASCADE,related_name="received_feedback")
    rated_user_id=models.ForeignKey(User,on_delete=models.CASCADE,related_name='Rating_Given')
    rating=models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment=models.TextField(blank=True)
    class Meta:
        unique_together=('job_id','rated_by_user_id')
# Create your models here.
