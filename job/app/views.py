from django.http import FileResponse
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Choice, Job, Course, Company, CourseCategory,Course, CourseCategory, Enrollment,LessonCompletion,Lesson, Question, Quiz, QuizAttempt, UserAnswer
from .models import UserProfile, Experience, Education, Skill, Project, Language, Certificate



def home(request):

    featured_jobs = Job.objects.filter(is_active=True).order_by('-posted_date')[:3]
    
    popular_courses = Course.objects.filter(is_active=True).order_by('-created_date')[:3]
    
    context = {
        'featured_jobs': featured_jobs,
        'popular_courses': popular_courses,
    }
    return render(request, 'welcome.html', context)

def job_list(request):
    jobs = Job.objects.filter(is_active=True).order_by('-posted_date')
    
    # Get filter parameters
    location_filter = request.GET.get('location', '')
    job_type_filter = request.GET.get('job_type', '')
    experience_filter = request.GET.get('experience', '')
    search_query = request.GET.get('q', '')
    
    # Apply filters
    if search_query:
        jobs = jobs.filter(title__icontains=search_query)
    
    if location_filter:
        if location_filter == 'remote':
            jobs = jobs.filter(work_mode='remote')
        else:
            jobs = jobs.filter(location__icontains=location_filter)
    
    if job_type_filter:
        jobs = jobs.filter(job_type=job_type_filter)
    
    if experience_filter:
        jobs = jobs.filter(experience_level=experience_filter)
    
    # Get unique values for filter dropdowns
    locations = Job.objects.filter(is_active=True).values_list('location', flat=True).distinct()
    job_types = Job.JOB_TYPES
    experience_levels = Job.EXPERIENCE_LEVELS
    
    context = {
        'jobs': jobs,
        'locations': locations,
        'job_types': job_types,
        'experience_levels': experience_levels,
        'selected_location': location_filter,
        'selected_job_type': job_type_filter,
        'selected_experience': experience_filter,
        'search_query': search_query,
    }
    return render(request, 'jobs/job_list.html', context)

def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id, is_active=True)
    context = {
        'job': job,
    }
    return render(request, 'jobs/job_detail.html', context)



def course_list(request):
    courses = Course.objects.filter(is_active=True).order_by('-created_date')
    categories = CourseCategory.objects.all()
    
    context = {
        'courses': courses,
        'categories': categories,
    }
    return render(request, 'courses/course_list.html', context)

def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id, is_active=True)
    context = {
        'course': course,
    }
    return render(request, 'courses/course_detail.html', context)

def search_jobs(request):
    query = request.GET.get('q', '')
    location = request.GET.get('location', '')
    
    jobs = Job.objects.filter(is_active=True)
    
    if query:
        jobs = jobs.filter(title__icontains=query)
    
    if location:
        jobs = jobs.filter(location__icontains=location)
    
    context = {
        'jobs': jobs,
        'query': query,
        'location': location,
    }
    return render(request, 'jobs/job_search.html', context)


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')



