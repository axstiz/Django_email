import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout as auth_logout, login
from django.http import HttpResponseNotAllowed
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

from .models import Email
from .forms import ComposeEmailForm, RegistrationForm


def root_redirect(request):
    """Перенаправление с корня сайта."""
    if request.user.is_authenticated:
        return redirect('inbox', username=request.user.username)
    return redirect('login')


def logout_view(request):
    """Выход из системы."""
    if request.method == 'POST':
        auth_logout(request)
        response = redirect('login')
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
    return HttpResponseNotAllowed(['POST'])


def register_view(request):
    """Регистрация нового пользователя."""
    if request.user.is_authenticated:
        return redirect('inbox', username=request.user.username)
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Добро пожаловать, {user.username}! Вы успешно зарегистрированы.")
            return redirect('inbox', username=user.username)
    else:
        form = RegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})


@login_required
def inbox(request, username):
    """Страница входящих писем."""
    if username != request.user.username:
        return redirect('inbox', username=request.user.username)

    emails = Email.objects.filter(recipient=request.user, folder='inbox')
    
    # Поиск
    query = request.GET.get('q')
    if query:
        emails = emails.filter(
            Q(subject__icontains=query) |
            Q(body__icontains=query) |
            Q(sender__username__icontains=query)
        )
        messages.info(request, f"Найдено писем по запросу '{query}': {emails.count()}")
    
    # Пагинация
    paginator = Paginator(emails, 10)
    page = request.GET.get('page')
    try:
        emails_page = paginator.page(page)
    except PageNotAnInteger:
        emails_page = paginator.page(1)
    except EmptyPage:
        emails_page = paginator.page(paginator.num_pages)
    
    return render(request, 'email/inbox.html', {
        'emails': emails_page,
        'username': username,
        'page_obj': emails_page,
        'query': query
    })


@login_required
def email_list(request, username, folder):
    """Список писем в указанной папке."""
    if username != request.user.username:
        return redirect('inbox', username=request.user.username)

    folders = ['inbox', 'sent', 'drafts', 'trash']
    if folder not in folders:
        messages.error(request, f"Папка '{folder}' не найдена.")
        return redirect('inbox', username=username)

    # Для разных папок — разные фильтры
    if folder == 'sent':
        # Отправленные — только sender
        emails = Email.objects.filter(sender=request.user, folder=folder)
    elif folder == 'drafts':
        # Черновики — только sender
        emails = Email.objects.filter(sender=request.user, folder=folder)
    elif folder == 'trash':
        # Корзина — и sender, и recipient
        emails = Email.objects.filter(
            Q(sender=request.user, folder=folder) |
            Q(recipient=request.user, folder=folder)
        )
    else:
        # Входящие и остальные — recipient
        emails = Email.objects.filter(recipient=request.user, folder=folder)
    
    # Поиск
    query = request.GET.get('q')
    if query:
        if folder == 'sent':
            emails = emails.filter(
                Q(subject__icontains=query) |
                Q(body__icontains=query) |
                Q(recipient__username__icontains=query)
            )
        else:
            emails = emails.filter(
                Q(subject__icontains=query) |
                Q(body__icontains=query) |
                Q(sender__username__icontains=query)
            )
    
    # Пагинация
    paginator = Paginator(emails, 10)
    page = request.GET.get('page')
    try:
        emails_page = paginator.page(page)
    except PageNotAnInteger:
        emails_page = paginator.page(1)
    except EmptyPage:
        emails_page = paginator.page(paginator.num_pages)
    
    return render(request, 'email/list.html', {
        'emails': emails_page,
        'folder': folder,
        'folder_name': dict(Email.FOLDER_CHOICES).get(folder, folder),
        'username': username,
        'page_obj': emails_page,
        'query': query
    })


@login_required
def email_detail(request, username, email_slug):
    """Просмотр отдельного письма."""
    if username != request.user.username:
        return redirect('inbox', username=request.user.username)

    email_item = get_object_or_404(Email, slug=email_slug)

    if email_item.recipient != request.user and email_item.sender != request.user:
        messages.error(request, "Доступ запрещён.")
        return redirect('inbox', username=username)

    # Отмечаем как прочитанное ТОЛЬКО если:
    # 1. Письмо во входящих (folder='inbox')
    # 2. Просматривает получатель
    # 3. Письмо ещё не прочитано
    if email_item.folder == 'inbox' and email_item.recipient == request.user and not email_item.read:
        email_item.mark_as_read()

    return render(request, 'email/detail.html', {
        'email': email_item,
        'username': username
    })


