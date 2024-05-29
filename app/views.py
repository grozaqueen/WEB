import math
from collections import Counter

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .forms import LoginForm, RegisterForm, QuestionForm, AnswerForm, SettingsForm
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from .models import Question, QuestionRating, Tag, Profile, AnswerRating, Answer


def paginate(objects, page, per_page=4):
    paginator = Paginator(objects, per_page)
    obj = paginator.get_page(page)
    return obj

def paginateans(objects, page, per_page=2):
    paginator = Paginator(objects, per_page)
    obj = paginator.get_page(page)
    return obj

@login_required(login_url='login', redirect_field_name='continue')
def index(request):
    name = request.user.profile.user.username
    questions = Question.objects.new_questions_list()
    tag_list = Counter(Tag.objects.values_list('tag', flat=True)).most_common(4)
    page = request.GET.get('page')
    if not page:
        page = 1
    return render(request, 'index.html', {'questions':paginate(questions, int(page)), 'tags':tag_list, 'name':name})

@login_required(login_url='login', redirect_field_name='continue')
def question(request, q_id):
    name = request.user.profile.user.username
    tag_list = Counter(Tag.objects.values_list('tag', flat=True)).most_common(4)
    page = request.GET.get('page')
    if not page:
        page = 1
    element = Question.objects.search(q_id)
    ans = Answer.objects.answers_list(q_id)
    if request.method == "GET":
        answer_form = AnswerForm()
    elif request.method == "POST":
        answer_form = AnswerForm(request.POST)
        if answer_form.is_valid():
            answer = answer_form.save(request, q_id)
            last_page = math.ceil(Answer.objects.answers_list(q_id).count() / 2)
            return redirect(reverse('question', kwargs={'q_id': q_id}) + f'?page={last_page}#{answer.pk}')
    return render(request, 'question.html', {'question':element, 'answers':paginateans(ans, int(page)), 'tags':tag_list, 'name':name, 'form':answer_form})

@login_required(login_url='login', redirect_field_name='continue')
def ask(request):
    name = request.user.profile.user.username
    tag_list = Counter(Tag.objects.values_list('tag', flat=True)).most_common(4)
    if request.method == "GET":
        question_form = QuestionForm()
    elif request.method == "POST":
        question_form = QuestionForm(request.POST)
        if question_form.is_valid():
            new_question = question_form.save(request)
            return redirect(reverse('question', kwargs={'q_id': new_question.pk}))
    return render(request, 'ask.html', {'tags':tag_list, 'name':name, 'form': question_form})

@login_required(login_url='login', redirect_field_name='continue')
def tagind(request, t_ind):
    name = request.user.profile.user.username
    tag_list = Counter(Tag.objects.values_list('tag', flat=True)).most_common(4)
    page = request.GET.get('page')
    filtered_questions = Question.objects.find_by_tag(t_ind)
    if not page:
        page = 1
    return render(request, 'tagind.html', {'questions': paginate(filtered_questions, int(page)), 'tag':t_ind, 'tags':tag_list, 'name':name})

@login_required(login_url='login', redirect_field_name='continue')
def settings(request):
    name = request.user.profile.user.username
    tag_list = Counter(Tag.objects.values_list('tag', flat=True)).most_common(4)
    if request.method == "GET":
        settings_form = SettingsForm(instance=request.user)
    elif request.method == "POST":
        settings_form = SettingsForm(instance=request.user, data=request.POST,  files=request.FILES)
        print("SUCCESS0")
        if settings_form.is_valid():
            settings_form.save(request)
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('settings')

    return render(request, 'settings.html', {'tags':tag_list, 'name':name, 'form':settings_form})

def log_in(request):
    tag_list = Counter(Tag.objects.values_list('tag', flat=True)).most_common(4)
    logout = True
    if request.method == "GET":
        login_form = LoginForm()
    if request.method == "POST":
        login_form = LoginForm(data=request.POST)
        if login_form.is_valid():

            user = authenticate(request, **login_form.cleaned_data)
            print("SUCCESS1")
            if user is not None:
                login(request, user)
                print("SUCCESS2")
                return redirect(reverse('index'))
            else:
                login_form.add_error(None, "Неверный пароль или такого пользователя не существует")

    return render(request, 'login.html', context={'form':login_form, 'logout':logout, 'tags':tag_list})

def signup(request):
    tag_list = Counter(Tag.objects.values_list('tag', flat=True)).most_common(4)
    logout = True
    if request.method == "GET":
        signup_form = RegisterForm()
    elif request.method == "POST":
        signup_form = RegisterForm(request.POST, request.FILES)
        print("SUCCESS0")
        if signup_form.is_valid():
            print("SUCCESS1")
            try:
                user = signup_form.save()
                print("SUCCESS2")
                login(request, user)
                return redirect(reverse('index'))
            except IntegrityError:
                signup_form.add_error(None, 'Пользователь с таким именем уже существует.')
                print("SUCCESS3")
    else:
        signup_form = RegisterForm()

    return render(request, 'signup.html', {'form': signup_form,'logout':logout, 'tags':tag_list})

@login_required(login_url='login', redirect_field_name='continue')
def show_hot(request):
    name = request.user.profile.user.username
    tag_list = Counter(Tag.objects.values_list('tag', flat=True)).most_common(4)
    questionshot = Question.objects.hot_questions_list()
    hot = True
    page = request.GET.get('page')
    if not page:
        page = 1
    return render(request, 'index.html', {'questions': paginate(questionshot, int(page)), 'hot':hot, 'tags':tag_list, 'name':name})


def exit(request):
    print("Kek")
    logout(request)
    return redirect(reverse('login'))

def rate(request):
    item_id = request.POST.get('item_id')
    rate_type = request.POST.get('rate_type')
    item_type = request.POST.get('item_type')
    search_obj = None
    rating = 0

    if item_type == 'answer':
        item_obj = get_object_or_404(Answer, pk=item_id)
        search_obj = AnswerRating.objects.search(item_obj, request.user.profile)
    elif item_type == 'question':
        item_obj = get_object_or_404(Question, pk=item_id)
        search_obj = QuestionRating.objects.search(item_obj, request.user.profile)

    if rate_type == 'like':
        rating = 1
    elif rate_type == 'dislike':
        rating = -1

    if search_obj is not None:
        if search_obj.mark == rating:
            search_obj.mark = 0
        else:
            search_obj.mark = rating
        search_obj.save()
    else:
        if item_type == 'question':
            QuestionRating.objects.create(mark=rating, post=item_obj, profile=request.user.profile)
        else:
            AnswerRating.objects.create(mark=rating, post=item_obj, profile=request.user.profile)

    return JsonResponse({'count': item_obj.rating_count()})

@require_http_methods(['POST'])
def correct(request):
    answer_id = request.POST.get('answer_id')
    is_correct = request.POST.get('is_correct')

    answer = Answer.objects.get(pk=answer_id)
    answer.is_correct = is_correct == 'true'
    answer.save()

    return JsonResponse({'message': 'Answer correctness updated successfully'})

