from django.shortcuts import render,redirect
from django.contrib import messages
from contasml.models import ContaMercado
import json
import requests


def get_products(ids_produto :  list, access_token: str):
    
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

def pegue_produto(id_produto : int, access_token: str):
    
    url = f'https://api.mercadolibre.com/items/{id_produto}?access_token={access_token}'
    response = requests.get(url=url)
    response = response.json()
    
    return response

def get_descricao(id_produto : int | str, access_token: str):
    
    id_produto = str(id_produto)
    
    # Enviando requisição para recuperar a descrição
    url = f'https://api.mercadolibre.com/items/{id_produto}/description?access_token={access_token}'
    response = requests.get(url=url)
    
    descricao = response.json()

    # Recuperando a descrição em si e caso não exista vamos enviar um objeto None
    try:
        descricao['status'] 
        descricao =  None
    except:
        descricao = descricao['plain_text'] 
         
    return descricao

# Create your views here.

def listar_anuncios_conta_principal(request):
    
    caminho_template = 'GerenciamentoAnuncios/listagem-anuncios.html'

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



    return render(request, caminho_template,context)

def listar_anuncios_conta_principal_sem_rep(request):
    
    caminho_template = 'GerenciamentoAnuncios/listagem-anuncios-sem-rep.html'

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



    return render(request, caminho_template,context)



"""def publicar_anuncios_(request):

    if not request.user.is_authenticated:
        messages.add_message(request,messages.INFO,'Autentique-se primeiro!')
        return redirect('login')

    if request.method == 'POST':
        
        # Pegando informações dos anúncios contidas no JSON
        json_texto = request.POST.get('json')
        
        if not json_texto:
            return redirect('listar-anuncios')
            

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
"""