def course_list(request):
    # Determine active tab
    tab = request.GET.get('tab', 'all')
    
    # For "All Courses" tab
    if tab == 'all':
        courses = Course.objects.filter(is_active=True).order_by('-created_date')
        
        # Get filter parameters
        category_filter = request.GET.get('category', '')
        difficulty_filter = request.GET.get('difficulty', '')
        price_filter = request.GET.get('price', '')
        search_query = request.GET.get('q', '')
        
        # Apply filters
        if search_query:
            courses = courses.filter(
                Q(title__icontains=search_query) |
                Q(instructor__icontains=search_query) |
                Q(skills_covered__icontains=search_query)
            )
        
        if category_filter:
            courses = courses.filter(category__name=category_filter)
        
        if difficulty_filter:
            courses = courses.filter(difficulty=difficulty_filter)
        
        if price_filter:
            if price_filter == 'free':
                courses = courses.filter(price=0)
            elif price_filter == 'under_1000':
                courses = courses.filter(price__lt=1000)
            elif price_filter == 'over_1000':
                courses = courses.filter(price__gte=1000)
        
        # Get unique values for filter dropdowns
        categories = CourseCategory.objects.all()
        difficulty_levels = Course.DIFFICULTY_LEVELS
        
        context = {
            'courses': courses,
            'categories': categories,
            'difficulty_levels': difficulty_levels,
            'selected_category': category_filter,
            'selected_difficulty': difficulty_filter,
            'selected_price': price_filter,
            'search_query': search_query,
            'active_tab': tab,
            'show_filters': True,  # Show filters for "All Courses"
        }
    
    # For "My Courses" tab
    elif tab == 'my_courses' and request.user.is_authenticated:
        enrollments = Enrollment.objects.filter(user=request.user).select_related('course')
        
        # Calculate progress for each enrollment
        courses_with_progress = []
        total_lessons_completed = 0
        completed_courses_count = 0
        
        for enrollment in enrollments:
            progress_percentage = enrollment.get_progress_percentage()
            completed_lessons = enrollment.get_completed_lessons_count()
            total_lessons = enrollment.course.lessons.count()
            
            total_lessons_completed += completed_lessons
            
            if progress_percentage == 100:
                completed_courses_count += 1
            
            courses_with_progress.append({
                'enrollment': enrollment,
                'course': enrollment.course,
                'progress_percentage': progress_percentage,
                'completed_lessons': completed_lessons,
                'total_lessons': total_lessons,
                'next_lesson': enrollment.get_next_lesson(),
            })
        
        # Get suggested courses (excluding already enrolled ones)
        enrolled_course_ids = enrollments.values_list('course_id', flat=True)
        suggested_courses = Course.objects.filter(is_active=True).exclude(
            id__in=enrolled_course_ids
        )[:4]
        
        context = {
            'courses_with_progress': courses_with_progress,
            'suggested_courses': suggested_courses,
            'total_lessons_completed': total_lessons_completed,
            'completed_courses_count': completed_courses_count,
            'active_tab': tab,
            'show_filters': False,  # Hide filters for "My Courses"
        }
    
    else:
        # Default to "All Courses" if not authenticated or invalid tab
        return redirect('app:course_list?tab=all')
    
    return render(request, 'courses/course_list.html', context)

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id, is_active=True)
    enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
    lessons = course.lessons.all().order_by('order')
    
    # Get completion status for each lesson
    lessons_with_completion = []
    for lesson in lessons:
        completion = None
        if enrollment:
            completion = LessonCompletion.objects.filter(
                enrollment=enrollment, 
                lesson=lesson
            ).first()
        
        lessons_with_completion.append({
            'lesson': lesson,
            'completion': completion,
        })
    
    # Calculate progress percentage
    progress_percentage = enrollment.get_progress_percentage() if enrollment else 0
    
    # Get related courses (same category, excluding current course)
    related_courses = Course.objects.filter(
        category=course.category, 
        is_active=True
    ).exclude(id=course.id)[:3]
    
    # Count instructor's courses
    instructor_courses_count = Course.objects.filter(
        instructor=course.instructor, 
        is_active=True
    ).count()
    
    context = {
        'course': course,
        'enrollment': enrollment,
        'lessons_with_completion': lessons_with_completion,
        'progress_percentage': progress_percentage,
        'related_courses': related_courses,
        'instructor_courses_count': instructor_courses_count,
    }
    return render(request, 'courses/course_detail.html', context)

@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, is_active=True)
    
    # Check if already enrolled
    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        course=course
    )
    
    if created:
        messages.success(request, f'Successfully enrolled in {course.title}!')
    else:
        messages.info(request, f'You are already enrolled in {course.title}')
    
    return redirect('app:course_detail', course_id=course_id)

