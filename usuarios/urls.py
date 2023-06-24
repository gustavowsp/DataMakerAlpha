from django.urls import path
from . import views


urlpatterns = [
    path('register', views.register, name='register'),
    path('', views.logar, name='login'),
    path('logout', views.deslogar, name='logout'),
]