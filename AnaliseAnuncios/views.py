from django.shortcuts import render,redirect
from django.http import HttpResponse, Http404
import requests
from django.contrib import messages
import json
from datetime import datetime

# Create your views here.
def analisador_anuncios(request):

    caminho_template = 'AnaliseAnuncios/analiseanuncios.html'
    context = {
    }


    usuario_nao_logado = False if request.user.is_authenticated else True

    if usuario_nao_logado:
        messages.add_message(request,messages.INFO,'É necessário estar logado para acessar aquela página')
        return redirect('login')


    metodo_requisicao = request.method

    if metodo_requisicao != 'POST':
        return render(request, caminho_template,context)
    
    nome_anuncio = request.POST.get('anuncio')

    if not nome_anuncio:
        messages.add_message(request,messages.WARNING,'É necessário escrever o que você busca primeiro! O campo acima não pode ficar vazio')
        return render(request, caminho_template)

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
            'id_anuncio'    : anuncio['id'],
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

    return render(request, caminho_template, context)

def melhores_palavras(request):

    caminho_template = 'AnaliseAnuncios/melhorespalavras.html'

    usuario_logado = request.user.is_authenticated
    if not usuario_logado:
        messages.add_message(request,messages.WARNING,'É necessário estar logado para acessar aquela página')
        return redirect('login')
    
    if request.method == 'GET':
        return render(request,caminho_template)    
    
    nome_anuncio = request.POST.get('nome_anuncio')
    
    if not nome_anuncio:
        messages.add_message(request,messages.WARNING,'É necessário preencher o campo acima')
        return render(request,caminho_template)    
    
    anuncios = list()
    offsets = 0

    # Pegando os anúncios das cinco primeiras páginas
    for vez in range(0,5):
        response = requests.get(f'https://api.mercadolibre.com/sites/MLB/search?q={nome_anuncio}&offset={offsets}').json()
        
        # Pegando o resultado do JSON response. O result são os anúncios, resultados da busca.
        result = response['results']
        anuncios.append(result)
        
        # Ignorando mais ciquenta anúncios
        offsets += 50

    palavras = set()
    palavras_com_metricas = list()

    # Iterando os resultados de busca contidos na lista de anuncios
    for result in anuncios:

        # Iterando os anuncios do resultado da busca
        for anuncio in result:

            # Pegando informações do anúncio
            nome_produto    =   anuncio['title']
            vendas_produto  =   anuncio['sold_quantity']

            nome_produto = nome_produto.split()
            
            for nome in nome_produto:

                # Essa tupla contêm a palavra e a quantidade que essa palavra vendeu
                metricas_palavra = (nome,vendas_produto)
                palavras_com_metricas.append(metricas_palavra)
                palavras.add(nome)

    # Dicionário que vai conter quantidade de repetições de cada palavra com seu total de vendas
    palavras_repeticao = dict()

    # Criando as chaves de cada palavra para inserirmos um valor
    for palavra in palavras:
        palavras_repeticao[palavra] = {
            'repeticao' : 0,
            'vendas' : 0,
            'palavra' : palavra
        }
    
    # Inserindo valores no dicionário
    for item in palavras_com_metricas:

        palavra         = item[0] # Pegando a palavra
        vendas_palavra  = item[1] # Pegando as vendas que essa palavra possui

        # Acessando valores atuais da palavra
        repeticao = palavras_repeticao[palavra]['repeticao']
        vendas = palavras_repeticao[palavra]['vendas']

        # Adicionando novos valores na palavra
        palavras_repeticao[palavra]['repeticao'] = repeticao + 1
        palavras_repeticao[palavra]['vendas'] = vendas + vendas_palavra

    palavras_ordenadas = list()

    # Ordenando os anúncios
    for palavra in palavras_repeticao.values():

        # Lista vazia?
        if len(palavras_ordenadas) == 0:
            palavras_ordenadas.append(palavra)
            continue
        local_list = 0

        for palavra_ordenada in palavras_ordenadas:
            # Informações do anuncio ('repeticoes' :0, 'vendas':0, palavra: 'palavra')
            repeticoes = palavra_ordenada['repeticao']

            # Repetições da palavra atual, da variável palavra.
            repeticoes_palavra_atual = palavra['repeticao']

            # Se o total de repetições dessa palavra que está na localização X da lista ordenada for menor ou igual à palavra atual
            # Inserimos a palavra atual na posição que ela possuia.

            if repeticoes <= repeticoes_palavra_atual:
                palavras_ordenadas.insert(local_list,palavra)
                local_list = -1
                break
            
            local_list += 1

        if local_list != -1:
            palavras_ordenadas.append(palavra)
        
    palavras_ordenadas_final = list()

    for local in range(0,len(palavras_ordenadas)):
        if local == 50:
            break
        palavras_ordenadas_final.append(palavras_ordenadas[local])

    context = {
        'anuncios' : palavras_ordenadas_final
    }
        
            
    return render(request,caminho_template,context)    

