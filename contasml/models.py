from django.db import models
import requests
from django.contrib.auth.models import User
from ferramentas.models import App
from django.utils import timezone


# Create your models here.
class ContaMercado(models.Model):
    
    access_token        = models.CharField(max_length=255)
    
    refresh_token       = models.CharField(max_length=255)
    
    id_conta            =  models.IntegerField()
    nome_conta          =   models.CharField(
        max_length      =   255, 
        verbose_name    =   'Nome da conta'
    )
    time_generate_access= models.DateTimeField(
        default         =   timezone.now,
        verbose_name    =   'Geração Access Token')    
    owner = models.ForeignKey(
        User, 
        on_delete       =   models.CASCADE, 
        verbose_name    =   'Dono'
        )
 
    # Define se utilizaremos a conta
    status_account      =   models.BooleanField(
        default         =   True, 
        verbose_name    =   'Access Token ativa')
    
    conta_ativa         =   models.BooleanField(
        default         =   True, 
        verbose_name    =   'Conta ativa',
        blank= True,
        null= True
        )
    
    # Define se a conta será usada como principal ou filha
    conta_pai_ou_filha  = models.BooleanField(
        default         =    False,
        verbose_name    =   'Tipo conta',
        blank= True,
        null= True
    )
    
    def __str__(self) -> str:
        return f'{self.nome_conta} - {self.owner}'


    def trocar_access_token(self):

        app = App.objects.get(id=1)
        info_app = {
            'id' : app.client_id,
            'secret': app.secret_key
        }
        
        headers = {
            'accept': 'application/json',
            'content-type': 'application/x-www-form-urlencoded',
        }
        data = f'grant_type=refresh_token&client_id={info_app["id"]}&client_secret={info_app["secret"]}&refresh_token={self.refresh_token}'

        response = requests.post('https://api.mercadolibre.com/oauth/token', headers=headers, data=data)
        response = response.json()

        # Atualizando dados da conta
        self.refresh_token = response['refresh_token']
        self.access_token = response['access_token']
        self.time_generate_access = timezone.now()
        self.status_account = True
        self.save()
            
    
    def access_token_inativo(self):
        
        # Diferenca entre o horário atual e o horário que o token foi gerado
        diferenca = timezone.now()-self.time_generate_access
        
        if len(str(diferenca)) > 14:
            return True
    
        try:
            horas_passadas_geracao_token =  str(diferenca)[0:2]
            
            if ':' in horas_passadas_geracao_token:
                horas_passadas_geracao_token = horas_passadas_geracao_token.replace(':','')
                        
            if int(horas_passadas_geracao_token) >=5:
                return True
            
        except:
            return True

        return False