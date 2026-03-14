from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class ComposeEmailForm(forms.Form):
    """Форма для написания нового письма."""
    recipient = forms.CharField(
        label="Получатель (username)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите username получателя'})
    )
    subject = forms.CharField(
        max_length=200,
        label="Тема",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Тема письма'})
    )
    body = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Текст письма'}),
        label="Сообщение"
    )

    def clean_recipient(self):
        username = self.cleaned_data['recipient']
        try:
            user = User.objects.get(username=username)
            if user == self.context.get('user'):
                raise forms.ValidationError("Нельзя отправить письмо самому себе.")
        except User.DoesNotExist:
            raise forms.ValidationError("Пользователь с таким username не найден.")
        return user


class RegistrationForm(UserCreationForm):
    """Форма регистрации нового пользователя."""
    
    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя пользователя'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Подтверждение пароля'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = 'Требуется имя пользователя. Только буквы, цифры и символы @/./+/-/_.'
        self.fields['password1'].help_text = 'Пароль должен содержать минимум 8 символов.'
        self.fields['password2'].help_text = 'Введите тот же пароль ещё раз.'