@login_required
def my_courses(request):
    enrollments = Enrollment.objects.filter(user=request.user).select_related('course')
    
    # Calculate progress for each enrollment
    courses_with_progress = []
    for enrollment in enrollments:
        progress_percentage = enrollment.get_progress_percentage()
        completed_lessons = enrollment.get_completed_lessons_count()
        total_lessons = enrollment.course.lessons.count()
        
        courses_with_progress.append({
            'enrollment': enrollment,
            'course': enrollment.course,
            'progress_percentage': progress_percentage,
            'completed_lessons': completed_lessons,
            'total_lessons': total_lessons,
            'next_lesson': enrollment.get_next_lesson(),
        })
    
    context = {
        'courses_with_progress': courses_with_progress,
        'active_tab': 'my_courses',
    }
    return render(request, 'courses/my_courses.html', context)

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id, is_active=True)
    enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
    lessons = course.lessons.all()
    
    # Get completion status for each lesson
    lessons_with_completion = []
    for lesson in lessons:
        completion = None
        if enrollment:
            completion = LessonCompletion.objects.filter(
                enrollment=enrollment, 
                lesson=lesson
            ).first()
        
        lessons_with_completion.append({
            'lesson': lesson,
            'completion': completion,
        })
    
    context = {
        'course': course,
        'enrollment': enrollment,
        'lessons_with_completion': lessons_with_completion,
        'progress_percentage': enrollment.get_progress_percentage() if enrollment else 0,
    }
    return render(request, 'courses/course_detail.html', context)

@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, is_active=True)
    
    # Check if already enrolled
    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        course=course
    )
    
    if created:
        # Create lesson completion records for all lessons
        lessons = course.lessons.all()
        for lesson in lessons:
            LessonCompletion.objects.create(
                enrollment=enrollment,
                lesson=lesson,
                completed=False
            )
        messages.success(request, f'Successfully enrolled in {course.title}!')
    else:
        messages.info(request, f'You are already enrolled in {course.title}')
    
    return redirect('app:course_detail', course_id=course_id)

@login_required
def mark_lesson_complete(request, enrollment_id, lesson_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, user=request.user)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=enrollment.course)
    
    completion, created = LessonCompletion.objects.get_or_create(
        enrollment=enrollment,
        lesson=lesson
    )
    
    if not completion.completed:
        completion.completed = True
        completion.completed_date = timezone.now()
        completion.save()
        messages.success(request, f'Lesson "{lesson.title}" marked as completed!')
    else:
        messages.info(request, f'Lesson "{lesson.title}" was already completed')
    
    return redirect('app:course_detail', course_id=enrollment.course.id)

@login_required
def continue_learning(request, course_id):
    course = get_object_or_404(Course, id=course_id, is_active=True)
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
    
    next_lesson = enrollment.get_next_lesson()
    if next_lesson:
        return redirect('app:lesson_detail', course_id=course_id, lesson_id=next_lesson.id)
    else:
        messages.success(request, 'Congratulations! You have completed this course!')
        return redirect('app:course_detail', course_id=course_id)
    

def about_view(request):
    return render(request, 'jobs/about.html')



def quiz_list(request):
    quizzes = Quiz.objects.filter(is_active=True).order_by('-created_date')
    
    context = {
        'quizzes': quizzes,
    }
    return render(request, 'quizzes/quiz_list.html', context)

def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
    questions = quiz.questions.all().prefetch_related('choices')
    
    # Check if user has already attempted this quiz
    previous_attempt = None
    if request.user.is_authenticated:
        previous_attempt = QuizAttempt.objects.filter(
            user=request.user, 
            quiz=quiz
        ).first()
    
    context = {
        'quiz': quiz,
        'questions': questions,
        'previous_attempt': previous_attempt,
    }
    return render(request, 'quizzes/quiz_detail.html', context)

@login_required
def start_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
    
    # Check if user has already attempted this quiz
    existing_attempt = QuizAttempt.objects.filter(
        user=request.user, 
        quiz=quiz
    ).first()
    
    if existing_attempt and existing_attempt.score > 40:
        messages.info(request, f'You have already attempted this quiz. Your score: {existing_attempt.score}%')
        return redirect('app:quiz_result', attempt_id=existing_attempt.id)

    if existing_attempt :
        existing_attempt.delete()
    
    # Create new quiz attempt
    attempt = QuizAttempt.objects.create(
        user=request.user,
        quiz=quiz
    )
    
    return redirect('app:take_quiz', attempt_id=attempt.id)

