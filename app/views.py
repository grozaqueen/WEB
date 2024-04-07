from collections import Counter

from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Question, QuestionRating, Tag, Profile, AnswerRating, Answer

questions = Question.objects.new_questions_list()
tag_list = Counter(Tag.objects.values_list('tag', flat=True)).most_common(4)

def paginate(objects, page, per_page=4):
    paginator = Paginator(objects, per_page)
    obj = paginator.get_page(page)
    return obj

def paginateans(objects, page, per_page=2):
    paginator = Paginator(objects, per_page)
    obj = paginator.get_page(page)
    return obj


def index(request):
    page = request.GET.get('page')
    if not page:
        page = 1
    return render(request, 'index.html', {'questions':paginate(questions, int(page)), 'tags':tag_list})


def question(request, q_id):
    page = request.GET.get('page')
    if not page:
        page = 1
    element = Question.objects.search(q_id)
    ans = Answer.objects.answers_list(q_id)
    return render(request, 'question.html', {'question':element, 'answers':paginateans(ans, int(page)), 'tags':tag_list})

def ask(request):
    return render(request, 'ask.html', {'tags':tag_list})

def tagind(request, t_ind):
    page = request.GET.get('page')
    filtered_questions = Question.objects.find_by_tag(t_ind)
    if not page:
        page = 1
    return render(request, 'tagind.html', {'questions': paginate(filtered_questions, int(page)), 'tag':t_ind, 'tags':tag_list})

def settings(request):
    return render(request, 'settings.html', {'tags':tag_list})

def login(request):
    logout = True
    return render(request, 'login.html', {'logout':logout, 'tags':tag_list})

def signup(request):
    logout = True
    return render(request, 'signup.html', {'logout':logout, 'tags':tag_list})


def show_hot(request):
    questionshot = Question.objects.hot_questions_list()
    hot = True
    page = request.GET.get('page')
    if not page:
        page = 1
    return render(request, 'index.html', {'questions': paginate(questionshot, int(page)), 'hot':hot, 'tags':tag_list})