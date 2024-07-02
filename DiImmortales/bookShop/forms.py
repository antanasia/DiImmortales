from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Profile, Review


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ChangeUsernameForm(forms.Form):
    old_username = forms.CharField(label="Старое имя пользователя")
    new_username = forms.CharField(label="Новое имя пользователя")

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(ChangeUsernameForm, self).__init__(*args, **kwargs)

    def clean_old_username(self):
        old_username = self.cleaned_data.get('old_username')
        if old_username != self.user.username:
            raise forms.ValidationError("Старое имя пользователя неверно")
        return old_username

    def clean_new_username(self):
        new_username = self.cleaned_data.get('new_username')
        if User.objects.filter(username=new_username).exists():
            raise forms.ValidationError("Пользователь с таким именем уже существует.")
        return new_username


class ChangeEmailForm(forms.Form):
    old_email = forms.EmailField(label="Старая электронная почта")
    new_email = forms.EmailField(label="Новая электронная почта")

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(ChangeEmailForm, self).__init__(*args, **kwargs)

    def clean_old_email(self):
        old_email = self.cleaned_data.get('old_email')
        if old_email != self.user.email:
            raise forms.ValidationError("Старая электронная почта неверна")
        return old_email

    def clean_new_email(self):
        new_email = self.cleaned_data.get('new_email')
        if User.objects.filter(email=new_email).exists():
            raise forms.ValidationError("Пользователь с такой электронной почтой уже существует.")
        return new_email


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput, label="Старый пароль")
    new_password1 = forms.CharField(widget=forms.PasswordInput, label="Новый пароль")
    new_password2 = forms.CharField(widget=forms.PasswordInput, label="Подтвердите новый пароль")

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not authenticate(username=self.user.username, password=old_password):
            raise forms.ValidationError("Старый пароль неверен")
        return old_password

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")

        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise forms.ValidationError("Новые пароли не совпадают")
        return cleaned_data


class AvatarChangeForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['review_content']
        widgets = {
            'review_content': forms.Textarea(attrs={'placeholder': 'Напишите ваш отзыв здесь...'})
        }