@login_required
def take_quiz(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    
    if attempt.completed_at:
        messages.info(request, 'This quiz has already been completed.')
        return redirect('app:quiz_result', attempt_id=attempt.id)
    
    # Get unanswered questions
    answered_question_ids = attempt.user_answers.values_list('question_id', flat=True)
    current_question = attempt.quiz.questions.exclude(id__in=answered_question_ids).first()
    
    if not current_question:
        # All questions answered, calculate score
        return calculate_quiz_score(attempt)
    
    if request.method == 'POST':
        # Process the answer
        question_id = request.POST.get('question_id')
        question = get_object_or_404(Question, id=question_id, quiz=attempt.quiz)
        
        if question.question_type == 'multiple_choice':
            choice_id = request.POST.get('choice_id')
            if choice_id:
                selected_choice = get_object_or_404(Choice, id=choice_id, question=question)
                is_correct = selected_choice.is_correct
                
                UserAnswer.objects.create(
                    attempt=attempt,
                    question=question,
                    selected_choice=selected_choice,
                    is_correct=is_correct
                )
        elif question.question_type == 'true_false':
            answer = request.POST.get('answer') == 'true'
            # For true/false, we need to know the correct answer
            # This is a simplified version - you'd need to store correct answers differently
            pass
        
        # Get next question or finish quiz
        next_question = attempt.quiz.questions.exclude(
            id__in=attempt.user_answers.values_list('question_id', flat=True)
        ).first()
        
        if next_question:
            current_question = next_question
        else:
            return calculate_quiz_score(attempt)
    
    context = {
        'attempt': attempt,
        'current_question': current_question,
    }
    return render(request, 'quizzes/take_quiz.html', context)

def calculate_quiz_score(attempt):
    total_questions = attempt.quiz.questions.count()
    correct_answers = attempt.user_answers.filter(is_correct=True).count()
    
    if total_questions > 0:
        score = (correct_answers / total_questions) * 100
    else:
        score = 0
    
    attempt.score = score
    attempt.passed = score >= attempt.quiz.passing_score
    attempt.completed_at = timezone.now()
    attempt.save()
    
    # Update quiz statistics
    attempt.quiz.attempts_count += 1
    attempt.quiz.save()
    
    return redirect('app:quiz_result', attempt_id=attempt.id)

@login_required
def quiz_result(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    
    if not attempt.completed_at:
        messages.error(request, 'Quiz not completed yet.')
        return redirect('app:take_quiz', attempt_id=attempt.id)
    
    for ua in attempt.user_answers.all():
        ua.correct_choices = ua.question.choices.filter(is_correct=True)

    context = {
        'attempt': attempt,
        'correct_answers': attempt.user_answers.filter(is_correct=True).count(),
        'total_questions': attempt.quiz.questions.count(),
    }
    return render(request, 'quizzes/quiz_result.html', context)




@login_required
def profile(request, username=None):
    # If no username provided, show current user's profile
    if username:
        profile_user = get_object_or_404(User, username=username)
    else:
        profile_user = request.user
    
    # Get active tab
    active_tab = request.GET.get('tab', 'overview')
    
    # Get profile data
    profile, created = UserProfile.objects.get_or_create(user=profile_user)
    experiences = Experience.objects.filter(user=profile_user).order_by('-start_date')
    educations = Education.objects.filter(user=profile_user).order_by('-start_date')
    skills = Skill.objects.filter(user=profile_user).order_by('-percentage')
    projects = Project.objects.filter(user=profile_user).order_by('-start_date')
    languages = Language.objects.filter(user=profile_user)
    certificates = Certificate.objects.filter(user=profile_user).order_by('-issue_date')
    
    context = {
        'profile_user': profile_user,
        'profile': profile,
        'experiences': experiences,
        'educations': educations,
        'skills': skills,
        'projects': projects,
        'languages': languages,
        'certificates': certificates,
        'active_tab': active_tab,
        'is_own_profile': profile_user == request.user,
    }
    return render(request, 'profile/profile.html', context)

@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        
        # Update other fields
        profile.bio = request.POST.get('bio', '')
        profile.title = request.POST.get('title', '')
        profile.location = request.POST.get('location', '')
        profile.phone = request.POST.get('phone', '')
        profile.website = request.POST.get('website', '')
        profile.linkedin = request.POST.get('linkedin', '')
        profile.github = request.POST.get('github', '')
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('app:profile')
    
    context = {
        'profile': profile,
    }
    return render(request, 'profile/edit_profile.html', context)

@login_required
def download_cv(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    if profile.resume:
        response = FileResponse(profile.resume, as_attachment=True)
        return response
    else:
        messages.error(request, 'No resume uploaded yet.')
        return redirect('app:profile')