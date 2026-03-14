from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class ComposeEmailForm(forms.Form):
    recipient = forms.CharField(label="Получатель (username)")
    subject = forms.CharField(max_length=200, label="Тема")
    body = forms.CharField(widget=forms.Textarea, label="Сообщение")

    def clean_recipient(self):
        username = self.cleaned_data['recipient']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError("Пользователь с таким username не найден.")
        return user