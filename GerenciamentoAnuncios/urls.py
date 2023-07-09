from django.urls import path
from GerenciamentoAnuncios import views


urlpatterns = [
    path('republicador',views.listar_anuncios_conta_principal, name='listar-anuncios'),
    path('p', views.publicar_anuncios, name='publicador'),
]