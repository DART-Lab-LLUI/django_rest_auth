from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from .forms import LoginForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

# Login view
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('accounts:dashboard')
            else:
                return render(request, 'accounts/login.html', {
                    'form': form,
                    'error': 'Invalid username or password',
                })
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

#Logout view
def logout_view(request):
    logout(request)
    return redirect('accounts:login')

@login_required
def dashboard_view(request):
    """
    A generic dashboard page, accessible only if the user is logged in.
    You can check roles with request.user.profile.role or user groups.
    """
    return HttpResponse(f"Hello, {request.user.username}. Your role is: {request.user.profile.role}.")


