from django.db import models
# from .utils import default_camps
# from django.contrib.auth.models import User
# from django.utils import timezone

"""# Create your models here.
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

    def access_token_ativo(self):
        
        #Desenvolver função que mostra se o access token está ativo ou não.
        ...
"""