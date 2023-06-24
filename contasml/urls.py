from django.urls import path
from contasml import views


urlpatterns = [
    #path('ml-accounts',views.list_account, name='list-accounts-ml'),

    path('',views.listar_contasml, name='listar-contas' ),
    path('meus-anuncios',views.listar_anuncios_conta_principal, name='listar-anuncios'),

    path('transformar-principal',views.transformar_em_conta_principal, name='transfomar-principal' ),
    path('ativar-conta',views.ativar_conta, name='ativar-conta' ),
    
    path('refresh',views.refresh_token, name='refresh'),
]