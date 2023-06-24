from django.urls import path
from . import views


urlpatterns = [
    path('register', views.register, name='register'),
    path('', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    # path('ml-accounts',views.list_account, name='list-accounts-ml'),
    # path('refresh',views.refresh_token, name='refresh'),


    # path('minhas-contas',views.listar_contasml, name='listar-contas' ),
    # path('transformar-principal',views.transformar_em_conta_principal, name='transfomar-principal' ),
    # path('ativar-conta',views.ativar_conta, name='ativar-conta' ),

    # path('meus-anuncios',views.listar_anuncios_conta_principal, name='listar-anuncios'),
]