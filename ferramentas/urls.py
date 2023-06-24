from django.urls import path
from . import views

urlpatterns = [

    path('autentic/', views.autentic, name='autentic'),
    path('get_code/',views.get_code, name='get_code'),
    path('',views.list, name='list'),

]