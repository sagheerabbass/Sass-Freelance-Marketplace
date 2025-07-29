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
         total_accepted_bids=Bids.objects.filter(status='accepted').count()
         total_freelancers=User.objects.filter(role='freelancer').count()
         total_budget=Jobs.objects.aggregate(total=models.Sum('budget'))['total']
         upcoming_deadlines=Jobs.objects.filter(deadline__isnull=False).count
         jobs=Jobs.objects.all()
         recent_activities=[]
         recent_Bids=Bids.objects.order_by('job_id')[:2]
         for bid in recent_Bids:
             activity = f"Bid for  {bid.job.title} with deadline {bid.timeline} and amount (Rs {bid.bid_amount}) has created on {bid.timeline.strftime('%Y-%m-%d')}"
             recent_activities.append(activity)
         recent_jobs=Jobs.objects.order_by('poster')[:1]
         for job in recent_jobs:
             activity=f"Job {job.title} and description {job.description} and budget  {job.budget} has created at {job.deadline}"
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
           print(form.errors)
    else:
        form=jobform()
    return render(request,"admin/jobs/job_posting.html",{'form':form})
@login_required
def job_list(request):
    all_jobs = Jobs.objects.all()
    return render(request, "admin/jobs/job_list.html", {'all_jobs': all_jobs})

def edit_job(request, job_id):
    job = get_object_or_404(Jobs, id=job_id)
    
    if request.method == 'POST':
        form = jobform(request.POST, instance=job)
        if form.is_valid():
            print("Assigned Freelancer:", form.cleaned_data['freelancer'])
            form.save()
            return redirect('job_list')
    else:
        form = jobform(instance=job)

    return render(request, 'admin/jobs/edit_job.html', {'form': form, 'job': job})

def delete_job(request, job_id):
    job = get_object_or_404(Jobs, id=job_id)
    if request.method == 'POST':
        job.delete()
        messages.success(request, "Job deleted successfully!")
        return redirect('job_list')
@login_required
def freelancer_dashboard(request):
    if not request.user.is_freelancer():
        return redirect('login')  

    jobs = Jobs.objects.all()

    return render(request, "freelancer/freelancer_dashboard.html", {'jobs': jobs})
@login_required
def Place_bid(request, job_id):
    print("🔹 Place_bid view called")
    job = get_object_or_404(Jobs, id=job_id)
    print(f"🔹 Found job: {job.title}")

    # Check if user already bid
    existing_bid = Bids.objects.filter(job=job, freelancer=request.user).first()
    if existing_bid:
        messages.warning(request, "You have already placed a bid on this job.")
        return redirect('freelancer-dashboard')

    if request.method == "POST":
        print("🔹 POST request detected")
        form = Bidform(request.POST)
        if form.is_valid():
            print("✅ Form is valid")
            bid = form.save(commit=False)
            bid.job = job
            bid.freelancer = request.user
            bid.save()
            messages.success(request, "Bid placed successfully.")
            return redirect('freelancer-dashboard')
        else:
            print("❌ Form is invalid:", form.errors)
    else:
        print("🔸 GET request")

    form = Bidform()
    return render(request, "freelancer/Job/Place_biding.html", {
        'form': form,
        'job': job,
    })

def all_bids(request):
    total_bids=Bids.objects.all().filter(freelancer=request.user)
    return render(request,"freelancer/Job/my_bids.html",{'total_bids':total_bids})
# view bids
@login_required
def view_bids(request):
    bids = Bids.objects.select_related('job', 'freelancer').order_by('-status', '-id')
    accepted_bid_job_ids = set(bids.filter(status='accepted').values_list('job_id', flat=True))
    return render(request, "admin/bids/view_bids.html", {
        'bids': bids,
        'accepted_bid_job_ids': accepted_bid_job_ids,
    })
