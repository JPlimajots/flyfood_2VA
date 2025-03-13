import os
import time

# Função que retorna um dicionário de arquivos TSP a partir de um diretório
def arquivos_tsp(dir_tsp):
    # Lista os arquivos no diretório e cria um dicionário numerado
    dic_arquivos = {str(i + 1): arquivo for i, arquivo in enumerate(sorted(os.listdir(dir_tsp)))}
    return dic_arquivos

# Função para selecionar um arquivo TSP do diretório
def sel_arq_tsp(dir_tsp):
    dic_arquivos = arquivos_tsp(dir_tsp)  # Obtém dicionário de arquivos
    print('\n Arquivos TSP localizados: \n')
    
    # Exibe os arquivos disponíveis
    for numero, arquivo in dic_arquivos.items():
        print(f'{numero} - {arquivo}')  # Exibe os arquivos disponíveis
        
    print()
    num_arquivo = 0
    
    # Solicita ao usuário que escolha um arquivo
    while num_arquivo not in dic_arquivos:  # Escolha do arquivo que será testado
        num_arquivo = input('Informe o número do arquivo TSP que deseja analisar: ')
    return dic_arquivos[num_arquivo]  # Retorna o arquivo escolhido

# Calcula a distância euclidiana entre dois pontos
def distancia_euclidiana(x1, y1, x2, y2):
    return ((x2 - x1)**2 + (y2 - y1)**2) ** 0.5

# Implementa o algoritmo de roteamento do vizinho mais próximo
# Agora ele aceita tanto pontos com coordenadas quanto matriz de distâncias (quando matriz != None)
def roteamento_vizinho_mais_proximo(pontos, matriz=None):
    # Lista de nodos a partir das chaves do dicionário 'pontos'
    nodos = list(pontos.keys())
    origem = nodos[0]        # Define o ponto de origem como o primeiro ponto
    rota = [origem]          # Rota a ser construída, começando na origem
    distancia_total = 0      # Distância total do percurso
    atual = origem           # Ponto atual começa na origem
    nao_visitados = nodos.copy()  # Lista de pontos não visitados
    nao_visitados.remove(origem)  # Remove a origem da lista de não visitados

    # Enquanto houver pontos não visitados
    while nao_visitados:
        menor_distancia = float('inf')
        proximo_ponto = None

        # Para cada ponto não visitado, calcula a distância a partir do ponto atual
        for candidato in nao_visitados:
            if matriz is None:
                # Calcula a distância usando coordenadas
                dist = distancia_euclidiana(pontos[atual][0], pontos[atual][1],
                                            pontos[candidato][0], pontos[candidato][1])
            else:
                # Para matriz explícita: converte as chaves para índice
                dist = matriz[int(atual)-1][int(candidato)-1]
            if dist < menor_distancia:
                menor_distancia = dist      # Atualiza a menor distância
                proximo_ponto = candidato   # Atualiza o próximo ponto

        if proximo_ponto is None:  # Se não houver mais vizinhos, sai do loop
            break
        rota.append(proximo_ponto)           # Adiciona o ponto à rota
        distancia_total += menor_distancia     # Acumula a distância
        nao_visitados.remove(proximo_ponto)    # Remove o ponto da lista de não visitados
        atual = proximo_ponto                # Atualiza o ponto atual

    # Retorna ao ponto de origem e acumula a distância
    if matriz is None:
        distancia_total += distancia_euclidiana(pontos[atual][0], pontos[atual][1],
                                                  pontos[origem][0], pontos[origem][1])
    else:
        distancia_total += matriz[int(atual)-1][int(origem)-1]
    rota.append(origem)  # Retorna ao ponto de origem
    return rota, distancia_total  # Retorna a rota e a distância total

def principal():
    dir_tsp = 'tsp'  # Diretório onde os arquivos TSP estão armazenados
    arq_tsp = sel_arq_tsp(dir_tsp)  # Seleciona um arquivo TSP

    # Lendo o arquivo TSP
    with open(f'{dir_tsp}/{arq_tsp}', 'r') as file:
        linhas = file.read().splitlines()  # Lê todas as linhas do arquivo

    # Verifica qual o formato do arquivo: coordenadas ou matriz explícita
    if any("NODE_COORD_SECTION" in linha for linha in linhas):
        # Arquivo com coordenadas dos nós
        pontos = {}
        ler_pontos = False
        for linha in linhas:
            if linha.startswith("NODE_COORD_SECTION"):
                ler_pontos = True
                continue
            if linha.startswith("EOF"):
                break
            if ler_pontos:
                partes = linha.split()
                pontos[partes[0]] = (float(partes[1]), float(partes[2]))  # Armazena as coordenadas dos pontos
        matriz = None  # Não há matriz explícita
    elif any("EDGE_WEIGHT_SECTION" in linha for linha in linhas):
        # Arquivo com matriz de distâncias explícita
        # Obtém a dimensão a partir do cabeçalho
        dimensao = None
        for linha in linhas:
            if linha.startswith("DIMENSION"):
                dimensao = int(linha.split(":")[-1].strip())
                break
        if dimensao is None:
            raise Exception("DIMENSION não encontrado no arquivo TSP")
        # Cria dicionário de nós (valores podem ser None, pois usaremos a matriz)
        pontos = {str(i): None for i in range(1, dimensao+1)}
        em_secao = False
        numeros_matriz = []
        # Lê os números da matriz a partir da seção EDGE_WEIGHT_SECTION até encontrar "EOF"
        for linha in linhas:
            if "EDGE_WEIGHT_SECTION" in linha:
                em_secao = True
                continue
            if "EOF" in linha:
                break
            if em_secao:
                numeros_matriz.extend([float(x) for x in linha.split()])
        # Verifica se a quantidade de números é a esperada: (n*(n-1))//2
        if len(numeros_matriz) != (dimensao*(dimensao-1))//2:
            raise Exception("Número inesperado de valores na matriz de distâncias")
        # Constroi a matriz completa (simétrica)
        matriz = [[0]*dimensao for _ in range(dimensao)]
        indice = 0
        for i in range(dimensao-1):
            for j in range(i+1, dimensao):
                matriz[i][j] = numeros_matriz[indice]
                matriz[j][i] = numeros_matriz[indice]
                indice += 1
    else:
        raise Exception("Formato do arquivo TSP não reconhecido")

    try:
        # Início da execução dos cálculos
        inicio_tempo = time.time()

        rota, distancia_total = roteamento_vizinho_mais_proximo(pontos, matriz)  # Executa o roteamento
                   
        rota_string = ' -> '.join(rota)  # Constrói a string da rota
        
        print("\nRota:", rota_string)             # Exibe a rota
        print("\nDistância total:", distancia_total)  # Exibe a distância total

        # Fim da execução dos cálculos
        fim_tempo = time.time()
        tempo_execucao = fim_tempo - inicio_tempo  # Calcula o tempo de execução
        print("\nTempo de execucao:", round(tempo_execucao*1000, 2), "milissegundos\n")
    except Exception as e:
        print("Erro:", e)  # Trata exceções

principal()
