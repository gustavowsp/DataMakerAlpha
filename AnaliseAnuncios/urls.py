from django.urls import path
from AnaliseAnuncios import views


urlpatterns = [
    path('analisando-paginas', views.analisador_anuncios, name='analisador'),
    path('palavras-chaves', views.melhores_palavras, name='analisador'),
]