@login_required
def compose_email(request, username):
    """Написание и отправка письма, либо сохранение в черновики."""
    if username != request.user.username:
        return redirect('inbox', username=request.user.username)

    if request.method == 'POST':
        form = ComposeEmailForm(request.POST)
        form.context = {'user': request.user}
        
        # Определяем действие: отправка или сохранение в черновики
        save_as_draft = 'save_draft' in request.POST
        
        if form.is_valid():
            recipient = form.cleaned_data['recipient']
            subject = form.cleaned_data['subject']
            body = form.cleaned_data['body']

            if save_as_draft:
                # Сохраняем только в черновики (одна запись)
                Email.objects.create(
                    sender=request.user,
                    recipient=recipient,
                    subject=subject,
                    body=body,
                    folder='drafts',
                    read=True
                )
                messages.success(request, "Письмо сохранено в черновиках.")
                return redirect('email_list', username=username, folder='drafts')
            else:
                # Отправляем письмо (две записи: для получателя и отправителя)
                Email.send_email(
                    sender=request.user,
                    recipient=recipient,
                    subject=subject,
                    body=body
                )
                messages.success(request, f"Письмо успешно отправлено пользователю {recipient.username}")
                return redirect('email_list', username=username, folder='sent')
    else:
        form = ComposeEmailForm()
        form.context = {'user': request.user}

    return render(request, 'email/compose.html', {
        'form': form,
        'username': username
    })


@login_required
def move_email(request, email_slug, username):
    """Перемещение письма в другую папку."""
    email = get_object_or_404(Email, slug=email_slug)

    # Проверка доступа
    if email.sender != request.user and email.recipient != request.user:
        messages.error(request, "Доступ запрещён.")
        return redirect('inbox', username=request.user.username)

    if request.method == "POST":
        folder = request.POST.get("folder")
        
        # Проверка: получатель не может переместить письмо в черновики
        if email.recipient == request.user and folder == 'drafts':
            messages.error(request, "Нельзя переместить письмо в черновики.")
            return redirect('email_detail', username=username, email_slug=email.slug)
        
        # Проверка: допустимые папки для перемещения
        valid_folders = ["inbox", "drafts", "trash", "sent"]
        if folder in valid_folders:
            # Отправитель может перемещать только в sent или trash
            if email.sender == request.user and folder not in ['sent', 'trash']:
                messages.error(request, "Отправитель может перемещать письмо только в 'Отправленные' или 'Корзина'.")
                return redirect('email_detail', username=username, email_slug=email.slug)
            
            # Получатель может перемещать только в inbox или trash
            if email.recipient == request.user and folder not in ['inbox', 'trash']:
                messages.error(request, "Получатель может перемещать письмо только в 'Входящие' или 'Корзина'.")
                return redirect('email_detail', username=username, email_slug=email.slug)
            
            email.folder = folder
            email.save()
            messages.success(request, f"Письмо перемещено в папку «{folder}».")

    return redirect('email_detail', username=request.user.username, email_slug=email.slug)


@login_required
def delete_email(request, email_slug, username):
    """
    Удаление письма.
    - Если письмо в корзине — удаляем навсегда
    - Если письмо не в корзине — перемещаем в корзину
    """
    email = get_object_or_404(Email, slug=email_slug)

    if email.sender != request.user and email.recipient != request.user:
        messages.error(request, "Доступ запрещён.")
        return redirect('inbox', username=request.user.username)

    if email.folder == 'trash':
        # Письмо уже в корзине — удаляем навсегда
        email.delete()
        messages.success(request, "Письмо удалено навсегда.")
    else:
        # Письмо не в корзине — перемещаем в корзину
        email.move_to_folder('trash')
        messages.success(request, "Письмо перемещено в корзину.")

    return redirect('inbox', username=request.user.username)


@login_required
def edit_draft(request, email_slug, username):
    """Редактирование черновика."""
    if username != request.user.username:
        return redirect('inbox', username=request.user.username)

    email_item = get_object_or_404(Email, slug=email_slug)

    # Проверка: это должен быть черновик и принадлежать текущему пользователю
    if email_item.folder != 'drafts' or email_item.sender != request.user:
        messages.error(request, "Редактировать можно только свои черновики.")
        return redirect('inbox', username=username)

    if request.method == 'POST':
        form = ComposeEmailForm(request.POST)
        form.context = {'user': request.user}
        
        save_as_draft = 'save_draft' in request.POST
        
        if form.is_valid():
            email_item.recipient = form.cleaned_data['recipient']
            email_item.subject = form.cleaned_data['subject']
            email_item.body = form.cleaned_data['body']
            
            if save_as_draft:
                email_item.save()
                messages.success(request, "Черновик обновлён.")
                return redirect('email_list', username=username, folder='drafts')
            else:
                # Отправляем письмо
                recipient = form.cleaned_data['recipient']
                
                # Обновляем текущую запись для отправителя (меняем folder на sent)
                email_item.folder = 'sent'
                email_item.save()
                
                # Создаём копию для получателя
                Email.objects.create(
                    sender=request.user,
                    recipient=recipient,
                    subject=email_item.subject,
                    body=email_item.body,
                    slug=str(uuid.uuid4()),
                    folder='inbox',
                    read=False
                )
                
                messages.success(request, f"Письмо отправлено пользователю {recipient.username}")
                return redirect('email_list', username=username, folder='sent')
    else:
        # Заполняем форму данными черновика
        form = ComposeEmailForm(initial={
            'recipient': email_item.recipient.username,
            'subject': email_item.subject,
            'body': email_item.body
        })
        form.context = {'user': request.user}

    return render(request, 'email/edit_draft.html', {
        'form': form,
        'email': email_item,
        'username': username
    })
