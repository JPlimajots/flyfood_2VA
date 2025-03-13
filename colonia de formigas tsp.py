import re
import matplotlib.pyplot as plt
import time
import os
import random

def listar_arquivos_tsp(diretorio):
    """Lista os arquivos TSP no diretório e cria um dicionário numerado."""
    arquivos = {str(i+1): nome for i, nome in enumerate(sorted(os.listdir(diretorio)))}
    return arquivos

def selecionar_arquivo_tsp(diretorio):
    """Permite ao usuário selecionar um arquivo TSP do diretório."""
    arquivos = listar_arquivos_tsp(diretorio)
    print("Arquivos TSP disponíveis:")
    for num, nome in arquivos.items():
        print(f"{num} - {nome}")
    escolha = input("\nDigite o número do arquivo: ")
    return arquivos[escolha]

def ler_coordenadas(arquivo):
    """Lê as coordenadas de um arquivo TSP no formato EUC_2D."""
    coordenadas = {}
    ler = False
    with open(arquivo, 'r') as f:
        for linha in f:
            linha = linha.strip()
            if linha == "NODE_COORD_SECTION":
                ler = True
                continue
            if linha == "EOF" or linha.startswith("EDGE_WEIGHT_SECTION"):
                break
            if ler and linha:
                partes = re.split(r'\s+', linha.strip())
                if len(partes) >= 3:
                    coordenadas[partes[0]] = (float(partes[1]), float(partes[2]))
    return coordenadas

def ler_matriz_explicita(arquivo, dimensao, formato):
    """Lê a matriz de distâncias de um arquivo TSP no formato EXPLICIT."""
    matriz = []
    ler = False
    with open(arquivo, 'r') as f:
        for linha in f:
            linha = linha.strip()
            if linha.startswith("EDGE_WEIGHT_SECTION"):
                ler = True
                continue
            if linha == "EOF":
                break
            if ler and linha:
                matriz.extend(list(map(int, re.split(r'\s+', linha.strip()))))
    
    if formato == "UPPER_ROW":
        tamanho = dimensao*(dimensao-1)//2
        matriz = matriz[:tamanho]
        distancias = [[0]*dimensao for _ in range(dimensao)]
        indice = 0
        for i in range(dimensao):
            for j in range(i+1, dimensao):
                if indice < len(matriz):
                    distancias[i][j] = matriz[indice]
                    distancias[j][i] = matriz[indice]
                    indice += 1
        return distancias
    else:
        raise ValueError(f"Formato {formato} não suportado")

def calcular_distancia_euclidiana(p1, p2):
    """Calcula a distância euclidiana entre dois pontos."""
    return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5

