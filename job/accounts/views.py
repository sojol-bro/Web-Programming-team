from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.shortcuts import render, redirect

from .models import CustomUser

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        user_type = request.POST.get('user_type')
        
        # Validate required fields
        if not username or not email or not password or not confirm_password or not user_type:
            messages.error(request, 'All fields are required.')
            return render(request, 'auth/signup.html')
            
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'auth/signup.html')
            
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'auth/signup.html')
            
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'auth/signup.html')
        
        # Validate user type
        valid_user_types = ['user', 'employee', 'admin']
        if user_type not in valid_user_types:
            messages.error(request, 'Invalid user type selected.')
            return render(request, 'auth/signup.html')
        
        try:
            # Create user
            user = User.objects.create_user(username=username, email=email, password=password)
            
            # Create user profile
            CustomUser.objects.create(user=user, user_type=user_type)
            
            # Set staff status for admins
            if user_type == 'admin':
                user.is_staff = True
                user.save()
            
            login(request, user)
            messages.success(request, f'Account created successfully! Welcome, {username}.')
            if user_type == 'admin':
                messages.success(request, 'Welcome back, Administrator!')
                return redirect('admin_dashboard')
            elif user_type == 'employee':
                messages.success(request, 'Welcome back, Employee!')
                return redirect('employee_view')
            else:
                messages.success(request, 'Welcome back!')
                return redirect('home')
            
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
    
    return render(request, 'auth/signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Get user profile to check user type
            try:
                user_profile = CustomUser.objects.get(user=user)
                user_type = user_profile.user_type
            except CustomUser.DoesNotExist:
                # Fallback if profile doesn't exist
                user_type = 'user'
            
            # Redirect based on user type
            if user_type == 'admin':
                messages.success(request, 'Welcome back, Administrator!')
                return redirect('admin_dashboard')
            elif user_type == 'employee':
                messages.success(request, 'Welcome back, Employee!')
                return redirect('employee_view')
            else:
                messages.success(request, 'Welcome back!')
                return redirect('home')
                
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'auth/login.html')


def employee_view(request):
    return render(request, 'employee/dashboard.html')
