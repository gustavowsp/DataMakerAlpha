from django.shortcuts import render,redirect
from contasml.models import ContaMercado
from django.contrib import messages
import requests
from django.utils import timezone as timezone_dg
from datetime import datetime
from ferramentas.models import  App
from django.http import HttpResponse

# Create your views here.


# Criando uma conta
def autentic(request):

    return render(
        request,
        'contasml/autentic.html'
    )

def get_code(request):
    """
    O mercado livre deve redirecionar o user,após sua autenticação
    para este local, pegaremos o code e recuperaremos o AcessToken,
    refresh token e outras informações.

    O usuário não pode mexer em nada nesta página, apenas vamos pegar
    as informações salvar e redirecionar   
    """
    
    def get_access_token(code):
        """
        Retorna um JSON() 
        com informações da conta.

        Essa função recupera o access_token e informações importantes
        Para a criação da conta ML
        """

        headers = {
            'Accept': 'application/json',
            'content-type': 'application/x-www-form-urlencoded',
        }

        # Recuperando informações da aplicação
        app = App.objects.get(id='1')

        # Montando a requisição para enviar ao servidor do mercado Livre
        data = f'grant_type=authorization_code&client_id={app.client_id}&client_secret={app.secret_key}&code={code}&redirect_uri=https://dtmaker.vercel.app/get_code/'

        # Enviando
        response = requests.post('https://api.mercadolibre.com/oauth/token', headers=headers, data=data)

        return response.json()

    def retorna_access_foi_enviado(response):
        """
        True: Access token foi retornado
        False: Não foi retornado

        Essa função verifica se o que foi retornado é o access token
        ou deu erro.
        """
        try:
            acess_token = response['access_token']
            return True
        except:
            return False

    def get_name_user(access_token):
        """
        Essa função envia uma requisição a api do mercado livre
        que retorna dados pessoais da conta, assim descubro o nome da conta
        e a retorno
        """

        response = requests.get(f'https://api.mercadolibre.com/users/me?access_token={access_token}')
        return response.json()['nickname']

    def account_exists(access_token):
        """
        True: Conta já existe
        False: Não existe

        Verifica se já há uma conta mercado livre dessa ativa.
        """

        response = requests.get(f'https://api.mercadolibre.com/users/me?access_token={access_token}')
        id_account = response.json()['id']

        try:
            ContaMercado.objects.get(id_conta=id_account)
            return True
        except:
            return False

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
    

    #TODO: Salvar código no banco de dados       
    code = request.GET.get('code')

    return HttpResponse(code)

    # Se não tiver code
    if not code:
        messages.add_message(request,messages.INFO,'Você precisa autorizar o nosso App para que possamos criar uma conta')
        return redirect('autentic')

    # Pegando o acess_token
    info = get_access_token(code)        

    # Verificando se access_token foi retornado, caso não erro
    if not retorna_access_foi_enviado(info):
        messages.add_message(request,messages.ERROR,'Tente novamente, não conseguimos autenticar')
        return redirect('autentic')


    # Verificando se conta ML já existe
    if account_exists(info['access_token']):
        account = ContaMercado.objects.get(id_conta=info['user_id'])

        # Atualizando dados
        account.access_token    =   info['access_token']
        account.refresh_token   =   info['refresh_token']
        account.status_account  =   True
        account.time_generate_access = ajust_data()

        account.save()

        messages.add_message(request,messages.INFO,'Essa conta já foi autenticada! Atualizamos seus dados')
        return redirect('listar-contas')

    # Salvar informações da conta do mercado livre, na conta.
    new_contaml = ContaMercado(
        access_token = info['access_token'],
        refresh_token = info['refresh_token'],
        id_conta = info['user_id'],
        nome_conta = get_name_user(info['access_token']),
        time_generate_access = datetime.now(),
        owner = request.user
    )
    new_contaml.save()

    # Sucesso, conta criada redirecionando para listagem
    messages.add_message(request,messages.SUCCESS, 'Você registrou uma conta!')
    return redirect('listar-contas')



# Renovando o access_token
"""def refresh_token(request):
    
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
    return redirect('list')"""




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

        if conta.access_token_inativo:
            print('Está inativo')
        else:
            print('Está ativo')

        context['contas'][conta.nome_conta] = {
            'nome_conta'            :conta.nome_conta, 
            'id_conta'              :conta.id_conta, 
            'geracao_access'        :conta.time_generate_access,
            'conta_pai_ou_filha'    :conta.conta_pai_ou_filha,
            'status_account'        :conta.conta_ativa,
        }

    return render(
        request,
        'contasml/listagem_contasml.html',
        context
    )

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


# Listagem de anúncios
