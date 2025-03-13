import random
import os
import time

# Função que retorna um dicionário de arquivos TSP a partir de um diretório
def arquivos_tsp(dir_tsp):
    # Lista os arquivos no diretório e cria um dicionário numerado
    dic_arquivos = {str(i + 1): arquivo for i, arquivo in enumerate(sorted(os.listdir(dir_tsp)))}
    return dic_arquivos

# Função para selecionar um arquivo TSP do diretório
def sel_arq_tsp(dir_tsp):
    dic_arquivos = arquivos_tsp(dir_tsp)
    print('\n Arquivos TSP localizados: \n')
    for numero, arquivo in dic_arquivos.items():
        print(f'{numero} - {arquivo}')  # Exibe os arquivos disponíveis
    print()
    num_arquivo = 0
    while num_arquivo not in dic_arquivos:  # Escolha do arquivo que será testado
        num_arquivo = input('Informe o número do arquivo TSP que deseja analisar: ')
    return dic_arquivos[num_arquivo]  # Retorna o arquivo escolhido

# Calcula a distância euclidiana entre dois pontos
def distancia_euclidiana(x1, y1, x2, y2):
    return ((x2 - x1)**2 + (y2 - y1)**2) ** 0.5

# Cálculo do fitness (Aptidão)
def fitness(dic_pontos, matriz_distancias, tipo_distancia, populacao):
    fitness_populacao = []
    for individuo in populacao:
        soma_dist = 0.0
        for j in range(len(individuo)):
            pt_atual = individuo[j]
            if j == len(individuo) - 1:
                pt_proximo = individuo[0]  # Fecha o ciclo
            else:
                pt_proximo = individuo[j + 1]
            if tipo_distancia == 'EUC_2D':
                x1, y1 = dic_pontos[pt_atual]
                x2, y2 = dic_pontos[pt_proximo]
                dist = distancia_euclidiana(x1, y1, x2, y2)
            elif tipo_distancia == 'EXPLICIT':
                i = int(pt_atual) - 1
                j_idx = int(pt_proximo) - 1
                dist = matriz_distancias[i][j_idx]
            soma_dist += dist
        fitness_individuo = [soma_dist, individuo]
        fitness_populacao.append(fitness_individuo)
    fitness_populacao.sort(key=lambda x: x[0])  # Ordena pelo menor fitness
    return fitness_populacao

# Método da roleta
def roleta(populacao, tx_de_reproducao):
    pop = populacao.copy()
    cont = 0
    pais = []
    taxa = int(len(populacao) * ((tx_de_reproducao/2) / 100))
    
    while cont < taxa:
        pai = []
        for _ in range(2):
            limite = pop[int(len(pop)/2)][3] if len(pop) > 0 else 0
            roleta_ponteiro = round(random.uniform(0, limite), 2)
            for j in range(len(pop)):
                if j == 0:
                    if roleta_ponteiro <= pop[j][3]:
                        pai.append(pop[j])
                        pop.pop(j)
                        break
                else:
                    if pop[j-1][3] < roleta_ponteiro <= pop[j][3]:
                        pai.append(pop[j])
                        pop.pop(j)
                        break
        pais.append(pai)
        cont += 1
    return pais

# Crossover
def crossover(dic_pontos, matriz_distancias, tipo_distancia, pais, prob_de_mutacao):
    nova_populacao = []
    ponto_corte = random.randint(1, len(pais[0][0][1])-1) if pais else 0
    for par in pais:
        if len(par) < 2:
            continue
        pai_1 = par[0][1]
        pai_2 = par[1][1]
        filho_1 = pai_1[:ponto_corte] + pai_2[ponto_corte:]
        filho_2 = pai_2[:ponto_corte] + pai_1[ponto_corte:]
        filho_1 = mutacao(filho_1, prob_de_mutacao)
        filho_2 = mutacao(filho_2, prob_de_mutacao)
        organizar_filho(pai_1, filho_1)
        organizar_filho(pai_2, filho_2)
        nova_populacao.append(filho_1)
        nova_populacao.append(filho_2)
    nova_populacao = fitness(dic_pontos, matriz_distancias, tipo_distancia, nova_populacao)
    return nova_populacao

# Mutação
def mutacao(filho, tx_de_mutacao):
    if random.uniform(0.0, 1.0) < tx_de_mutacao:
        id1, id2 = random.sample(range(len(filho)), 2)
        filho[id1], filho[id2] = filho[id2], filho[id1]
    return filho

# Organiza o filho para remover repetições
def organizar_filho(pai, filho):
    faltantes = [p for p in pai if p not in filho]
    duplicados = []
    visto = set()
    for i, p in enumerate(filho):
        if p in visto:
            duplicados.append(i)
        else:
            visto.add(p)
    for i in duplicados:
        if faltantes:
            filho[i] = faltantes.pop()
    return filho

