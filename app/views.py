from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponseForbidden,HttpResponse
from .models import *
from django.db.models import Avg
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,authenticate,logout
from .forms import *
from django.contrib import messages
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime,timedelta
def home(request):
    return render(request,"home.html")
def signup_view(request):
    if request.method == 'POST':
        form = Signupform(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  
    else:
        form = Signupform()

    return render(request, 'authentication/signup.html', {'form': form})
def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        role = request.POST.get("role")  
        print("Login attempt:", username, password, role)
        user = authenticate(request, username=username, password=password)
        print("Authenticated user:", user) 
        if user is not None:
            if user.role == role:
                login(request, user)
                if role == "admin":
                    return redirect('admin-dashboard')
                elif role == "freelancer":
                    return redirect('freelancer-dashboard')
            else:
                messages.error(request, "Incorrect role selected.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "authentication/login.html")
def custom_logout(request):
    logout(request)  
    return redirect('login')
   
# Admin dashboard
@login_required
def Admin_dashboard(request):
   if request.user.is_authenticated and request.user.is_admin():
         total_jobs=Jobs.objects.count()
         total_bids=Bids.objects.count()
         total_feedback_ratings=Ratings.objects.count()
         average_rating = Ratings.objects.aggregate(avg=Avg('rating'))['avg'] or 0
         total_accepted_bids=Bids.objects.filter(accepted_at=True).count()
         total_freelancers=User.objects.filter(role='freelancer').count()
         total_budget=Jobs.objects.aggregate(total=models.Sum('budget'))['total']
         upcoming_deadlines=Jobs.objects.filter(deadline__isnull=False).count
         jobs=Jobs.objects.all()
         recent_activities=[]
         recent_Bids=Bids.objects.order_by('created_at')[:2]
         for bid in recent_Bids:
             activity = f"Bid for  {bid.job.title} with deadline {bid.delivery_time} and amount (Rs {bid.bid_amount}) has created on {bid.created_at.strftime('%Y-%m-%d')}"
             recent_activities.append(activity)
         recent_jobs=Jobs.objects.order_by('created_at')[:1]
         for job in recent_jobs:
             activity=f"Job {job.title} and description {job.description} and budget  {job.budget} has created at {job.created_at}"
             recent_activities.append(activity)
         return render(request,"admin/admin_dashbaord.html",{
            'total_jobs': total_jobs,
            'total_freelancers': total_freelancers,
            'total_budget': total_budget,
            'jobs':jobs,
            'total_bids':total_bids,
            'average_rating':average_rating,
            'total_accepted_bids':total_accepted_bids,
            'total_feedback_ratings':total_feedback_ratings,
             'recent_activities':recent_activities,
            'upcoming_deadlines': upcoming_deadlines,})
   return redirect('login')
@login_required 
def job_posting(request):
    if not request.user.is_admin():
            return HttpResponseForbidden("Only Admin has right to post the job")
    if request.method=="POST":
        form=jobform(request.POST)
        if form.is_valid():
            job=form.save(commit=False)
            job.posted_by= request.user
            job.save()
            return redirect('job_list')
    else:
        form=jobform()
    return render(request,"admin/jobs/job_posting.html",{'form':form})
@login_required
def job_list(request):
    all_jobs=Jobs.objects.all()
    data={
        'all_jobs':all_jobs,
    }
    return render(request,"admin/jobs/job_list.html",data)
@login_required
def freelancer_dashboard(request):
   if request.user.is_authenticated and request.user.is_freelancer():
      jobs = Jobs.objects.filter(freelancer=request.user)
      return render(request,"freelancer/freelancer_dashboard.html",{'jobs':jobs,})
   return redirect('login')
@login_required
def Place_bid(request,job_id):
    job = get_object_or_404(Jobs, id=job_id)
    if request.method=="POST":
        form=Bidform(request.POST)
        if form.is_valid():
            bid=form.save(commit=False)
            bid.job=job
            bid.freelancer=request.user
            bid.save()
            return redirect('freelancer-dashboard')
    else:
        form=Bidform()
    return render(request,"freelancer/Job/Place_biding.html",{'form':form,'job': job,})
def all_bids(request):
    total_bids=Bids.objects.all().filter(freelancer=request.user)
    return render(request,"freelancer/Job/my_bids.html",{'total_bids':total_bids})
# view bids
@login_required
def view_bids(request):
    bids=Bids.objects.all()
    return render(request,"admin/bids/view_bids.html",{'bids':bids})
#Accept Bid
@login_required
def accept_bid(request,job_id):
    job=get_object_or_404(Jobs,id=job_id)
    bid=Bids.objects.filter(job=job).first()
    if bid:
        bid.accepted_at=True
        bid.save()
        job.freelancer=bid.freelancer
        bid.job.save()
        messages.success(request,"You'r Bid is Accepted now and Assigned to a freelancer")
        return redirect('view_bids')
    else:
         return redirect('view_bids')
#Accepted Bid
@login_required
def accepted_bids(request):
    bids=Bids.objects.filter(accepted_at=True)
    return render(request, "admin/bids/accepted_bids.html", {'bids': bids})


# Feedback & Rating

@login_required
def all_job_feedback_view(request):
    jobs = Jobs.objects.all()
    form = Feedbackform()

    if request.method == 'POST':
        job_id = request.POST.get('job_id')
        job = get_object_or_404(Jobs, id=job_id)

        # Check if feedback already exists
        existing_feedback = Ratings.objects.filter(job=job, Given_by=request.user).first()
        if existing_feedback:
            messages.info(request, "You have already given feedback for this job.")
            return redirect('feedback-page')

        form = Feedbackform(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.job = job
            feedback.freelancer = job.freelancer
            feedback.Given_by = request.user
            feedback.save()
            messages.success(request, "Feedback submitted successfully!")
            return redirect('feedback-page')

    # Load feedbacks for all jobs
    job_feedback_data = []
    for job in jobs:
        job_feedback_data.append({
            'job': job,
            'feedbacks': Ratings.objects.filter(job=job),
            'already_given': Ratings.objects.filter(job=job, Given_by=request.user).exists()
        })

    return render(request, 'admin/feedback/feedback.html', {
        'job_feedback_data': job_feedback_data,
        'form': form,
    })
@login_required
# def add_milestone(request,job_id):
#     job=get_object_or_404(Jobs,id=job_id)
#     all_milestones=Milestones.objects.filter(job=job)
#     if request.method=="POST":
#         form=Milestonesform(request.POST)
#         if form.is_valid():
#             milestone=form.save(commit=False)
#             milestone.job=job
#             milestone.save()
#             return redirect('milestone',job_id=job.id)
#     else:
#         form=Milestonesform()
#         return render(request,"freelancer/milestone/milestones.html",{'form':form,'job':job,'all_milestones':all_milestones})  
@login_required
# def accept_milestone(request):
#     if request.method=="POST":
#         milestone_id=request.POST.get("milestone_id")
#         milestone=get_object_or_404(Milestones,id=milestone_id)
#         milestone.is_approved_by_client=True
#         milestone.save()
#         messages.success(request,"Milestone Approved Successfully!")

#     completed_milestone=Milestones.objects.all()
#     return render(request,"admin/milestones/accept_milestone.html",{'completed_milestone': completed_milestone})
# @login_required 
# def accepted_milestone(request):
#     all_milestone=Milestones.objects.filter(is_approved_by_client=True)
#     return render (request,"admin/milestones/accepted_milestone.html",{'all_milestone':all_milestone})
@login_required
def chat_page(request,job_id):
    if not request.user.is_authenticated:
        return redirect('login')
    job = get_object_or_404(Jobs, id=job_id)
    messages = Messages.objects.filter(job=job).order_by('timestamp')
    return render(request,"Chat/chatpage.html",{'job':job,'username':request.user.username,"messages": messages})
# job_completion certificate
@login_required
def job_completion_certificate(request,job_id):
    job=get_object_or_404(Jobs,id=job_id,freelancer=request.user)
    response=HttpResponse(content_type="application/pdf")
    response['Content-Disposition']='attachment; file_name="job_completion_certificate.pdf"'
    p=canvas.Canvas(response,pagesize=A4)
    width,height=A4
    p.setFont("Helvetica-Bold",24)
    p.drawCentredString(width/2,height -100,"Certificate of Job Completion")
    p.setFont("Helvetica",16)
    p.drawCentredString(width/2,height -160,f"This is the Certifiacte")
    p.setFont("Helvetica",18)
    p.drawCentredString(width/2,height -200,job.freelancer.get_full_name() or job.freelancer.username)
    p.setFont("Helvetica",14)
    p.drawCentredString(width/2,height -240,f"has SuccessFully Completed Job")
    p.setFont("Helvetica",16)
    p.drawCentredString(width/2,height -270,job.title)
    p.setFont("Helvetica",12)
    p.drawCentredString(width/2,height -310,f"Description:{job.description}")
    p.drawCentredString(width/2,height -330,f"Budget:{job.budget}")
    p.drawCentredString(width/2,height -350,f"Deadline:{job.deadline}")
    p.drawCentredString(width/2,height -370,f"Posted_by:{job.posted_by}")
    p.drawString(100,100,"Signature_____________________")
    p.showPage()
    p.save()
    return response
@login_required
def job_completion_list(request,):
    jobs=Jobs.objects.filter(freelancer=request.user)
    return render(request,"job_completion_certificate",{'jobs':jobs})
# Create your views here.
