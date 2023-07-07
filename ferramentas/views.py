from django.shortcuts import render,redirect
from django.http import HttpResponse
import requests
from django.contrib import messages
from contasml.models import ContaMercado
import json

# TODO: Retornar apenas as contas que o usuário é dono para vizualização. Atualmente estamos retornando todas


def get_products(ids_produto : int | list, access_token: str):
    
    """
    Essa função retorna um dicionário com informações do produto
    """
    produtos = {}
    """{
        '123' = {},
        '234' = {}
        }"""
    
    for id_produto in ids_produto:
        url = f'https://api.mercadolibre.com/items/{id_produto}?access_token={access_token}'
        response = requests.get(url=url)
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
        conta_principal = ContaMercado.objects.get(conta_pai_ou_filha=True,owner=request.user)
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

        context['produtos'][produto['id']] = {
                    'id_produto' : produto['id'],
                    'titulo_produto' : produto['title'],
                    'preco' : produto['price'],
                    'produto_img': produto['thumbnail'],
                    'estoque': produto['available_quantity'],
                }
    
        # Retornar frete
    contas_secundarias = ContaMercado.objects.all().filter(conta_ativa=True,owner=request.user)
    for conta in contas_secundarias:
        if conta.access_token_inativo():
            conta.trocar_access_token()



    return render(request, 'ferramentas/listagem-anuncios.html',context)

