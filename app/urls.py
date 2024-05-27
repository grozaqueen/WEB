"""
URL configuration for baumask project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('', views.index, name='index'),
    path('question/<int:q_id>', views.question, name='question'),
    path('ask', views.ask, name='ask'),
    path('tagind/<str:t_ind>', views.tagind, name='tagind'),
    path('show_hot', views.show_hot, name='show_hot'),
    path('settings', views.settings, name='settings'),
    path('login/', views.log_in, name='login'),
    path('signup', views.signup, name='signup'),
    path('exit', views.exit, name='exit'),
    path('rate/', views.rate, name='rate'),
    path('correct/', views.correct, name='correct'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)