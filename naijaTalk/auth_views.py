from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignUpForm
from django.contrib.auth import login, authenticate, logout

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')  # Redirect to home if already logged in

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log in after sign-up

            # Send a welcome email
           # send_mail(
           #     'Welcome to Our Website',
             #   'Thank you for signing up! We are happy to have you.',
             #   settings.EMAIL_HOST_USER,  # From email
            #    [user.email],  # To email
             #   fail_silently=False,
            #)

            return redirect('home')  # Change to your home view
    else:
        form = SignUpForm()
    
    return render(request, 'auth/sign_up.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')  # Redirect to home if already logged in

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Send a login notification email
          
            return redirect('home')  # Redirect to the home view
        else:
            messages.error(request, 'Invalid credentials')  # Show error message
    else:
        form = AuthenticationForm()
    
    return render(request, 'auth/login.html', {'form': form})
def logout_view(request):
    logout(request)
    return redirect('login') 