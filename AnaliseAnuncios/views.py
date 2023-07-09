from django.shortcuts import render,redirect
import requests
from django.contrib import messages

# Create your views here.

def analisador_anuncios(request):

    caminho_template = 'AnaliseAnuncios/analiseanuncios.html'
    caminhos_css = ['AnaliseAnuncios/buscador.css',]
    context = {
        'caminho_css' : caminhos_css
    }


    usuario_nao_logado = False if request.user.is_authenticated else True

    if usuario_nao_logado:
        messages.add_message(request,messages.INFO,'É necessário estar logado para acessar aquela página')
        return redirect('login')


    metodo_requisicao = request.method

    if metodo_requisicao != 'POST':
        print(context)
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

    print(context)
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

    print(type(palavras_ordenadas))
    for local in range(0,len(palavras_ordenadas)):
        if local == 50:
            break
        palavras_ordenadas_final.append(palavras_ordenadas[local])

    context = {
        'anuncios' : palavras_ordenadas_final
    }
        
            
    return render(request,caminho_template,context)    

