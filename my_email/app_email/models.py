import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Email(models.Model):
    """Модель электронного письма."""
    
    FOLDER_CHOICES = [
        ('inbox', 'Входящие'),
        ('sent', 'Отправленные'),
        ('drafts', 'Черновики'),
        ('trash', 'Корзина'),
    ]

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_emails',
        verbose_name='Отправитель'
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_emails',
        verbose_name='Получатель'
    )
    subject = models.CharField(max_length=200, verbose_name='Тема')
    body = models.TextField(verbose_name='Текст письма')
    folder = models.CharField(
        max_length=10,
        choices=FOLDER_CHOICES,
        default='inbox',
        verbose_name='Папка'
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Дата отправки')
    read = models.BooleanField(default=False, verbose_name='Прочитано')
    slug = models.SlugField(unique=True, default=uuid.uuid4, verbose_name='Уникальный идентификатор')

    def __str__(self):
        return f"{self.subject} → {self.recipient}"

    @classmethod
    def send_email(cls, sender, recipient, subject, body):
        """
        Отправить письмо от sender к recipient.
        Автоматически создаёт копии для отправителя (sent) и получателя (inbox).
        """
        # Письмо для получателя (во входящих)
        recipient_email = cls.objects.create(
            sender=sender,
            recipient=recipient,
            subject=subject,
            body=body,
            folder='inbox',
            read=False
        )
        
        # Копия для отправителя (в отправленных) — с уникальным slug
        cls.objects.create(
            sender=sender,
            recipient=recipient,
            subject=subject,
            body=body,
            folder='sent',
            read=True
        )
        
        return recipient_email

    def move_to_folder(self, folder):
        """Переместить письмо в другую папку."""
        valid_folders = [choice[0] for choice in self.FOLDER_CHOICES]
        if folder in valid_folders:
            self.folder = folder
            self.save(update_fields=['folder'])
            return True
        return False

    def mark_as_read(self):
        """Отметить письмо как прочитанное."""
        if not self.read:
            self.read = True
            self.save(update_fields=['read'])

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Письмо'
        verbose_name_plural = 'Письма'
        indexes = [
            models.Index(fields=['recipient', 'folder']),
            models.Index(fields=['sender', 'folder']),
            models.Index(fields=['read']),
            models.Index(fields=['timestamp']),
        ]