def metricas(request):

    def pegar_anuncios(anuncio_a_ser_buscado : str, offset : int):
        response = requests.get(f'https://api.mercadolibre.com/sites/MLB/search?q={anuncio_a_ser_buscado}&offset={offset}').json()
        
        # Pegando o resultado do JSON response. O result são os anúncios, resultados da busca.
        result = response['results']
        return result
    
    def ordenar_anuncios_por_venda(paginas : dict):
        anuncios_ordenados = list()

        # Ordenando anúncios
        for anuncios in paginas.values():
            for anuncio in anuncios:

                if len(anuncios_ordenados) == 0:
                    anuncios_ordenados.append(anuncio)
                    break
                
                local_lista = 0 # Referencia a o index atual, onde estamos na iteração.

                for anuncio_ordenado in anuncios_ordenados: # Iterando para encontrar um anuncio com a venda menor que o anuncio atual.
                    
                    vendas_anuncio_ordenado = anuncio_ordenado['sold_quantity']
                    vendas_anuncio = anuncio['sold_quantity']

                    if vendas_anuncio_ordenado <= vendas_anuncio:
                        anuncios_ordenados.insert(local_lista,anuncio)
                        local_lista = -1
                        break
                        # Inserimos o anuncio no local do anúncio com menos vendas

                    else:
                        local_lista += 1

                if local_lista != -1:
                    anuncios_ordenados.append(anuncio)

        return anuncios_ordenados
    
    def ordenar_anuncios_estoque(anuncios : list):
        anuncios_ordenados = list()

        # Ordenando anúncios
        for anuncio in anuncios:
                        

            if len(anuncios_ordenados) == 0:
                anuncios_ordenados.append(anuncio)
                continue
            
            local_lista = 0 # Referencia a o index atual, onde estamos na iteração.

            for anuncio_ordenado in anuncios_ordenados: # Iterando para encontrar um anuncio com a venda menor que o anuncio atual.
                
                estoque_anuncio_ordenado = anuncio_ordenado['available_quantity']
                
                estoque_anuncio = anuncio['available_quantity']

                if estoque_anuncio_ordenado <= estoque_anuncio:
                    anuncios_ordenados.insert(local_lista,anuncio)
                    local_lista = -1
                    break
                    # Inserimos o anuncio no local do anúncio com menos vendas

                else:
                    local_lista += 1

            if local_lista != -1:
                anuncios_ordenados.append(anuncio)

        return anuncios_ordenados

    def vendas_por_estado(anuncios):
        anuncios_por_estado = {

        }

        for anuncio in anuncios:
            estado_anuncio = anuncio['address']['state_name']
            vendas_anuncio = anuncio['sold_quantity']


            # Checando se esse estado já foi criado
            if not estado_anuncio in anuncios_por_estado:
                
                anuncios_por_estado[estado_anuncio] = {
                    'vendas_do_estado' : vendas_anuncio,
                }
                continue

            vendas_estado = anuncios_por_estado[estado_anuncio]['vendas_do_estado'] + vendas_anuncio
            anuncios_por_estado[estado_anuncio]['vendas_do_estado']  = vendas_estado

        return anuncios_por_estado

    def vendas_por_pagina(paginas : dict):

        vendas_por_cada_pagina = dict()

        for pagina_atual, anuncios in paginas.items():

            for anuncio in anuncios:
                vendas_anuncios = anuncio['sold_quantity']

                pagina_existe_no_dicionario = True if pagina_atual in vendas_por_cada_pagina else False

                if not pagina_existe_no_dicionario:

                    # Criando página para captura de vendas
                    vendas_por_cada_pagina[pagina_atual] = {
                        'vendas_pagina' : vendas_anuncios
                    }
                    """
                    {
                        'primeira: {
                            'vendas_pagina : 10
                        },
                        'segunda: {
                            'vendas_pagina : 10
                        },
                        'terceira: {
                            'vendas_pagina : 15
                        }
                    }
                    """
                    continue

                vendas_por_cada_pagina[pagina_atual]['vendas_pagina'] = vendas_por_cada_pagina[pagina_atual]['vendas_pagina'] + vendas_anuncios
        return vendas_por_cada_pagina

    def contar_medalhas(anuncios: list):

        contador_medalhas = dict()

        for anuncio in anuncios:
            reputacao_vendedor = anuncio['seller']['seller_reputation']
            medalha_vendedor = reputacao_vendedor['power_seller_status']
            
            if not medalha_vendedor in contador_medalhas:
                
                if not medalha_vendedor:
                    medalha_vendedor = 'Sem medalha'

                # Criando contagem da medalha
                contador_medalhas[medalha_vendedor] = {
                    'repeticoes' : 1
                }
                continue
            
            # Adicionando uma repetição
            repeticoes_atual_medalha = contador_medalhas[medalha_vendedor]['repeticoes'] 

            # Adicionando mais uma repetição à repetições antigas.
            contador_medalhas[medalha_vendedor]['repeticoes'] = repeticoes_atual_medalha + 1
        
        return contador_medalhas
    
    def recuperar_anuncios_full(anuncios):
        
        anuncios_full = list()
        
        for anuncio in anuncios:
            
            anuncio_tipo_logistica = anuncio['shipping']['logistic_type']
            
            if anuncio_tipo_logistica == 'fulfillment':
                anuncios_full.append(anuncio)
        return anuncios_full



    if request.method == 'GET':
        return render(request, 'AnaliseAnuncios/metricas.html')
    
    # Caso seja post
    anuncio_buscado = request.POST.get('nome_anuncio')

    if not anuncio_buscado:
        messages.add_message(request,messages.INFO, 'É necessário preencher o campo acima')
        return render(request, 'AnaliseAnuncios/metricas.html')
    
    # Criando estruturas de dados para armazenar os anúncios das cinco primeiras páginas
    result = {}
    paginas = ('primeira','segunda','terceira','quarta','quinta')
    offsets = 0 # Variável usada para ignorar anúncios

    for pagina in paginas:
        response = pegar_anuncios(anuncio_buscado,offsets)
        
        # Passando os anúncios da página para um dicionário com a key referente a página.
        result[pagina] = response

        offsets += 50 # Ignorar + cinquenta primeiros anúncios
    # Recuperamos os anúncios e agrupamo-os por sua página de origem

    context = {
        #'cinco_anuncios_mais_estoque_full'  :   None,
    }

    # Criando a informação dos cinco anúncios com mais venda
    anuncios_ordenados = ordenar_anuncios_por_venda(result)
    anuncios = []
    for anuncio in anuncios_ordenados[0:5]:
        data_anuncio = {
            'titulo' : anuncio['title'],
            'link': anuncio['permalink']
        }
        anuncios.append(data_anuncio)

    # Criando a informação vendas por estado
    vendas_estado = vendas_por_estado(anuncios_ordenados)
    context['vendas_por_estado'] = vendas_estado

    # Criando vendas por página
    vendas_pagina = vendas_por_pagina(result)
    context['vendas_por_pagina'] = vendas_pagina

    #Criando top cinco anúncios full com mais estoque
    anuncios_full = recuperar_anuncios_full(anuncios_ordenados)
    anuncios_full_ordenados = ordenar_anuncios_estoque(anuncios_full)
    anuncios_full = []
    for anuncio in anuncios_full_ordenados[0:5]:
        data_anuncio = {
            'titulo' : anuncio['title'],
            'link': anuncio['permalink']
        }
        anuncios_full.append(data_anuncio)

    # Criando medalhas vendedor
    medalhas_vendedor = contar_medalhas(anuncios_ordenados)


    informacoes = json.dumps(context)
    while True:
        if "'" in informacoes:
            informacoes = informacoes.replace("'", '"')
        else:
            break
    informacoes = json.loads(informacoes)

    print(anuncios_full_ordenados)

    context = {
        'data' : informacoes,
        'medalha_anuncios' : medalhas_vendedor,
        'cinco_anuncios_mais_vendas' : anuncios,
        'anuncios_full_ordenados'   :anuncios_full
    }

    # Fim do algoritimo
    return render(request, 'AnaliseAnuncios/metricas_dash.html', context)
    #return render(request, 'AnaliseAnuncios/metricas_dash.html', context)
    
