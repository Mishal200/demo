from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from accounts.models import UserProfile


def register(request):
    if request.method == "POST":

        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        UserProfile.objects.get_or_create(user=user)

        messages.success(request, "Account created successfully")
        return redirect("login")

    return render(request, "register.html")


def user_login(request):

    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(
            username=username,
            password=password
        )

        if user:

            profile, created = UserProfile.objects.get_or_create(
                user=user
            )

            profile.is_online = True
            profile.save()

            login(request, user)

            return redirect("home")

        messages.error(request, "Invalid username or password")

    return render(request, "login.html")


def user_logout(request):

    if request.user.is_authenticated:

        profile, created = UserProfile.objects.get_or_create(
            user=request.user
        )

        profile.is_online = False
        profile.save()

    logout(request)

    return redirect("login")