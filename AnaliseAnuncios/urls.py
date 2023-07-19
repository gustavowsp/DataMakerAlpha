from django.urls import path
from AnaliseAnuncios import views


urlpatterns = [
    path('analisando-paginas', views.analisador_anuncios, name='analisador'),
    path('palavras-chaves', views.melhores_palavras, name='palavras-chaves'),
    path('anuncio/<str:id_anuncio>', views.analise_anuncio, name='analisador-anuncio-unico'),
    path('informacoes-pagina', views.metricas, name='metricas'),
    
]
