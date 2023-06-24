from django.urls import path
from contasml import views


urlpatterns = [

    path('',views.listar_contasml, name='listar-contas' ),
    path('autentic/', views.autentic, name='autentic'),
    path('get_code/',views.get_code, name='get_code'),

    path('transformar-principal',views.transformar_em_conta_principal, name='transfomar-principal' ),
    path('ativar-conta',views.ativar_conta, name='ativar-conta' ),
    
    path('refresh',views.refresh_token, name='refresh'),
]