def criar_matriz_distancias(coordenadas):
    """Cria matriz de distâncias a partir de coordenadas EUC_2D."""
    nos = sorted(coordenadas.keys(), key=lambda x: int(x))  # Ordena numericamente
    n = len(nos)
    matriz = [[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1, n):
            dist = calcular_distancia_euclidiana(coordenadas[nos[i]], coordenadas[nos[j]])
            matriz[i][j] = dist
            matriz[j][i] = dist
    return matriz, nos  # Retorna também a lista de nós ordenados

def inicializar_feromonios(matriz, tau0):
    """Inicializa a matriz de feromônios."""
    n = len(matriz)
    return [[tau0 for _ in range(n)] for _ in range(n)]

def calcular_probabilidades(matriz_dist, matriz_fero, alfa, beta):
    """Calcula as probabilidades de transição entre nós."""
    n = len(matriz_dist)
    probabilidades = []
    for i in range(n):
        probs = []
        total = 0
        for j in range(n):
            if i == j:
                probs.append(0)
            else:
                valor = (matriz_fero[i][j]**alfa) * ((1/matriz_dist[i][j])**beta)
                probs.append(valor)
                total += valor
        if total == 0:
            probs = [1/n for _ in range(n)]
        else:
            probs = [p/total for p in probs]
        probabilidades.append(probs)
    return probabilidades

def selecionar_proximo_no(atual, probs, visitados):
    """Seleciona o próximo nó usando a roleta de probabilidades."""
    candidatos = [i for i in range(len(probs)) if i not in visitados]
    if not candidatos:
        return None
    probs_candidatos = [probs[atual][i] for i in candidatos]
    total = sum(probs_candidatos)
    if total == 0:
        return random.choice(candidatos)
    r = random.uniform(0, total)
    acumulado = 0
    for index in range(len(candidatos)):
        i = candidatos[index]
        p = probs_candidatos[index]
        acumulado += p
        if r <= acumulado:
            return i
    return random.choice(candidatos)

def calcular_custo_rota(rota, matriz_dist):
    """Calcula o custo total de uma rota."""
    custo = 0
    for i in range(len(rota)-1):
        custo += matriz_dist[rota[i]][rota[i+1]]
    return custo

def atualizar_feromonios(matriz_fero, rotas, custos, rho, Q):
    """Atualiza os feromônios usando evaporação e depósito."""
    n = len(matriz_fero)
    for i in range(n):
        for j in range(n):
            matriz_fero[i][j] *= (1 - rho)
    
    for k in range(len(rotas)):
        rota = rotas[k]
        custo = custos[k]
        delta = Q / custo
        for i in range(len(rota)-1):
            matriz_fero[rota[i]][rota[i+1]] += delta
            matriz_fero[rota[i+1]][rota[i]] += delta

def colonia_de_formigas(arquivo_tsp, num_formigas=20, max_iter=100, alfa=1, beta=2, rho=0.5, Q=100):
    """Implementação do algoritmo de colônia de formigas para TSP."""
    with open(arquivo_tsp, 'r') as f:
        conteudo = f.read().upper()
    
    dim_match = re.search(r'DIMENSION\s*:\s*(\d+)', conteudo)
    dimensao = int(dim_match.group(1))
    
    edge_type_match = re.search(r'EDGE_WEIGHT_TYPE\s*:\s*([^\s]+)', conteudo)
    edge_type = edge_type_match.group(1).strip().replace(" ", "")
    
    edge_format = None
    if edge_type == "EXPLICIT":
        format_match = re.search(r'EDGE_WEIGHT_FORMAT\s*:\s*([^\s]+)', conteudo)
        edge_format = format_match.group(1).strip().replace(" ", "")
    
    if edge_type in ["EUC_2D", "CEIL_2D", "GEO"]:
        coordenadas = ler_coordenadas(arquivo_tsp)
        matriz_dist, nos = criar_matriz_distancias(coordenadas)  # Recebe a lista de nós
    elif edge_type == "EXPLICIT":
        if edge_format == "UPPER_ROW":
            matriz_dist = ler_matriz_explicita(arquivo_tsp, dimensao, edge_format)
            nos = [str(i+1) for i in range(dimensao)]
        else:
            raise ValueError(f"Formato EXPLICIT {edge_format} não suportado")
    else:
        raise ValueError(f"Tipo de peso {edge_type} não suportado")
    
    tau0 = 1 / (dimensao * sum([sum(linha) for linha in matriz_dist])/len(matriz_dist)**2)
    matriz_fero = inicializar_feromonios(matriz_dist, tau0)
    melhor_rota = None
    melhor_custo = float('inf')
    
    for _ in range(max_iter):
        rotas = []
        custos = []
        for _ in range(num_formigas):
            rota = [random.randint(0, dimensao-1)]
            visitados = set(rota)
            probs = calcular_probabilidades(matriz_dist, matriz_fero, alfa, beta)
            
            while len(rota) < dimensao:
                prox = selecionar_proximo_no(rota[-1], probs, visitados)
                if prox is None:
                    break
                rota.append(prox)
                visitados.add(prox)
            
            rota.append(rota[0])
            custo = calcular_custo_rota(rota, matriz_dist)
            rotas.append(rota)
            custos.append(custo)
            
            if custo < melhor_custo:
                melhor_custo = custo
                melhor_rota = rota
        
        atualizar_feromonios(matriz_fero, rotas, custos, rho, Q)
    
    return melhor_rota, melhor_custo, nos  # Retorna a lista de nós

def main():
    diretorio = 'tsp'
    arquivo = selecionar_arquivo_tsp(diretorio)
    caminho_completo = os.path.join(diretorio, arquivo)
    
    # Configuração de hiperparâmetros
    print("\nConfiguração dos hiperparâmetros:\n")
    num_formigas = int(input("Número de formigas (padrão=20): ") or 20)
    max_iter = int(input("Número máximo de iterações (padrão=100): ") or 100)
    alfa = float(input("Valor de alfa (feromônios, padrão=1): ") or 1)
    beta = float(input("Valor de beta (heurística, padrão=2): ") or 2)
    rho = float(input("Taxa de evaporação rho (padrão=0.5): ") or 0.5)
    Q = float(input("Constante de atualização Q (padrão=100): ") or 100)
    
    for i in range(100): # loop para realizar os 100 testes
        print(f'~~~~~~Teste {i+1}~~~~~~~~')
        inicio = time.time()
        rota, custo, nos = colonia_de_formigas(
            caminho_completo,
            num_formigas=num_formigas,
            max_iter=max_iter,
            alfa=alfa,
            beta=beta,
            rho=rho,
            Q=Q
        )
        tempo = time.time() - inicio
        
        # Formatação da rota
        rota_nos = [nos[i] for i in rota]
        rota_formatada = ' -> '.join(rota_nos)
        
        print(f"\nMelhor rota encontrada: {rota_formatada}")
        print(f"Custo: {custo}")
        print(f"Tempo de execução: {round(tempo * 1000, 3)} milissegundos\n")

if __name__ == "__main__":
    main()
