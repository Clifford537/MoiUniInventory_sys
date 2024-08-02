from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! click the login button to continue.')
            request.session['user_logged_in'] = True  # Set session variable
            return redirect('register')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful!')
                request.session['user_logged_in'] = True  # Set session variable
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def dashboard_view(request):
    return render(request, 'dashboard.html')

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    request.session['user_logged_in'] = False  # Clear session variable
    return redirect('login')

@login_required
def check_login_status(request):
    is_logged_in = request.user.is_authenticated
    return JsonResponse({'logged_in': is_logged_in})

def require_login_message_middleware(get_response):
    def middleware(request):
        response = get_response(request)
        if not request.user.is_authenticated and request.path != '/login/':
            messages.warning(request, 'You are not logged in.')
            return redirect('login')
        return response
    return middleware