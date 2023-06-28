from django.shortcuts import render,redirect
from contasml.models import ContaMercado
from django.contrib import messages
import requests
from django.utils import timezone
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
        data = f'grant_type=authorization_code&client_id={app.client_id}&client_secret={app.secret_key}&code={code}&redirect_uri=https://dtmaker.vercel.app/mercadolivre/get_code/'

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


    #TODO: Salvar código no banco de dados       
    code = request.GET.get('code')


    # Se não tiver code
    if not code:
        messages.add_message(request,messages.INFO,'Você precisa autorizar o nosso App para que possamos criar uma conta')
        return redirect('autentic')

    # Pegando o acess_token
    info = get_access_token(code)        
    print(info['refresh_token'])
    
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
        account.time_generate_access = timezone.now()

        account.save()

        messages.add_message(request,messages.INFO,'Essa conta já foi autenticada! Atualizamos seus dados')
        return redirect('listar-contas')

    # Salvar informações da conta do mercado livre, na conta.
    new_contaml = ContaMercado(
        access_token = info['access_token'],
        refresh_token = info['refresh_token'],
        id_conta = info['user_id'],
        nome_conta = get_name_user(info['access_token']),
        time_generate_access = timezone.now(),
        owner = request.user
    )
    new_contaml.save()

    # Sucesso, conta criada redirecionando para listagem
    messages.add_message(request,messages.SUCCESS, 'Você registrou uma conta!')
    return redirect('listar-contas')



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
        
        if conta.access_token_inativo():
            conta.trocar_access_token()

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