def publicar_anuncios(request):

    if not request.user.is_authenticated:
        messages.add_message(request,messages.INFO,'Autentique-se primeiro!')
        return redirect('login')

    if request.method == 'POST':
        json_texto = request.POST.get('json')
        json_object = json.loads(json_texto)
        conta_principal = ContaMercado.objects.get(conta_pai_ou_filha=True,owner=request.user)

        if conta_principal.access_token_inativo():
            conta_principal.trocar_access_token()
        access_token_conta_principal = conta_principal.access_token
        
        contas_secundarias = ContaMercado.objects.all().filter(conta_ativa=True,owner=request.user)


        for anuncio in json_object.values():

            id_anuncio = (anuncio['id_anuncio'],)
            produto = get_products(id_anuncio, access_token_conta_principal)
            info_anuncio = produto.get(id_anuncio[0])

            #if 

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

            def crie_fotos(info_anuncio):
                pictures = (info_anuncio.get('pictures'))

                print(pictures)

                fotos_json = list()
                for foto_source in pictures:
                    foto_nova = {
                        'source' : [foto_source['url']]
                    }
                    fotos_json.append(foto_nova)
                    

                return fotos_json

            def crie_variacoes_produtos(info_anuncios):
                try:
                    variacoes = info_anuncios.get('variations')
                except:
                    return
                
                lista_variacoes = []
                for variacao in variacoes:
                    
                    atributos_variacao = variacao['attribute_combinations']
                    nova_variacao = {
                        "attribute_combinations" : [
                        
                        ],
                    }
                    for atributo in atributos_variacao:

                        atributo_novo = {
                            "name" : atributo['name'],
                            "value_id" : atributo['value_id'],
                            "value_name" : atributo['value_name'],
                        }
                        nova_variacao['attribute_combinations'].append(atributo_novo)

                    

                    nova_variacao["price"] = variacao["price"]
                    nova_variacao["available_quantity"] = variacao["available_quantity"]
                    nova_variacao["picture_ids"] = variacao["picture_ids"]
                    
                    lista_variacoes.append(nova_variacao)
                
                return lista_variacoes

            def crie_atributos_produtos(info_anuncio):
                attributes = (info_anuncio.get('attributes'))

                atributos_sem_id = (
                    'PROCESSOR_CORES_NUMBER',
                    'RELEASE_YEAR',
                    'FRONT_CAMERAS_NUMBER',
                    'FRONT_CAMERA_RECORDING_RESOLUTION',
                    'REAR_CAMERAS_NUMBER',
                    'CAMERAS_MAIN_FEATURES',
                    'ESIMS_NUMBER',
                    'REAR_CAMERA_RECORDING_RESOLUTION',
                    'DISPLAY_RESOLUTION',
                    'SIM_CARD_SLOTS_NUMBER',
                    'LINE',
                    'HAZMAT_TRANSPORTABILITY',
                    'CPU_MODELS',
                
                )

                atributos = list()
                for atributo in attributes:
                    if atributo['id'] in atributos_sem_id:
                        um_atributo = {
                        'id' : atributo['id'],
                        'value_name' : atributo['value_name'],
                        }
                    else:
                        um_atributo = {
                            'id' : atributo['id'],
                            'value_name' : atributo['value_name'],
                            'value_id' : atributo['value_id']
                        }
                    atributos.append(um_atributo)
                    

                return atributos

            variacoes = crie_variacoes_produtos(info_anuncio)
            attributes = crie_atributos_produtos(info_anuncio)
            sales_terms = crie_saleterms(info_anuncio)
            fotos = crie_fotos(info_anuncio)
            data = {
                "title"                 :   f'{anuncio["title"]}',
                "category_id"           :   info_anuncio.get('category_id'),
                "price"                 :   f'{anuncio["price"]}',
                "currency_id"           :   "BRL",
                "available_quantity"    :   f'{anuncio["stok"]}',
                "buying_mode"           :   "buy_it_now",
                "listing_type_id"       :   f'{anuncio["tipo"]}',
                "condition"             :   f'{info_anuncio.get("condition")}',
            }

            categorias_listtipy_premium = ('MLB26426','MLB1055','MLB277671')
            if info_anuncio['category_id'] in categorias_listtipy_premium:
                data['listing_type_id'] = 'gold_pro'
            try:
                int(data['price'])
            except:
                data.pop('price')

            data = str(data).strip()
            data = data[0:-1] # Fatiando o json, removendo '}' que é o último caractere
            data += ','

            if len(sales_terms) > 1:
                data += f'''"sale_terms" : [{sales_terms[0]},{sales_terms[1]}],'''
            else:
                data += f'''"sale_terms" : [{sales_terms[0]}],'''
                
            if info_anuncio['video_id'] != '':
                data += ' "video_id" : "' 
                data += f" {info_anuncio['video_id']}"
                data += '",'
            data += '''"pictures":[ {"source" :'''
            data += f'''"{info_anuncio['thumbnail']}'''
            looping = 1
            for foto in fotos:
                if looping == len(fotos):
                    data += str(foto)
                else:
                    data += f'{str(foto)},'
                    
                looping += 1
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


            data += '''"variations":[ '''
            looping = 1
            for variacao in variacoes:
                if looping == len(variacoes):
                    data += str(variacao)
                else:
                    data += f'{str(variacao)},'
                    
                looping += 1

            data += '''],'''

            data += '}'
            
            data_ = data.encode()

            for conta in contas_secundarias:
                access_token = conta.access_token
                headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/x-www-form-urlencoded',
                }
                requests.post('https://api.mercadolibre.com/items', headers=headers, data=data_)
            

        messages.add_message(request,messages.SUCCESS, "Seus anúncios foram publicados!")
        return redirect('listar-anuncios')
    return redirect('listar-anuncios')

