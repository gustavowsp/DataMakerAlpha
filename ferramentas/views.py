from django.shortcuts import render,redirect
import requests
from django.contrib import messages
from contasml.models import ContaMercado



def index(request):
    return render(request,'ferramentas/index.html')

def listar_anuncios_conta_principal(request):
    
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




    return render(request, 'ferramentas/listagem-anuncios.html',context)