# Ajuste da população
def ajuste_populacional(populacao, tamanho_populacao):
    while len(populacao) > tamanho_populacao:
        i = random.randint(0, len(populacao)-1)
        populacao.pop(i)
    return populacao

# Algoritmo genético
def alg_genetico(dic_pontos, matriz_distancias, tipo_distancia, pontos, tamanho_populacao, tx_de_reproducao, prob_de_mutacao, criterio_de_parada):
    # População inicial
    populacao = []
    for _ in range(tamanho_populacao):
        individuo = random.sample(pontos, len(pontos))
        populacao.append(individuo)
    populacao = fitness(dic_pontos, matriz_distancias, tipo_distancia, populacao)
    
    for geracao in range(criterio_de_parada):
        # Calcula fitness total e probabilidades
        fitness_total = sum(ind[0] for ind in populacao)
        for ind in populacao:
            ind.append(round(fitness_total / ind[0], 2))
            ind.append(round(ind[2] + (populacao.index(ind) * ind[2]), 2)) if populacao.index(ind) != 0 else ind.append(ind[2])
        
        # Seleção de pais
        pais = roleta(populacao, tx_de_reproducao)
        # Crossover e nova população
        nova_pop = crossover(dic_pontos, matriz_distancias, tipo_distancia, pais, prob_de_mutacao)
        populacao += nova_pop
        populacao = sorted(populacao, key=lambda x: x[0])
        populacao = ajuste_populacional(populacao, tamanho_populacao)
    
    return populacao

def main():
    # Parâmetros
    tamanho_populacao = 10
    tx_de_reproducao = 60
    prob_de_mutacao = 0.5
    criterio_de_parada = 80

    # Configurações do usuário
    tamanho_populacao = int(input('Tamanho da população (default 10): ') or 10)
    tx_de_reproducao = int(input('Taxa de reprodução (default 60): ') or 60)
    prob_de_mutacao = float(input('Probabilidade de mutação (default 0.5): ') or 0.5)
    criterio_de_parada = int(input('Critério de parada (default 80): ') or 80)

    dir_tsp = 'tsp'
    arq_tsp = sel_arq_tsp(dir_tsp)

    # Ler arquivo TSP
    with open(f'{dir_tsp}/{arq_tsp}', 'r') as file:
        linhas = file.read().splitlines()

    # Processar arquivo TSP
    dimensao = None
    tipo_distancia = None
    formato_matriz = None
    dic_pontos = {}
    matriz_distancias = None
    pontos = []

    # Inicialize as variáveis de controle
    ler_pontos = False
    ler_matriz = False

    for linha in linhas:
        if linha.startswith("DIMENSION"):
            dimensao = int(linha.split(":")[-1].strip())
        elif linha.startswith("EDGE_WEIGHT_TYPE"):
            tipo_distancia = linha.split(":")[-1].strip()
        elif linha.startswith("EDGE_WEIGHT_FORMAT"):
            formato_matriz = linha.split(":")[-1].strip()
        elif linha.startswith("NODE_COORD_SECTION"):
            ler_pontos = True
            continue
        elif linha.startswith("EDGE_WEIGHT_SECTION"):
            ler_matriz = True
            continue
        elif linha.startswith("EOF"):
            break

        if ler_pontos:
            partes = linha.split()
            if len(partes) >= 3:
                id_ponto = partes[0]
                x, y = float(partes[1]), float(partes[2])
                dic_pontos[id_ponto] = (x, y)
                pontos.append(id_ponto)
        elif ler_matriz:
            valores = list(map(float, linha.split()))
            if not matriz_distancias:
                matriz_distancias = [[0.0] * dimensao for _ in range(dimensao)]
                idx = 0
                for i in range(dimensao - 1):
                    for j in range(i + 1, dimensao):
                        if idx < len(valores):
                            matriz_distancias[i][j] = valores[idx]
                            matriz_distancias[j][i] = valores[idx]
                            idx += 1

    if tipo_distancia == 'EXPLICIT':
        pontos = [str(i+1) for i in range(dimensao)]
        dic_pontos = {p: None for p in pontos}

    # Executar algoritmo genético
    inicio = time.time()
    populacao_final = alg_genetico(dic_pontos, matriz_distancias, tipo_distancia, pontos, tamanho_populacao, tx_de_reproducao, prob_de_mutacao, criterio_de_parada)
    melhor = populacao_final[0]
    tempo = (time.time() - inicio) * 1000

    print(f"\nMelhor solução: {melhor[0]} | Rota: {melhor[1]}")
    print(f"Tempo de execução: {round(tempo, 2)} milissegundos")

if __name__ == '__main__':
    main()