def analisador_anuncios(request):

    usuario_nao_logado = False if request.user.is_authenticated else True

    if usuario_nao_logado:
        messages.add_message(request,messages.INFO,'É necessário estar logado para acessar aquela página')
        return redirect('login')


    metodo_requisicao = request.method

    if metodo_requisicao != 'POST':
        return render(request, 'ferramentas/analiseanuncios.html')
    
    nome_anuncio = request.POST.get('anuncio')

    if not nome_anuncio:
        messages.add_message(request,messages.WARNING,'É necessário escrever o que você busca primeiro! O campo acima não pode ficar vazio')
        return render(request, 'ferramentas/analiseanuncios.html')

    response = requests.get(f'https://api.mercadolibre.com/sites/MLB/search?q={nome_anuncio}')
    
    anuncios_json = response.json()
    anuncios_json = anuncios_json['results']

    id_conta_anuncios = set()

    anuncios = list()
    conta_anuncios = list()
    for anuncio in anuncios_json:
        id_conta = anuncio["seller"]["id"]
        id_conta_anuncios.add(id_conta)

        # Pegando informações específicas do anúncio
        endereco_anuncio = anuncio["seller_address"]
        anuncio_vendedor = anuncio['seller']
        metricar_do_vendedor = anuncio_vendedor['seller_reputation']['metrics']
        transacoes_do_vendedor = anuncio_vendedor['seller_reputation']['transactions']
        endereco_vendedor = anuncio['seller_address']
        anuncio_atributos = anuncio['attributes']

        # Criando anuncio no JSON
        for atributo in anuncio_atributos:
            if atributo['id'] == 'BRAND':
                anuncio_atributos = atributo['value_name']
        anuncio_informacoes = {
            "nome_vendedor" : anuncio_vendedor["nickname"],
            "titulo_produto" : anuncio['title'],
            "marca" : anuncio_atributos,
            "foto" : anuncio["thumbnail"],
            #"data_criacao" : f'',
            "localizacao" : f"{endereco_anuncio['state']['name']} - {endereco_anuncio['city']['name']}",
            "vendas" : anuncio["sold_quantity"],
            #"frete" : f'',
            "reputacao" : anuncio_vendedor['seller_reputation']['level_id'],
        }
        if type(anuncio_informacoes['marca']) == list:
            anuncio_informacoes['marca'] = 'Sem Marca'
        
    
        info_conta = {
            'vendas' : transacoes_do_vendedor["total"],
            'vendas_feitas' : transacoes_do_vendedor["completed"],
            'vendas_canceladas' : transacoes_do_vendedor["canceled"],

            'vendas_60d' : metricar_do_vendedor['sales']['completed'],
            'reinvidicacoes_60d' : metricar_do_vendedor['claims']['value'],
            'atrasos_60d' : metricar_do_vendedor['cancellations']['value'],
            
            'localizacao' : f'{endereco_vendedor["state"]["name"]} - {endereco_vendedor["city"]["name"]}',
            'reputacao' : anuncio_vendedor['seller_reputation']['level_id'],
            'nome' : anuncio_vendedor['nickname'],
        }
        
        conta_anuncios.append(info_conta)
        anuncios.append(anuncio_informacoes)
    
    #conta_anuncios = list()
    """for id in id_conta_anuncios:
        info_conta = requests.get(f'https://api.mercadolibre.com/users/{id}').json()


        seller_reputation = info_conta['seller_reputation']
   
        info_conta = {
            'vendas' : seller_reputation["transactions"]["total"],
            'vendas_feitas' : seller_reputation["transactions"]["completed"],
            'vendas_canceladas' : seller_reputation["transactions"]["canceled"],
            #'reclamacoes' : '',
            #'total_anuncios' : '',
            #'anuncios_fullfitmen' : '',
            #'anuncios_free_frete' : '',
            'localizacao' : f'{info_conta["address"]["state"]}-{info_conta["address"]["city"]}',
            'reputacao' : seller_reputation['level_id'],
            'nome' : info_conta['nickname'],
        }
        
        conta_anuncios.append(info_conta)
    """

    context = {}
    context['anuncios'] ={

    } 
    context['contas'] =  {

    }
    
    for anuncio in anuncios:

        nome_vendedor = anuncio['nome_vendedor']
        context['anuncios'][nome_vendedor] = anuncio


    for conta in conta_anuncios:
        nome_vendedor = conta['nome']
        context['contas'][nome_vendedor] = conta

    
    return render(request, 'ferramentas/analiseanuncios.html',context)

# def melhores_palavras(request):
#     return HttpResponse('Melhores palavras')    


