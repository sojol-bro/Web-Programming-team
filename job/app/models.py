from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User

class Company(models.Model):
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Job(models.Model):
    JOB_TYPES = [
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
    ]
    
    EXPERIENCE_LEVELS = [
        ('entry', 'Entry-level'),
        ('mid', 'Mid-level'),
        ('senior', 'Senior'),
        ('top', 'Top-level'),
    ]
    
    WORK_MODES = [
        ('remote', 'Remote'),
        ('office', 'Office'),
        ('hybrid', 'Hybrid'),
    ]
    
    title = models.CharField(max_length=200)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    location = models.CharField(max_length=100)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2)
    job_type = models.CharField(max_length=20, choices=JOB_TYPES, default='full_time')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS, default='mid')
    work_mode = models.CharField(max_length=20, choices=WORK_MODES, default='office')
    description = models.TextField()
    requirements = models.TextField()
    skills_required = models.CharField(max_length=500)
    posted_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    category = models.CharField(max_length=100, default='General')
    
    def __str__(self):
        return f"{self.title} at {self.company.name}"
    
    def get_salary_range(self):
        return f"${self.salary_min}k - ${self.salary_max}k"
    
    def get_skills_list(self):
        return [skill.strip() for skill in self.skills_required.split(',')]
    
    def get_formatted_date(self):
        return self.posted_date.strftime('%d/%m/%Y')
    
class CourseCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Course(models.Model):
    DIFFICULTY_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    title = models.CharField(max_length=200)
    category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE)
    instructor = models.CharField(max_length=100)
    instructor_photo = models.ImageField(upload_to='instructors/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_weeks = models.IntegerField()
    lessons_count = models.IntegerField()
    skills_covered = models.CharField(max_length=500)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.5)
    rating_count = models.IntegerField(default=0)
    students_count = models.IntegerField(default=0)
    created_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
    
    def get_skills_list(self):
        return [skill.strip() for skill in self.skills_covered.split(',')]
    
    def get_difficulty_badge_class(self):
        if self.difficulty == 'beginner':
            return 'bg-green-200 text-green-800'
        elif self.difficulty == 'intermediate':
            return 'bg-blue-600 text-white'
        else:
            return 'bg-purple-200 text-purple-800'
    
    def get_background_class(self):
        colors = ['bg-blue-200', 'bg-blue-300', 'bg-blue-400', 'bg-green-200', 'bg-blue-100']
        index = self.id % len(colors) if self.id else 0
        return colors[index]

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    description = models.TextField()
    video_url = models.URLField(blank=True, null=True)
    duration_minutes = models.IntegerField()
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_date = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    last_accessed = models.DateTimeField(default=timezone.now)  # Changed from auto_now=True
    
    class Meta:
        unique_together = ['user', 'course']
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title}"
    
    def save(self, *args, **kwargs):
        # Update last_accessed when saving
        if not self.pk:  # New enrollment
            self.last_accessed = timezone.now()
        super().save(*args, **kwargs)
    
    def get_progress_percentage(self):
        """Calculate progress percentage based on completed lessons"""
        try:
            completed_lessons = LessonCompletion.objects.filter(
                enrollment=self, 
                completed=True
            ).count()
            total_lessons = self.course.lessons.count()
            if total_lessons == 0:
                return 0
            return int((completed_lessons / total_lessons) * 100)
        except:
            return 0
    
    def get_completed_lessons_count(self):
        try:
            return LessonCompletion.objects.filter(enrollment=self, completed=True).count()
        except:
            return 0
    
    def get_next_lesson(self):
        """Get the next uncompleted lesson"""
        try:
            completed_lessons = LessonCompletion.objects.filter(
                enrollment=self, 
                completed=True
            ).values_list('lesson_id', flat=True)
            
            next_lesson = self.course.lessons.exclude(id__in=completed_lessons).first()
            return next_lesson
        except:
            return None

class LessonCompletion(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_date = models.DateTimeField(null=True, blank=True)
    time_spent_minutes = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['enrollment', 'lesson']
    
    def __str__(self):
        status = "Completed" if self.completed else "In Progress"
        return f"{self.enrollment.user.username} - {self.lesson.title} ({status})"