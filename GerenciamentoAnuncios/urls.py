from django.urls import path
from GerenciamentoAnuncios import views


urlpatterns = [
    path('republicador',views.listar_anuncios_conta_principal, name='listar-anuncios'),
    path('p', views.publicar_anuncios, name='publicador'),

    path('republicador-sem-repeticoes',views.listar_anuncios_conta_principal_sem_rep, name='listar-anuncios-sem-rep'),
    path('p_sem_repeticao', views.publicar_anuncios_sem_repeticao, name='publicador-sem_repeticao'),
]