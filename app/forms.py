import os

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import datetime
import re

from app.models import Profile, Question, Tag, QuestionRating, Answer, AnswerRating
from baumask import settings


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите никнейм'}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите пароль', 'minlength': '8'}),
    )


class RegisterForm(forms.ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'InputLogin',
                                      'placeholder': 'pasha.ru'}),
        max_length=15,
        label='Логин', required=True,
        help_text='Введите ваш логин (например, pasha.ru)')
    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'id': 'InputEmail', 'placeholder': 'pasha@mail.ru'}),
        max_length=40,
        label='Эл. почта', required=True, help_text='Формат почты: example@example.com',
        error_messages={'invalid': 'Некорректный формат электронной почты.'})
    nickname = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'id': 'InputNickname', 'placeholder': 'pashokSnezhok'}),
        max_length=30,
        label='Никнейм',
        required=True
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'InputPassword'}), max_length=30,
        min_length=6,
        label='Пароль', required=True, help_text='Минимальная длина пароля - 8 символов.')
    password_check = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'InputPasswordAgain'}), max_length=30,
        min_length=6,
        label='Повторите пароль', required=True)
    avatar = forms.ImageField(required=False, label='Аватарка')

    def clean_nickname(self):
        nickname = self.cleaned_data.get('nickname')
        if nickname:
            pattern = r'^[\w.-]*$'
            if not re.match(pattern, nickname):
                raise forms.ValidationError('В никнейме обнаружены недопустимые символы.')
        return nickname

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            pattern = r'^[\w.-]*$'
            if not re.match(pattern, username):
                raise forms.ValidationError('В имени пользователя обнаружены недопустимые символы.')
        if User.objects.filter(username=username).exists():
            self.add_error('username', 'Пользователь с таким логином уже существует.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            if User.objects.filter(email__iexact=email).exists():
                raise forms.ValidationError('Пользователь с такой электронной почтой уже существует.')
        return email

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, **kwargs):
        self.cleaned_data.pop('password_check')
        username = self.cleaned_data['username']
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        user = User.objects.create_user(username=username, email=email, password=password)

        print("FILES:", self.files)  # Add this line

        avatar = self.files.get('avatar')
        if avatar:
            # Save the uploaded avatar to the media directory
            avatar_path = os.path.join(settings.STATIC_URL, 'avatars')

            if not os.path.exists(avatar_path):
                os.makedirs(avatar_path)
            avatar_file_name = f"{self.cleaned_data['username']}_{avatar.name}"
            avatar_file_path = os.path.join(avatar_path, avatar_file_name)
            with open(avatar_file_path, 'wb+') as f:
                for chunk in avatar.chunks():
                    f.write(chunk)

            # Save the avatar URL to the database
            user_profile = Profile(avatar=f"avatars/{avatar_file_name}", user=user, login=self.cleaned_data['username'])
        else:
            # Use a default avatar if no file was uploaded
            user_profile = Profile(avatar='avatar.jpg', user=user, login=self.cleaned_data['username'])
        user_profile.save()
        return user

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        password_check = cleaned_data.get('password_check')

        if password != password_check:
            self.add_error('password_check', 'Введенные пароли не совпадают.')
            raise ValidationError('Введенные пароли не совпадают.')

class QuestionForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'InputTitle',
                                      'placeholder': 'Заголовок вашего вопроса'}), max_length=70, min_length=5,
        label='Заголовок вопроса', required=True)
    text = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'id': 'InputText',
                                     'placeholder': 'Опишите вашу проблему'}), max_length=500, min_length=5,
        label='Текст', required=True)
    tags = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'InputTags',
                                                         'placeholder': 'Ключевые слова, относящиеся к теме вопроса'}),
                           max_length=50,
                           label='Теги', required=True)

    class Meta:
        model = Question
        fields = ['title', 'text']

    def get_tags(self, tags):
        saved_tags = []
        for tag in tags:
            tag_obj = Tag.objects.filter(tag=tag).first()
            if tag_obj is None:
                tag_obj = Tag.objects.create(tag=tag)
            saved_tags.append(tag_obj)
        return saved_tags

    def clean_tags(self):
        tags = self.cleaned_data['tags']
        if not re.fullmatch(r'(\w|,| |;)*', tags):
            raise forms.ValidationError('В списке тегов обнаружены недопустимые символы.')
        tags = re.split(', |; | ', tags)
        tags = self.get_tags(tags)
        return tags

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title:
            pattern = r'^[a-zA-Z0-9\s\-!?():,.\'\" ]+$'
            if not re.match(pattern, title):
                raise forms.ValidationError('В заголовке обнаружены недопустимые символы.')
        return title

    def save(self, request, **kwargs):
        title = self.cleaned_data['title']
        text = self.cleaned_data['text']
        tags = self.cleaned_data['tags']
        date = datetime.now()
        profile = request.user.profile

        question = Question(title=title, text=text, date=date, profile=profile)
        question.save()
        question.tags.add(*tags)
        QuestionRating.objects.create(post=question, mark=0)
        return question