def publicar_anuncios(request):
    

    def formatar_sales_terms(sales_terms : list):

        sales_terms_formatado = []

        # Apagando campos indesejaveis
        for termo in sales_terms:
            del termo['name']
            del termo['value_id']
            del termo['value_struct']
            del termo['values']
            del termo['value_type']

            sales_terms_formatado.append(termo)

        return sales_terms_formatado
    
    def formatar_pictures(pictures : list):
        
        pictures_formatadas = []

        for foto in pictures:

            picture = {
                "source" : foto['url']
            }
            
            pictures_formatadas.append(picture)

        return pictures_formatadas

    def formatar_atributtes(atributos : list):

        atributos_formatados = []

        for atributo in atributos:

            #del atributo['value_id']
            del atributo['value_struct']
            del atributo['values']
            del atributo['attribute_group_id']
            del atributo['attribute_group_name']
            del atributo['value_type']
            del atributo['name']

            atributos_formatados.append(atributo)

        return atributos_formatados

    def formatar_variacoes(variacoes:list):

        variacao_formatada = []

        for variacao in variacoes:

            del variacao['id']
            del variacao['seller_custom_field']
            del variacao['catalog_product_id']
            del variacao['inventory_id']
            del variacao['item_relations']
            del variacao['user_product_id']

            # Formatando o cambo de combinação de atributos da variação
            for combinacao_atributos in variacao['attribute_combinations']:

                del combinacao_atributos['values']
                del combinacao_atributos['value_type']
                del combinacao_atributos['value_struct']

            # Formatando o campo de atributos da variação
            try:
                atributos = variacao['attributes']
                atributos = formatar_atributtes(atributos)
                variacao['attributes'] = atributos
            except:
                ...

            variacao_formatada.append(variacao)

        return variacao_formatada

    def str_para_json(string):
        string_json = json.loads(string)

        return string_json



    if request.method == 'GET':
        return redirect('listar-anuncios')

    # Pegando os anúncios que o usuário deseja republicar
    anuncios = request.POST.get('json')    
    anuncios = str_para_json(anuncios)

    if not request.user.is_authenticated:
        messages.add_message(request, messages.INFO,"Faça login primeiro")
        return redirect('login')

    # Recuperando as contas necessárias para a republicação de anúncios
    conta_principal_object = ContaMercado.objects.all().filter(
        conta_pai_ou_filha=True,
        owner=request.user)[0]
    
    # Caso não exista uma conta principal configurada
    if not conta_principal_object:
        messages.add_message(request,messages.INFO,'É necessário uma conta principal para utilizar esta ferramenta')
        return redirect('listar-anuncios')
    
    lista_contas_secundarias = ContaMercado.objects.all().filter(
        conta_pai_ou_filha=False,
        owner=request.user
    )

    if not lista_contas_secundarias:
        messages.add_message(request,messages.INFO,'É necessário ao menos uma conta secundária para utilizar esta ferramenta')
        return redirect('listar-anuncios')

    if conta_principal_object.access_token_inativo:
        conta_principal_object.trocar_access_token()
    
    for conta_secundaria in lista_contas_secundarias:
        
        if conta_secundaria.access_token_inativo:
            conta_secundaria.trocar_access_token()

    access_token_conta_principal = conta_principal_object.access_token

    for anuncio in anuncios.values():

        # Buscando informações excedentes do anúncio em questão
        id_anuncio          =   anuncio['id_anuncio']
        dados_anuncio       =   pegue_produto(id_anuncio,   access_token_conta_principal)
        descricao_anuncio   =   get_descricao(id_anuncio,   access_token_conta_principal)
        print('LISTAGEM TIPO ' + anuncio['tipo'])
        novo_anuncio = {
            'title'                 :   anuncio['title'],
            "category_id"           :   dados_anuncio['category_id'],
            "currency_id"           :   "BRL",
            "available_quantity"    :   1, #anuncio['stok'],
            "buying_mode"           :   "buy_it_now",
            "condition"             :   anuncio['condition'],
            "listing_type_id"       :   anuncio['tipo'],
            "sale_terms"            :   formatar_sales_terms(dados_anuncio['sale_terms']),
            "pictures"              :   formatar_pictures(dados_anuncio['pictures']),
            "attributes"            :   formatar_atributtes(dados_anuncio['attributes']),
            
        }

        if dados_anuncio['variations']:
            novo_anuncio['variations']  =   formatar_variacoes(dados_anuncio['variations'])   

        # Verificando se existe preço
        try: 
            int(anuncio['price'])
            novo_anuncio['price'] = anuncio['price']
        except:
            novo_anuncio['price'] = dados_anuncio["price"]

        for atributo in novo_anuncio['attributes']:

            condicoes_produto = {
                'used'          :   'Usado' ,
                'new'           :   'Novo' ,
                'recondicioned' :   'Recondicionado',

            }
            
            condicao_produto = condicoes_produto[novo_anuncio["condition"]]

            # Caso o atributo ITEM_CONDITION seja recondicionado e a condição do item não seja
            # Vamos alterar a condição do item para recondicionado.
            if atributo['value_name'] != condicao_produto and atributo['id'] == "ITEM_CONDITION":
                
                # Mudando a condição do item para recondicionado   
                novo_anuncio['condition'] = 'recondicioned'       

        # Transformando o novo anuncio em json
        novo_anuncio = json.dumps(novo_anuncio)
        novo_anuncio = json.loads(novo_anuncio)
        novo_anuncio = str(novo_anuncio).encode()

        # Postando o anúncio
        for conta_secundaria in lista_contas_secundarias:
                
                access_token_conta_secundaria = conta_secundaria.access_token
                
                headers = {
                'Authorization': f'Bearer {access_token_conta_secundaria}',
                'Content-Type': 'application/x-www-form-urlencoded',
                }
                response = requests.post('https://api.mercadolibre.com/items', headers=headers, data=novo_anuncio)
            

                # Caso conseguigamos postar o anúncio
                if not '40' in str(response):

                    id_novo_anuncio = response.json()['id']

                    if not anuncio['descricao']:
                        descricao_novo_anuncio = {
                            "plain_text" : descricao_anuncio
                        }
                    else:
                        descricao_novo_anuncio = {
                            "plain_text" : anuncio['descricao']
                        }
                    descricao_novo_anuncio = json.dumps(descricao_novo_anuncio)
                    descricao_novo_anuncio = json.loads(descricao_novo_anuncio)
                    descricao_novo_anuncio = str(descricao_novo_anuncio).encode()

                    response = requests.post(
                        f'https://api.mercadolibre.com/items/{id_novo_anuncio}/description',
                        headers=headers,
                        data = descricao_novo_anuncio
                        )

            

    return redirect('listar-anuncios')

