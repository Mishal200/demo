from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Message
from django.db.models import Q
from accounts.models import UserProfile


@login_required
def home(request):

    users = UserProfile.objects.exclude(
        user=request.user
    )

    return render(request, "home.html", {
        "users": users
    })

@login_required
def chat_room(request, user_id):

    receiver = get_object_or_404(User, id=user_id)

    room_name = "_".join(
        map(
            str,
            sorted([request.user.id, receiver.id])
        )
    )

    messages = Message.objects.filter(
        Q(sender=request.user, receiver=receiver) |
        Q(sender=receiver, receiver=request.user)
    ).order_by("timestamp")

    users = User.objects.exclude(id=request.user.id)

    return render(request, "home.html", {
        "users": users,
        "receiver": receiver,
        "messages": messages,
        "room_name": room_name,
    })