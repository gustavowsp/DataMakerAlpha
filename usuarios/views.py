from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login as login_django
from django.contrib.auth import logout as logout_django
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

def login(request):
    
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
            login_django(request,usuario_object)
            return redirect('list')
        else:
            messages.add_message(request,messages.ERROR,'Esse usuário não existe, ou você errou sua senha.')
            return render(request,'usuarios/login.html')
    
    return render(request,'usuarios/login.html')

def logout(request):
    logout_django(request)
    messages.add_message(request,messages.SUCCESS,'Você foi deslogado, entre em sua conta!')
    return redirect('login')



"""
def list_account(request):
    ""Essa view irá recuperar contas ML do usuário e retornar para vizualização.""

    # Se user não estiver logado
    if not request.user.is_authenticated:
        messages.add_message(request,messages.INFO,'Você precisar esta logado antes de acessar suas contas')
        return redirect('login')

    # Pegando contas
    contas_ml_dousuario = ContaMercado.objects.all().filter(owner=request.user)
    
    if not contas_ml_dousuario:
        messages.add_message(request, messages.WARNING,'Crie uma conta mercado livre antes')
        return redirect('autentic')

    context = {
        'contas': {}
    }
    for conta in contas_ml_dousuario:
        context['contas'][conta.nome_conta] = {
            'nome_conta'        :conta.nome_conta, 
            'geracao_access'    :conta.time_generate_access,
            'dono'              :conta.owner,
            'status_account'    :conta.status_account,
        }

    return render(
        request,
        'usuarios/list-accounts-ml.html',
        context=context
        )

def refresh_token(request):
    
    def ajust_data():
        now = timezone_dg.now()
        now = str(now)[:-7]

        now =(
                int(now[0:4]),
                int(now[5:7])  ,
                int(now[8:10])  ,
                int(now[11:13]),
                int(now[14:16]),
                int(now[17:19])
        )

    

        now = (datetime.datetime(
                int(now[0]),int(now[1]),int(now[2]),
                int(now[3]),int(now[4]),int(now[5])
                )
        )
        return now   

    # Caso o usuário não esteja logado vamos redireciona-lo
    if not request.user.is_authenticated:
        messages.add_message(request,messages.INFO,'Você precisar esta logado antes de ativar suas contas')
        return redirect('login')

    # Pegando informações da aplicação
    aplicacao = App.objects.get(id=1)
    info_app =  {
        'id': aplicacao.client_id,
        'secret': aplicacao.secret_key
    }

    # Pegando contas ML
    contas_ml = ContaMercado.objects.all().filter(owner=request.user)
    
    # Acessando todas as contas inativas e pegando um novo access_token
    for conta in contas_ml:
        if conta.status_account == False:
            
            refresh = conta.refresh_token
            headers = {
                'accept': 'application/json',
                'content-type': 'application/x-www-form-urlencoded',
            }

            data = f'grant_type=refresh_token&client_id={info_app["id"]}&client_secret={info_app["secret"]}&refresh_token={refresh}'

            response = requests.post('https://api.mercadolibre.com/oauth/token', headers=headers, data=data)
            response = response.json()

            # Atualizando dados da conta
            conta.refresh_token = response['refresh_token']
            conta.access_token = response['access_token']
            conta.time_generate_access = ajust_data()
            conta.status_account = True
            conta.save()

    messages.add_message(request,messages.SUCCESS, "Todas as contas estão ativas novamente")
    return redirect('list')




# Exibindo Contas
def listar_contasml(request):

    if not request.user.is_authenticated:
        messages.add_message(request,messages.INFO,'Autentique-se primeiro!')
        return redirect('login')
   
    contas_mercadol = ContaMercado.objects.all().filter(owner=request.user)

    context = {
        'contas': {}
    }

    for conta in contas_mercadol:
        context['contas'][conta.nome_conta] = {
            'nome_conta'            :conta.nome_conta, 
            'id_conta'              :conta.id_conta, 
            'geracao_access'        :conta.time_generate_access,
            'conta_pai_ou_filha'    :conta.conta_pai_ou_filha,
            'status_account'        :conta.conta_ativa,
        }

    return render(
        request,
        'usuarios/listagem_contasml.html',
        context
    )

# Mudando o tipo de conta de secundária para principal, ou ao ocntrário
def transformar_em_conta_principal(request):
    
    if not request.user.is_authenticated:
        messages.add_message(request,messages.INFO,'Autentique-se primeiro!')
        return redirect('login')

    # Se capturar algo, conta filha quer virar pai
    if request.POST.get('id_conta_filha'):
        id_conta = request.POST.get('id_conta_filha')

        conta_mudando_tipo = ContaMercado.objects.get(id_conta=id_conta)
        try:
            conta_pai_atual = ContaMercado.objects.get(conta_pai_ou_filha=True)
            conta_pai_atual.conta_pai_ou_filha = False
            conta_pai_atual.save()
        except:
            ...
        conta_mudando_tipo.conta_pai_ou_filha = True
        conta_mudando_tipo.save()

    elif request.POST.get('id_conta_pai'):
        id_conta = request.POST.get('id_conta_pai')

        conta = ContaMercado.objects.get(   id_conta=id_conta)
        conta.conta_pai_ou_filha = False
        conta.save()


    return redirect('listar-contas')

# Mudando o status da conta.
def ativar_conta(request):
    
    if not request.user.is_authenticated:
        messages.add_message(request,messages.INFO,'Autentique-se primeiro!')
        return redirect('login')
    
    # Recuperando informações
    ativar_conta = request.POST.get('ativar')
    id_conta = request.POST.get('id')
    
    # Informações foram enviadas
    informacoes_enviadas = True if ativar_conta and id_conta else False
    if not informacoes_enviadas:
        return redirect('listar-contas')

    # Informações estão corretas e conseguem recuperar uma conta?
    try:
        conta = ContaMercado.objects.get(id_conta=id_conta)
    except:
        messages.add_message(request, messages.INFO, 'Essa conta não existe.')
        return redirect('listar-contas')

    # Mudar status da conta
    if ativar_conta == 'True':
        conta.conta_ativa = True
        
    elif ativar_conta == 'False':
        conta.conta_ativa = False
        
    conta.save()
    return redirect('listar-contas')



def listar_anuncios_conta_principal(request):
    
    def get_products_ids(id_acount, access_token):

        ""
        Essa função retorna uma LISTA de IDS de anúncios da conta do mercado livre.
        ""

        response = requests.get(f'https://api.mercadolibre.com/users/{id_acount}/items/search?access_token={access_token}')
        response = response.json()

        # Pegando o id dos anúncios -- Retorna uma lista
        id_anuncios = response['results']
        return id_anuncios,access_token

    def get_products(id_produto, access_token):
        
        ""
        Essa função retorna um dicionário com informações do produto
        ""

        produtos = {}

        for id_p in id_produto:
            response = requests.get(f'https://api.mercadolibre.com/items/{id_p}?access_token={access_token}')
            response = response.json()
            
            produtos[response['id']] =  response

        return produtos



    if not request.user.is_authenticated:
        messages.add_message(request,messages.INFO,'Autentique-se primeiro!')
        return redirect('login')

    # Pegando a conta principal
    try:
        conta_principal = ContaMercado.objects.get(conta_pai_ou_filha=True)
    except:
        messages.add_message(request, messages.INFO, "Selecione uma conta principal primeiro")
        return redirect('listar-contas')
    
    #TODO: Verificar se o access token está ativo.
    id_conta = conta_principal.id_conta
    access_token =  conta_principal.access_token

    id_anuncios = get_products_ids(id_conta,access_token)

    produtos = get_products(id_anuncios[0],access_token)
    
    context = {
        'produtos' : {}
    }

            #Adicionando no dicinário.
    for produto in produtos.values():
        context['produtos'][produto['id']] = {
                    'id_produto' : produto['id'],
                    'titulo_produto' : produto['title'],
                    'tags_produtos' :produto['tags'],
                    'seller_id' : produto['seller_id'],
                    'preco' : produto['price'],
                    'qtd_vendida' :produto['sold_quantity'],
                    'produto_img': produto['thumbnail']
                }




    return render(request, 'usuarios/listagem-anuncios.html',context)
"""