#Accept Bid
@login_required
def accept_bid(request, job_id):
    if request.method == "POST":
        bid_id = request.POST.get("bid_id")
        job = get_object_or_404(Jobs, id=job_id)
        selected_bid = get_object_or_404(Bids, id=bid_id, job=job)
        Bids.objects.filter(job=job).exclude(id=selected_bid.id).update(status="pending")
        selected_bid.status = "accepted"
        selected_bid.save()
        job.status = "assigned"
        job.freelancer = selected_bid.freelancer
        job.save()

        messages.success(request, "Bid has been accepted and job assigned successfully.")
        return redirect("view_bids")
#Accepted Bid
@login_required

def accepted_bids(request):
    bids = Bids.objects.filter(status='accepted').select_related('freelancer', 'job')
    return render(request, 'admin/bids/accepted_bids.html', {'bids': bids})

# Feedback & Rating

@login_required
def all_job_feedback_view(request):
    jobs = Jobs.objects.all()
    form = Feedbackform()

    if request.method == 'POST':
        job_id = request.POST.get('job_id')
        job = get_object_or_404(Jobs, id=job_id)

        # Check if already given feedback
        existing_feedback = Ratings.objects.filter(job_id=job, rated_by_user_id=request.user).first()
        if existing_feedback:
            messages.info(request, "You have already given feedback for this job.")
            return redirect('feedback-page')

        form = Feedbackform(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.job_id = job
            feedback.rated_user_id = job.poster # assumes your `Jobs` model has a `freelancer` FK
            feedback.rated_by_user_id = request.user
            feedback.save()
            messages.success(request, "Feedback submitted successfully!")
            return redirect('feedback-page')

    # Load feedbacks for all jobs
    job_feedback_data = []
    for job in jobs:
        job_feedback_data.append({
            'job': job,
            'feedbacks': Ratings.objects.filter(job_id=job),
            'already_given': Ratings.objects.filter(job_id=job, rated_by_user_id=request.user).exists()
        })

    return render(request, 'admin/feedback/feedback.html', {
        'job_feedback_data': job_feedback_data,
        'form': form,
    })
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
def job_completion_list(request):
    jobs=Jobs.objects.filter(freelancer=request.user)
    return render(request,"job_completion_certificate.html",{'jobs':jobs})
@login_required
def assigned_tasks(request):
    print("Current user:", request.user)
    job=Jobs.objects.filter(status='assigned',freelancer=request.user)
    return render(request,'Assigned_jobs.html',{'job':job})
@login_required
def update_job_status(request, job_id):
    job = get_object_or_404(Jobs, id=job_id)

    # Only the assigned freelancer can update
    if job.freelancer != request.user:
        messages.error(request, "You are not allowed to update this job.")
        return redirect('freelancer-dashboard')

    if request.method == 'POST':
        job.status = 'completed'
        job.save()
        messages.success(request, f"Job '{job.title}' marked as completed.")
        return redirect('freelancer-dashboard')

    return render(request, 'freelancer/Job/update_status.html', {'job': job})

@login_required
def recieve_feedback(request):
    freelancer = request.user

    # Get only jobs assigned to this freelancer
    assigned_jobs = Jobs.objects.filter(freelancer=freelancer)

    job_feedback_data = []
    for job in assigned_jobs:
        feedbacks = Ratings.objects.filter( job_id= job)
        already_given = feedbacks.exists()
        job_feedback_data.append({
            'job': job,
            'feedbacks': feedbacks,
            'already_given': already_given,
        })

    return render(request, 'freelancer/feedback and ratings/feedback.html', {
        'job_feedback_data': job_feedback_data
    })
@login_required
def upload_work_list(request):
    assigned_jobs = Jobs.objects.filter(freelancer=request.user, status='assigned')
    return render(request, 'freelancer/upload_work.html', {'assigned_jobs': assigned_jobs})
@login_required
def upload_work_action(request, job_id):
    if request.method == 'POST':
        file = request.FILES.get('completed_file')
        notes = request.POST.get('notes')
        job = Jobs.objects.get(id=job_id, freelancer=request.user)

        job.completed_file = file
        job.completion_notes = notes
        job.status = 'Completed'
        job.save()

        messages.success(request, "Work uploaded successfully.")
        return redirect('upload_completed_work')
# Create your views here.
