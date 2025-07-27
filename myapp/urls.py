"""
URL configuration for myapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app.views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/',signup_view,name="signup"),
    path('', home,name="home"),
    path('login/', user_login, name='login'), # login
    path('logout/', custom_logout, name='logout'),
    # admin
    path('admin-dashboard/',Admin_dashboard,name="admin-dashboard"),  # admin-dashboard
    #post job
    path('job_post/',job_posting,name="job_post"),  # post a job 
    path('job_list/',job_list,name="job_list"),    #  job listing
    path('jobs/edit/<int:job_id>/', edit_job, name='edit-job'),
    path('jobs/delete/<int:job_id>/', delete_job, name='delete-job'),
    path('job-bid/<int:job_id>/', Place_bid, name='job_bid'),   # job bidding 
    path('my-bid/',all_bids,name="my_bid"),  # my bids
    # path('feedback-rating/',feeback_list_view,name="feedback_rating"),  # Feedback
    # path('submit-feeback/<int:job_id>/',Feedback_rating,name='submit_feedback'),
    # # submit Feedback
    path("feedbacks/",all_job_feedback_view, name="feedback-page"),
    path('view-bids/', view_bids, name="view_bids"), # view bids
    path('accept-bid/<int:job_id>/',accept_bid,name="accept_bid"),   # accept bid
    path('accepted-bids/',accepted_bids,name="accepted_bids"),     # Accepted Bid
    # path('milestone/<int:job_id>/',add_milestone,name="milestone"),  # milestone Tracking
    # path('accept-milestone/',accept_milestone,name="accept_milestone"), # accept milestone
    # path('accepted-milestone/',accepted_milestone,name="accepted_milestone"), # accepted milestone
    #freelancer
    path('freelancer-dashboard/',freelancer_dashboard,name='freelancer-dashboard'),
    path("chat/<int:job_id>/", chat_page, name="chat"), 
    path('certificate/<int:job_id>/', job_completion_certificate, name='job_certificate'),
    path('certificate-list/',job_completion_list,name="certificate_list"),

]

