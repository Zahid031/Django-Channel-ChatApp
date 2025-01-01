from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Message, Group
from .forms import UserRegistrationForm
import json
from django.db import models


from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q

@login_required
def home(request):
    # Get all users except the current user
    all_users = User.objects.exclude(id=request.user.id)
    
    # Get user's groups
    user_groups = request.user.chat_groups.all()
    
    # Get existing conversations
    conversations = Message.objects.filter(
        Q(sender=request.user) | Q(receiver_user=request.user)
    ).values_list('sender', 'receiver_user').distinct()
    
    # Create a set of user IDs who have conversations
    conversation_users = set()
    for sender, receiver in conversations:
        conversation_users.add(sender)
        if receiver:  # Check if receiver is not None
            conversation_users.add(receiver)
    
    return render(request, 'chat/home.html', {
        'all_users': all_users,
        'groups': user_groups,
        'conversation_users': conversation_users
    })

@login_required
def start_chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    return redirect('chat_room', conversation_id=user_id)








def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'chat/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'chat/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def home(request):
    user_conversations = Message.objects.filter(
        receiver_user=request.user
    ).values_list('sender', flat=True).distinct()
    
    conversations = User.objects.filter(id__in=user_conversations)
    user_groups = request.user.chat_groups.all()
    
    return render(request, 'chat/home.html', {
        'conversations': conversations,
        'groups': user_groups
    })

@login_required
def chat_room(request, conversation_id):
    is_group = request.GET.get('is_group', False)
    
    if is_group:
        group = get_object_or_404(Group, id=conversation_id)
        if request.user not in group.members.all():
            messages.error(request, 'You are not a member of this group.')
            return redirect('home')
        messages_queryset = Message.objects.filter(receiver_group=group)
        room_name = group.name
    else:
        other_user = get_object_or_404(User, id=conversation_id)
        messages_queryset = Message.objects.filter(
            (models.Q(sender=request.user, receiver_user=other_user) |
             models.Q(sender=other_user, receiver_user=request.user))
        )
        room_name = other_user.username

    paginator = Paginator(messages_queryset, 10)
    page = request.GET.get('page', 1)
    messages_list = paginator.get_page(page)

    return render(request, 'chat/chat_room.html', {
        'messages': messages_list,
        'room_id': conversation_id,
        'room_name': room_name,
        'is_group': is_group
    })

@login_required
def group_list(request):
    user_groups = request.user.chat_groups.all()
    available_groups = Group.objects.exclude(members=request.user)
    return render(request, 'chat/group_list.html', {
        'user_groups': user_groups,
        'available_groups': available_groups
    })

@login_required
def create_group(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            group = Group.objects.create(name=name)
            group.members.add(request.user)
            messages.success(request, f'Group "{name}" created successfully.')
            return redirect('group_list')
    return render(request, 'chat/create_group.html')

@login_required
def join_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.user not in group.members.all():
        group.members.add(request.user)
        messages.success(request, f'You joined the group "{group.name}".')
    return redirect('group_list')

@login_required
def leave_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.user in group.members.all():
        group.members.remove(request.user)
        messages.success(request, f'You left the group "{group.name}".')
    return redirect('group_list')

@login_required
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        room_id = request.POST.get('room_id')
        is_group = request.POST.get('is_group', False)

        if is_group:
            group = get_object_or_404(Group, id=room_id)
            message = Message.objects.create(
                sender=request.user,
                receiver_group=group,
                file=file,
            )
        else:
            receiver = get_object_or_404(User, id=room_id)
            message = Message.objects.create(
                sender=request.user,
                receiver_user=receiver,
                file=file,
            )

        return JsonResponse({'file_url': message.file.url})
    return JsonResponse({'error': 'No file uploaded'}, status=400)