class AnswerForm(forms.ModelForm):
    text = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control border-secondary', 'id': 'InputText',
                                     'placeholder': 'Введите текст ответа', 'rows': 5}), max_length=500, min_length=5,
                                      label='Добавьте свой ответ:', required=True)

    class Meta:
        model = Answer
        fields = ['text']

    def save(self, request, question_id, **kwargs):
        text = self.cleaned_data['text']
        date = datetime.now()
        profile = request.user.profile
        question = Question.objects.filter(pk=question_id).first()

        answer = Answer(text=text, date=date, profile=profile, question=question, is_correct=None)
        answer.save()
        AnswerRating.objects.create(post=answer, mark=0)
        return answer

class SettingsForm(forms.ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'InputLogin'}), max_length=15,
        label='Логин', required=False)
    email = forms.EmailField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'InputEmail'}), max_length=40,
        label='Эл. почта', required=False)
    nickname = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'InputNickname'}), max_length=30,
        label='Никнейм', required=False)
    avatar = forms.ImageField(
        widget=forms.FileInput(attrs={'class': 'form-control', 'id': 'InputAvatar'}), label='Аватар',
        required=False)

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        print("Username:", username)
        print("Instance username:", self.instance.username)
        if username and username != self.instance.username:
            print("Username has been changed")
            pattern = r'^[\w.-]*$'
            if not re.match(pattern, username):
                raise forms.ValidationError('В имени пользователя обнаружены недопустимые символы.')
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError('Пользователь с таким логином уже существует.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and email != self.instance.email:
            if User.objects.filter(email__iexact=email).exists() and email != self.instance.email:
                raise forms.ValidationError('Пользователь с такой электронной почтой уже существует.')
        return email

    def clean_nickname(self):
        nickname = self.cleaned_data['nickname']
        if nickname:
            if re.fullmatch(r'(\d|\w|_|-|\.)*', nickname):
                return nickname
            else:
                self.add_error(None,
                               'В имени пользователя обнаружены недопустимые символы.')
                raise ValidationError(self)

    def save(self, request, **kwargs):
        user = request.user
        profile = request.user.profile

        class Meta:
            model = Profile
            fields = ['avatar']

        if 'username' in self.changed_data:
            user.username = self.cleaned_data['username']
        if 'email' in self.changed_data:
            user.email = self.cleaned_data['email']
        if 'nickname' in self.changed_data:
            profile.login = self.cleaned_data['nickname']

        avatar = self.files.get('avatar')
        if avatar:
            # Delete the old avatar if it exists
            old_avatar_path = profile.avatar.path
            if os.path.exists(old_avatar_path):
                os.remove(old_avatar_path)

            # Save the uploaded avatar to the media directory
            avatar_path = os.path.join(settings.STATIC_URL, 'avatars')

            if not os.path.exists(avatar_path):
                os.makedirs(avatar_path)
            avatar_file_name = f"{self.cleaned_data['username']}_{avatar.name}"
            avatar_file_path = os.path.join(avatar_path, avatar_file_name)
            with open(avatar_file_path, 'wb+') as f:
                for chunk in avatar.chunks():
                    f.write(chunk)

            # Save the avatar URL to the database
            profile.avatar=f"avatars/{avatar_file_name}"
        else:
            # Use a default avatar if no file was uploaded
            profile.avatar = 'avatar.jpg'

        profile.save()
        user.save()
