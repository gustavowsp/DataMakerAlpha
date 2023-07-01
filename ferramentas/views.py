from django.shortcuts import render,redirect
from django.http import HttpResponse
import requests
from django.contrib import messages
from contasml.models import ContaMercado
import json


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



# views
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


    if not request.user.is_authenticated:
        messages.add_message(request,messages.INFO,'Autentique-se primeiro!')
        return redirect('login')

    # Pegando a conta principal
    try:
        conta_principal = ContaMercado.objects.get(conta_pai_ou_filha=True)
    except:
        messages.add_message(request, messages.INFO, "Selecione uma conta principal primeiro")
        return redirect('listar-contas')
    
    if conta_principal.access_token_inativo():
            conta_principal.trocar_access_token()


    id_conta = conta_principal.id_conta
    access_token =  conta_principal.access_token

    id_anuncios = get_products_ids(id_conta,access_token)

    produtos = get_products(id_anuncios[0],access_token)
    context = {
        'produtos' : {}
    }

     #Adicionando no dicinário.
    for produto in produtos.values():
        if produto['id'] == 'MLB3726745988':
            print(produto)
        context['produtos'][produto['id']] = {
                    'id_produto' : produto['id'],
                    'titulo_produto' : produto['title'],
                    'preco' : produto['price'],
                    'produto_img': produto['thumbnail'],
                    'estoque': produto['available_quantity'],
                }
    
        # Retornar frete




    return render(request, 'ferramentas/listagem-anuncios.html',context)

def publicar_anuncios(request):
    json_texto = request.POST.get('json')
    json_object = json.loads(json_texto)
    conta_principal = ContaMercado.objects.get(conta_pai_ou_filha=True)
    access_token = conta_principal.access_token

    contas_secundarias = ContaMercado.objects.all().filter(conta_ativa=True)


    for anuncio in json_object.values():

        id_anuncio = (anuncio['id_anuncio'],)
        produto = get_products(id_anuncio,access_token)
        info_anuncio = produto.get(id_anuncio[0])

        def crie_saleterms(info_anuncio):
            sale_terms = (info_anuncio.get('sale_terms'))
            
            atributos = list()
            for term in sale_terms:

                atributo_dict = {
                    'id' : term['id'],
                    'value_name' : term['value_name']
                }
                atributos.append(atributo_dict)
                
            return atributos

        def crie_atributos_produtos(info_anuncio):
            attributes = (info_anuncio.get('attributes'))

            atributos = list()
            for atributo in attributes:

                um_atributo = {
                    'id' : atributo['id'],
                    'value_name' : atributo['value_name']
                }
                atributos.append(um_atributo)
                

            return atributos

        attributes = crie_atributos_produtos(info_anuncio)
        sales_terms = crie_saleterms(info_anuncio)
        data = {
        "title"                 :   f'{anuncio["title"]}',
        #"title"                 :   'TESTEEEEE COLORIDO COR ROSA MEU AMOR',
        "category_id"           :   info_anuncio.get('category_id'),
        "price"                 :   f'{anuncio["price"]}',
        "currency_id"           :   "BRL",
        "available_quantity"    :   f'{anuncio["stok"]}',
        "buying_mode"           :   "buy_it_now",
        "listing_type_id"       :   f'{anuncio["tipo"]}',
        "condition"             :   'new',
        }
        data = str(data).strip()
        data = data[0:-1]

        data += ','
        if len(sales_terms) > 1:
            data += f'''"sale_terms" : [{sales_terms[0]},{sales_terms[1]}],'''
        else:
            data += f'''"sale_terms" : [{sales_terms[0]}],'''
            
        
        data += '''"pictures":[ {"source" :'''
        data += f'''"{info_anuncio['thumbnail']}'''
        data += '''" } ],'''
        

        data += '''"attributes":[ '''
        looping = 1
        for atributo in attributes:
            if looping == len(attributes):
                data += str(atributo)
            else:
                data += f'{str(atributo)},'
                
            looping += 1

        data += '''],'''
        data += '}'
        
        data = data.encode()

        for conta in contas_secundarias:
            access_token = conta.access_token
            headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
            requests.post('https://api.mercadolibre.com/items', headers=headers, data=data)

        


    return HttpResponse(json)




