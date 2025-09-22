

from django.contrib import admin
from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    path('jobs/search/', views.search_jobs, name='search_jobs'),
    
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('courses/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('enrollment/<int:enrollment_id>/lesson/<int:lesson_id>/complete/', views.mark_lesson_complete, name='mark_lesson_complete'),
    path('course/<int:course_id>/continue/', views.continue_learning, name='continue_learning'),
]
