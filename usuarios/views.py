from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login 
from django.contrib.auth import logout 
import re
#from usuarios.models import ContaMercado
#from ferramentas.models import App
#import requests
#from django.utils import timezone as timezone_dg
#import datetime

# Utils
def info_exists(infos):
        """
        True: Foram enviadas
        False: Não foram enviadas

        Essa função retorna se todas as informações necessárias 
        foram enviadas.
        """

        for value in infos.values():
            
            if not value:
                return False
            else: 
                envite = True

        return envite




# Usuários
def register(request):


    def exists_user(infos):
        """
        Verifica se já existe um user com este username.
        True: Existe
        False: Não existe
        """
        try:
            User.objects.get(username=infos['username_get'])
            exists = True
        except:
            exists = False
        
        return exists

    def email_utilizing(infos):
        """
        Verifica se já existe um user com este email.
        True: Existe
        False: Não existe
        """

        try:
            User.objects.get(email=infos['email'])
            exists = True
        except:
            exists = False
        return exists

    def validando_password(infos):
        """
        Retorno: 
        True - Existe erro - Casa 0
        False - Não existe erro - Casa 0
        Mensagem do erro - Casa 1

        Essa função vai validar a senha,
        verificar se a senha é forte o suficiente

        e verificar se as senhas coincidem.
        """
        password = infos['password_get']
        repassword = infos['re_password']

        
        if password != repassword:
            error = True,'As senhas não são iguais!'

        elif len(password) < 8:
            error = True, 'A senha possui menos que oito caracteres' 
        
        elif not re.search(r'[A-Z]', password):
            error = True, 'A senha não possui um caractere maíusculo'
            
        elif not re.search(r'\d', password):
            error = True, 'A senha não possui um número'
        
        elif not re.search(r'[!@#$%¨&*]', password):
            error = True, 'A senha não possui um caractere especial' 
        else:
            error = False,         

        return error
        
                         
    if request.method == 'POST':
        
        # Pegando informações enviadas
        user_info = {
        'username_get'      :   request.POST.get('username').lower(),
        'password_get'      :   request.POST.get('password') ,
        're_password'       :   request.POST.get('re_password'),
        'first_name_get'    :   request.POST.get('first_name'),
        'last_name_get'     :   request.POST.get('last_name'),
        'email'     :   request.POST.get('email'),
        }

        # Validando se todas as informações foram enviadas
        if not info_exists(user_info):
            messages.add_message(request,messages.INFO, "Você precisa preencher todos os campos!")
            return render(request,'usuarios/register.html')
        
        if bool(re.search(r"\s", user_info['username_get'])):
            messages.add_message(request,messages.INFO, "O username não pode ter espaços")
            return render(request,'usuarios/register.html')
        
        # Verificando se esse usuário já existe
        if exists_user(user_info):
            messages.add_message(request,messages.INFO, "Este username já está sendo utilizado")
            return render(request,'usuarios/register.html')

        # Verificando se o email já está sendo utilizado
        if email_utilizing(user_info):
            messages.add_message(request,messages.INFO, "Este email já está sendo utilizado")
            return render(request,'usuarios/register.html')

        #Validando senhas
        error = validando_password(user_info)
        if error[0]:
            messages.add_message(request,messages.WARNING,error[1])
            return render(request,'usuarios/register.html')

        # Se o usuário passou por tudo isso, sua conta será criada
        new_user = User.objects.create_user
        new_user =  new_user(
            username    =   user_info['username_get'],
            password    =   user_info['password_get'],
            email       =   user_info['email'],
            first_name  =   user_info['first_name_get'],
            last_name   =   user_info['last_name_get']   
        )
        new_user.save()

        messages.add_message(request,messages.SUCCESS,'Seu usuário foi criado!')
        return redirect('login')


    return render(
        request,
        'usuarios/register.html'
        )

def logar(request):
    
    if request.method == 'POST':
        
        # Pegando informações enviadas
        info = {
        'username'      :   request.POST.get('username').lower(),
        'password'      :   request.POST.get('password') ,
        }

        # Verificando se as informações foram enviadas
        if not info_exists(info):
            messages.add_message(request,messages.WARNING,'Você precisa preencher todos os campos')
            return render(request,'usuarios/login.html')
        
        # Autenticando o usuário
        usuario_object = authenticate(
            username=info['username'],
            password=info['password']
            )
        
        # Se o usuário estiver correto vou loga-lo
        if usuario_object:
            login(request,usuario_object)
            return redirect('listar-contas')
        else:
            messages.add_message(request,messages.ERROR,'Esse usuário não existe, ou você errou sua senha.')
            return render(request,'usuarios/login.html')
    
    return render(request,'usuarios/login.html')

def deslogar(request):
    logout(request)
    messages.add_message(request,messages.SUCCESS,'Você foi deslogado, entre em sua conta!')
    return redirect('login')