def analise_anuncio(request,id_anuncio):
    
    def pegar_produto(id_produto):
        url = f'https://api.mercadolibre.com/items/{id_produto}'
        response = requests.get(url=url)
        return response.json()

    def gerar_data(data):

        # Formatando a data para recuperação de seus dados
        data = data.replace('-',' ').replace('T',' ').split()

        ano = int(data[0])
        mes = int(data[1])
        dia = int(data[2])   

        data_object = datetime(year=ano,month=mes,day=dia)
        return data_object

    def comissao(preco,tipo_publicacao):

        tipo_listagens = {
            'gold_pro'      :   19,
            'gold_premium'  :   16,
            'gold_special'  :   13,
            'gold'          :   10,
            'silver'        :   7,
            'bronze'        :   4,
            'free'          :   0,
        }

        porcentagem_comissao = tipo_listagens[tipo_publicacao]
        
        comissao_mercado = preco * (porcentagem_comissao/100)

        return f'{comissao_mercado:.2f}'

    data_anuncio = pegar_produto(id_anuncio)
    
    # Checando se a requisição obteve sucesso
    if data_anuncio['status'] == 404:
        raise Http404('Esse anúncio não existe')


    # Criando a informação 'data da última atualização'.
    data_ultima_atualizacao = gerar_data(data_anuncio['last_updated']) 


    # Criando informação 'tempo passado desde a criação do anúncio'.
    data_criacao = gerar_data(data_anuncio['date_created'])
    data_atual  = datetime.now()
    
    tempo_passado_criacao_anuncio = data_atual- data_criacao 


    # Informação valor recebido pelo vendedor e comissão mercado livre criado
    preco_produto = data_anuncio['price'] 
    tipo_listagem = data_anuncio['listing_type_id']

    comissao_mercado = comissao(preco_produto,tipo_listagem)
    valor_ganho_vendedor = int(preco_produto) - float(comissao_mercado)

    context = {
        'valor_ganho_vendedor'          :   valor_ganho_vendedor,
        'tempo_passado_criacao_anuncio' :   tempo_passado_criacao_anuncio,
        'data_ultima_atualizacao'       :   data_ultima_atualizacao,
        'comissao_mercado'              :   comissao_mercado
    }



    return render(
        request,
        'AnaliseAnuncios/analise_anuncio.html',
        context)