def publicar_anuncios_sem_repeticao(request):
    

    def formatar_sales_terms(sales_terms : list):

        sales_terms_formatado = []

        # Apagando campos indesejaveis
        for termo in sales_terms:
            del termo['name']
            del termo['value_id']
            del termo['value_struct']
            del termo['values']
            del termo['value_type']

            sales_terms_formatado.append(termo)

        return sales_terms_formatado
    
    def formatar_pictures(pictures : list):
        
        pictures_formatadas = []

        for foto in pictures:

            picture = {
                "source" : foto['url']
            }
            
            pictures_formatadas.append(picture)

        return pictures_formatadas

    def formatar_atributtes(atributos : list):

        atributos_formatados = []

        for atributo in atributos:

            #del atributo['value_id']
            del atributo['value_struct']
            del atributo['values']
            del atributo['attribute_group_id']
            del atributo['attribute_group_name']
            del atributo['value_type']
            del atributo['name']

            atributos_formatados.append(atributo)

        return atributos_formatados

    def formatar_variacoes(variacoes:list):

        variacao_formatada = []

        for variacao in variacoes:

            del variacao['id']
            del variacao['seller_custom_field']
            del variacao['catalog_product_id']
            del variacao['inventory_id']
            del variacao['item_relations']
            del variacao['user_product_id']

            # Formatando o cambo de combinação de atributos da variação
            for combinacao_atributos in variacao['attribute_combinations']:

                del combinacao_atributos['values']
                del combinacao_atributos['value_type']
                del combinacao_atributos['value_struct']

            # Formatando o campo de atributos da variação
            try:
                atributos = variacao['attributes']
                atributos = formatar_atributtes(atributos)
                variacao['attributes'] = atributos
            except:
                ...

            variacao_formatada.append(variacao)

        return variacao_formatada

    def str_para_json(string):
        string_json = json.loads(string)

        return string_json

    def pegue_meu_id(access_token):
        headers = {
            'Authorization': f'Bearer {access_token}',
        }

        response = requests.get('https://api.mercadolibre.com/users/me', headers=headers)
        response = response.json()
        id_conta = response['id']

        return id_conta

    def pegar_nome_anuncios(access_token,id_vendedor):
        headers = {
            'Authorization': f'Bearer {access_token}',
        }
        response = requests.get(f'https://api.mercadolibre.com/sites/MLB/search?seller_id={id_vendedor}',headers=headers).json()
        response = response['results']
        anuncios = []
        
        for resultado in response:
            anuncios.append(resultado['title'])

        return anuncios

    if request.method == 'GET':
        return redirect('listar-anuncios')

    # Pegando os anúncios que o usuário deseja republicar
    anuncios = request.POST.get('json')    
    anuncios = str_para_json(anuncios)

    if not request.user.is_authenticated:
        messages.add_message(request, messages.INFO,"Faça login primeiro")
        return redirect('login')

    # Recuperando as contas necessárias para a republicação de anúncios
    conta_principal_object = ContaMercado.objects.all().filter(
        conta_pai_ou_filha=True,
        owner=request.user)[0]
    
    # Caso não exista uma conta principal configurada
    if not conta_principal_object:
        messages.add_message(request,messages.INFO,'É necessário uma conta principal para utilizar esta ferramenta')
        return redirect('listar-anuncios')
    
    lista_contas_secundarias = ContaMercado.objects.all().filter(
        conta_pai_ou_filha=False,
        owner=request.user
    )

    if not lista_contas_secundarias:
        messages.add_message(request,messages.INFO,'É necessário ao menos uma conta secundária para utilizar esta ferramenta')
        return redirect('listar-anuncios')

    if conta_principal_object.access_token_inativo:
        conta_principal_object.trocar_access_token()
    
    # Criando dicionário que vai guardar todos os nomes de anúncios
    nome_de_todos_anuncios_contas = {}

    for conta_secundaria in lista_contas_secundarias:
        
        if conta_secundaria.access_token_inativo:
            conta_secundaria.trocar_access_token()

        # Buscando todos os nomes de anúncios
        id_vendedor = pegue_meu_id(conta_secundaria.access_token)
        nome_anuncios = pegar_nome_anuncios(conta_secundaria.access_token,id_vendedor)
        
        nome_de_todos_anuncios_contas[conta_secundaria.access_token] = nome_anuncios

    access_token_conta_principal = conta_principal_object.access_token

    for anuncio in anuncios.values():
    

        # Buscando informações excedentes do anúncio em questão
        id_anuncio          =   anuncio['id_anuncio']
        dados_anuncio       =   pegue_produto(id_anuncio,   access_token_conta_principal)
        descricao_anuncio   =   get_descricao(id_anuncio,   access_token_conta_principal)

        novo_anuncio = {
            'title'                 :   anuncio['title'],
            "category_id"           :   dados_anuncio['category_id'],
            "currency_id"           :   "BRL",
            "available_quantity"    :   1, #anuncio['stok'],
            "buying_mode"           :   "buy_it_now",
            "condition"             :   anuncio['condition'],
            "listing_type_id"       :   anuncio['tipo'],
            "sale_terms"            :   formatar_sales_terms(dados_anuncio['sale_terms']),
            "pictures"              :   formatar_pictures(dados_anuncio['pictures']),
            "attributes"            :   formatar_atributtes(dados_anuncio['attributes']),
            
        }

        if dados_anuncio['variations']:
            novo_anuncio['variations']  =   formatar_variacoes(dados_anuncio['variations'])   

        # Verificando se existe preço
        try: 
            int(anuncio['price'])
            novo_anuncio['price'] = anuncio['price']
        except:
            novo_anuncio['price'] = dados_anuncio["price"]

        for atributo in novo_anuncio['attributes']:

            condicoes_produto = {
                'used'          :   'Usado' ,
                'new'           :   'Novo' ,
                'recondicioned' :   'Recondicionado',

            }
            
            condicao_produto = condicoes_produto[novo_anuncio["condition"]]

            # Caso o atributo ITEM_CONDITION seja recondicionado e a condição do item não seja
            # Vamos alterar a condição do item para recondicionado.
            if atributo['value_name'] != condicao_produto and atributo['id'] == "ITEM_CONDITION":
                
                # Mudando a condição do item para recondicionado   
                novo_anuncio['condition'] = 'recondicioned'       

        # Transformando o novo anuncio em json
        novo_anuncio = json.dumps(novo_anuncio)
        novo_anuncio = json.loads(novo_anuncio)
        novo_anuncio = str(novo_anuncio).encode()

        # Postando o anúncio
        for conta_secundaria in lista_contas_secundarias:
                
                # Checando se anúncio já existe na conta atual
                if anuncio['title'] in nome_de_todos_anuncios_contas[conta_secundaria.access_token]:
                    print(f'Não vou republicar o anúncio{anuncio["title"]}')
                    continue

                access_token_conta_secundaria = conta_secundaria.access_token
                print( nome_de_todos_anuncios_contas[conta_secundaria.access_token])
                
                #continue

                headers = {
                'Authorization': f'Bearer {access_token_conta_secundaria}',
                'Content-Type': 'application/x-www-form-urlencoded',
                }
                continue

                response = requests.post('https://api.mercadolibre.com/items', headers=headers, data=novo_anuncio)
            

                # Caso conseguigamos postar o anúncio
                if not '40' in str(response):

                    id_novo_anuncio = response.json()['id']
                    
                    if not anuncio['descricao']:
                        descricao_novo_anuncio = {
                            "plain_text" : descricao_anuncio
                        }
                    else:
                        descricao_novo_anuncio = {
                            "plain_text" : anuncio['descricao']
                        }
                        
                    descricao_novo_anuncio = json.dumps(descricao_novo_anuncio)
                    descricao_novo_anuncio = json.loads(descricao_novo_anuncio)
                    descricao_novo_anuncio = str(descricao_novo_anuncio).encode()

                    response = requests.post(
                        f'https://api.mercadolibre.com/items/{id_novo_anuncio}/description',
                        headers=headers,
                        data = descricao_novo_anuncio
                        )

            

    return redirect('listar-anuncios-sem-rep')


