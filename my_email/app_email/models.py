import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Email(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_emails')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_emails')
    subject = models.CharField(max_length=200)
    body = models.TextField()
    folder = models.CharField(max_length=10, choices=[
        ('inbox', 'Inbox'),
        ('sent', 'Sent'),
        ('drafts', 'Drafts'),
        ('trash', 'Trash'),
    ])
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    slug = models.SlugField(unique=True, default=uuid.uuid4)

    def __str__(self):
        return f"{self.subject} → {self.recipient}"

    class Meta:
        ordering = ['-timestamp']