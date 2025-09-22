from django.contrib import admin
from .models import Company, Job, CourseCategory, Course, Enrollment

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'location', 'experience_level', 'work_mode', 'job_type', 'salary_min', 'salary_max', 'posted_date', 'is_active']
    list_filter = ['job_type', 'experience_level', 'work_mode', 'is_active', 'posted_date']
    search_fields = ['title', 'company__name', 'location', 'skills_required']
    list_editable = ['is_active']

@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'instructor', 'price', 'difficulty', 'rating', 'students_count', 'is_active']
    list_filter = ['category', 'difficulty', 'is_active', 'created_date']
    search_fields = ['title', 'instructor', 'skills_covered']
    list_editable = ['is_active', 'price']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'enrolled_date', 'completed']
    list_filter = ['completed', 'enrolled_date']
    search_fields = ['user__username', 'course__title']