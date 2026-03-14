from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.http import HttpResponseNotAllowed

from .models import Email
from .forms import ComposeEmailForm

import uuid


def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('inbox', username=request.user.username)
    return redirect('login')


def logout_view(request):
    if request.method == 'POST':
        auth_logout(request)
        response = redirect('login')
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
    return HttpResponseNotAllowed(['POST'])


@login_required
def inbox(request, username):
    if username != request.user.username:
        return redirect('inbox', username=request.user.username)

    emails = Email.objects.filter(recipient=request.user, folder='inbox')
    return render(request, 'email/inbox.html', {
        'emails': emails,
        'username': username
    })


@login_required
def email_list(request, username, folder):
    if username != request.user.username:
        return redirect('inbox', username=request.user.username)

    folders = ['inbox', 'sent', 'drafts', 'trash']
    if folder not in folders:
        return redirect('inbox', username=username)

    if folder == 'sent':
        emails = Email.objects.filter(sender=request.user, folder=folder)
    else:
        emails = Email.objects.filter(recipient=request.user, folder=folder)

    return render(request, 'email/list.html', {
        'emails': emails,
        'folder': folder,
        'username': username
    })


@login_required
def email_detail(request, username, email_slug):
    if username != request.user.username:
        return redirect('inbox', username=request.user.username)

    email_item = get_object_or_404(Email, slug=email_slug)

    if email_item.recipient != request.user and email_item.sender != request.user:
        messages.error(request, "Доступ запрещён.")
        return redirect('inbox', username=username)

    if email_item.recipient == request.user and not email_item.read:
        email_item.read = True
        email_item.save()

    return render(request, 'email/detail.html', {
        'email': email_item,
        'username': username
    })


@login_required
def compose_email(request, username):
    if username != request.user.username:
        return redirect('inbox', username=request.user.username)

    if request.method == 'POST':
        form = ComposeEmailForm(request.POST)
        if form.is_valid():
            recipient = form.cleaned_data['recipient']
            subject = form.cleaned_data['subject']
            body = form.cleaned_data['body']
            email_slug = str(uuid.uuid4())

            # Сохраняем письмо в папку "sent" для отправителя
            sent_email = Email.objects.create(
                sender=request.user,
                recipient=recipient,
                subject=subject,
                body=body,
                slug=email_slug,
                folder='sent'
            )

            # Добавляем копию письма в папку "inbox" получателя
            Email.objects.create(
                sender=request.user,
                recipient=recipient,
                subject=subject,
                body=body,
                slug=str(uuid.uuid4()),  # уникальный slug для копии
                folder='inbox',
                read=False
            )

            messages.success(request, f"Письмо успешно отправлено пользователю {recipient.username}")
            return redirect('email_list', username=username, folder='sent')
    else:
        form = ComposeEmailForm()

    return render(request, 'email/compose.html', {
        'form': form,
        'username': username
    })


@login_required
def move_email(request, email_slug, username):
    email = get_object_or_404(Email, slug=email_slug)

    # Проверка доступа
    if email.sender != request.user and email.recipient != request.user:
        messages.error(request, "Доступ запрещён.")
        return redirect('inbox', username=request.user.username)

    if request.method == "POST":
        folder = request.POST.get("folder")
        valid_folders = ["inbox", "drafts", "trash"]
        if folder in valid_folders:
            email.folder = folder
            email.save()
            messages.success(request, f"Письмо перемещено в папку «{folder}».")

    # ✅ Передаём оба параметра: username и email_slug
    return redirect('email_detail', username=request.user.username, email_slug=email.slug)