from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User

# Create your views here.
def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect("/chat/")  # লগইন সফল হলে চ্যাট পেজে নিয়ে যাবে
        else:
            messages.error(request, "Invalid username or password")
    
    return render(request, "login.html")


def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect("signup")

        user = User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Account created successfully. You can now log in.")
        return redirect("login")

    return render(request, "signup.html")

def logout_view(request):
    logout(request)
    return redirect('login')



