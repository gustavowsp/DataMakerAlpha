from django.urls import path
from . import views

urlpatterns = [

    path('',views.index, name='ferramentas'),
    path('anuncios',views.listar_anuncios_conta_principal, name='listar-anuncios'),
    path('publicar', views.publicar_anuncios, name='publicador'),
    path('analisar-anuncios', views.analisador_anuncios, name='analisador'),
    path('melhores-palavras', views.melhores_palavras, name='analisador'),

]