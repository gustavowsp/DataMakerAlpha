from django.shortcuts import render,redirect
from django.contrib import messages
import requests
from django.http import HttpResponse
from contasml.models import ContaMercado
from ferramentas.models import  App
from usuarios.utils import default_camps as utils_user
from django.utils import timezone as timezone_dg
import datetime





# Create your views here.
def autentic(request):

    return render(
        request,
        'ferramentas/autentic.html'
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
        data = f'grant_type=authorization_code&client_id={app.client_id}&client_secret={app.secret_key}&code={code}&redirect_uri=https://deletedps2.vercel.app/get_code/'

        # Enviando
        response = requests.post('https://api.mercadolibre.com/oauth/token', headers=headers, data=data)

        print(response.json())
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
    """print(code)
    # Se não tiver code
    if not code:
        messages.add_message(request,messages.INFO,'Você precisa autorizar o nosso App para que possamos criar uma conta')
        return redirect('autentic')

    # Pegando o acess_token
    info = get_access_token(code)        

    print(info)

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
        return redirect('list')

    # Salvar informações da conta do mercado livre, na conta.
    new_contaml = ContaMercado(
        access_token = info['access_token'],
        refresh_token = info['refresh_token'],
        id_conta = info['user_id'],
        nome_conta = get_name_user(info['access_token']),
        time_generate_access = utils_user.get_time(),
        owner = request.user
    )
    new_contaml.save()

    # Sucesso, conta criada redirecionando para listagem
    messages.add_message(request,messages.SUCCESS, 'Você registrou uma conta!')
    return redirect('list')
    """

    return HttpResponse(code)
def list(request):
    """
    Esta view vai pegar os dados de todas as contas ligadas e 
    retornar os produtos existentes.

    Vamos receber dois tipos de requisições
    GET:
    Vai retornar todos os anúncios

    POST:
    vai pegar os filtros que o user colocou e retornar
    anúncios filtrados.
    """
    
    def get_products_ids(id_acount, access_token):

        """
        Essa função retorna uma LISTA de IDS de anúncios da conta do mercado livre.
        """

        response = requests.get(f'https://api.mercadolibre.com/users/{id_acount}/items/search?access_token={access_token}')
        response = response.json()

        # Pegando o id dos anúncios -- Retorna uma lista
        id_anuncios = response['results']
        return id_anuncios,access_token

    def get_products(id_produto, access_token):
        
        """
        Essa função retorna um dicionário com informações do produto
        """

        produtos = {}

        for id_p in id_produto:
            response = requests.get(f'https://api.mercadolibre.com/items/{id_p}?access_token={access_token}')
            response = response.json()
            
            produtos[response['id']] =  response

        return produtos

    def get_accountsml(user):
        """
        Essa função retorna todas as CONTAS ML Do usuário.

        [OBJETO1,OBJETO2,OBJETO3]
        [CONTA1,CONTA2,CONTA3]
        """
        contas = ContaMercado.objects.all().filter(owner=user)
        accounts_with_status = dict()

        """
        {
            'CONTA_1': {
                'CONTA' : OBJETO_CONTA,
                'STATUS' : TRUE-FALSE 
            }
            'CONTA_2': {
                'CONTA' : OBJETO_CONTA,
                'STATUS' : TRUE-FALSE 
            }
        }
        """


        for conta in contas:
            
            # Pegando o horário que foi gerado o access token
            gerated_access_token = conta.time_generate_access

            # Pegando a diferença
            diferrence = utils_user.getDifference(gerated_access_token)
            
            # Se for maior que cinco o status da conta deve virar Falso
            print(diferrence)
            if diferrence >= 5:
                accounts_with_status[conta.nome_conta] = {
                    'conta' : conta,
                    'status' : False
                }
            else:
                accounts_with_status[conta.nome_conta] = {
                    'conta' : conta,
                    'status' : True
                }

        return accounts_with_status


    # Se não for autenticado
    if  not request.user.is_authenticated:
        messages.add_message(request,messages.INFO,'Você precisa estar logado primeiro!')
        return redirect('login')

    # Se não tiver contas ML
    if not ContaMercado.objects.all().filter(owner=request.user):
        messages.add_message(request,messages.INFO,"Crie uma conta antes de utilizar nossa ferramenta!")
        return  redirect('autentic')


    if request.method == 'GET':

        #Pegando todas as contas ML que um user tem
        accounts_with_status = get_accountsml(request.user)
        accounts =  []
        status_accounts = set()
        
        for conta in accounts_with_status.values():
            object = conta['conta']
            

            # Enviando mensagem caso haja contas inativas
            if not conta['status']:
                status_accounts.add(False)

                # Se estiver com status Online desativar
                if object.status_account:
                    object.status_account = conta['status']
                    object.save()

            # Adicionando objeto ATIVO para a lista de contas
            else:
                accounts.append(object)

        if False in status_accounts:
            messages.add_message(request,messages.WARNING,'Algumas de suas contas estão inativas')

        account_info_ml = dict() # Dict que vai armazenar informações dos user

        for account in accounts:
            account_info_ml[account.nome_conta] = {
                'id_conta' : account.id_conta,
                'acess_token' :  account.access_token
            }

        #  Inserindo o id de produtos de cada conta em um dicionário
        for conta in accounts:

            # Pegando id e access_token
            ids,access_token = get_products_ids(conta.id_conta,conta.access_token)

            account_info_ml[conta.nome_conta] = {
                'ids' : ids,
                'access_token' : access_token
            }

        # Vai entrar em cada chave de conta e retornar os IDS, em forma de lista
        contas = {
            'produtos' : {

            }
        }
       
        produtos = contas['produtos']
        for nome_contaml,values in account_info_ml.items():
            # Pegando informações de todos os produtos
            info_produtos = get_products(values['ids'],values['access_token'])

            # Local onde vou armazenar os produtos da conta
            produtos[nome_contaml] = {}

            #Adicionando no dicinário.
            for produto in info_produtos.values():
                produtos[nome_contaml][produto['id']] = {
                    'id_produto' : produto['id'],
                    'titulo_produto' : produto['title'],
                    'tags_produtos' :produto['tags'],
                    'seller_id' : produto['seller_id'],
                    'preco' : produto['price'],
                    'qtd_vendida' :produto['sold_quantity'],
                    'produto_img': produto['thumbnail']
                }


        return  render(
            request,
            'ferramentas/listagem.html',
            contas
        )

