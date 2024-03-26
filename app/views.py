from django.shortcuts import render
from django.core.paginator import Paginator

tag_list = ['VK', 'Ассемблер']
questions = []
for i in range (0, 100):
    questions.append({
        'id': i,
        'title': f'Как понять железо? {i}',
        'content': 'Короче сел я как-то изучать схему 32-разрядной адресации и столкнулся с трудностями в понимании работы блока преобразования адресов. Откуда берется линейный адрес? И как из него получить физический адрес?',
        'tags': tag_list,
        'likes': 20+i,
        'answers': [
            {
                'title': 'Ответ 1',
                'content': 'Уровень логического адреса - это первая ступень в схеме преобразования адресов. Вторая ступень - получение из логического адреса 32-разрядного линейного адреса. Линейный адрес берётся из глобальной или локальной таблицы дескрипторов (GDT или LDT) в зависимости от соответствующего бита селектора (бит 2). Для получения из линейного адреса физического адреса используется третья ступень - механизм страничной адресации.'
            },
            {
                'title': 'Ответ 2',
                'content': 'Не знаю'
            },
            {
                'title': 'Ответ 3',
                'content': 'Для получения физического адреса из линейного адреса в компьютерных системах, часто используется механизм адресации и преобразования адресов, который осуществляется аппаратно с помощью таких компонентов, как Memory Management Unit (MMU) в процессоре.'
            }
        ]
    })


# Create your views here.

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
    return render(request, 'index.html', {'questions':paginate(questions, int(page))})


def question(request, q_id):
    page = request.GET.get('page')
    if not page:
        page = 1
    element = questions[q_id]
    return render(request, 'question.html', {'question':element, 'answers':paginateans(element['answers'], int(page))})

def ask(request):
    return render(request, 'ask.html')

def tagind(request, t_ind):
    page = request.GET.get('page')
    filtered_questions = [q for q in questions if t_ind in q['tags']]
    if not page:
        page = 1
    return render(request, 'tagind.html', {'questions': paginate(filtered_questions, int(page)), 'tag':t_ind})

def settings(request):
    return render(request, 'settings.html')

def login(request):
    logout = True
    return render(request, 'login.html', {'logout':logout})

def signup(request):
    logout = True
    return render(request, 'signup.html', {'logout':logout})


def show_hot(request):
    questionshot = sorted(questions, key=lambda x: x['likes'], reverse=True)
    hot = True
    page = request.GET.get('page')
    if not page:
        page = 1
    return render(request, 'index.html', {'questions': paginate(questionshot, int(page)), 'hot':hot})
