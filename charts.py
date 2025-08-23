# charts.py
"""
Funções para geração de gráficos com matplotlib.
"""
import matplotlib.pyplot as plt

def grafico_gastos(dados):
    # dados: lista de tuplas (categoria, valor)
    categorias, valores = zip(*dados)
    plt.figure(figsize=(6,4))
    plt.bar(categorias, valores, color='royalblue')
    plt.title('Gastos por Categoria')
    plt.xlabel('Categoria')
    plt.ylabel('Valor')
    plt.tight_layout()
    plt.show()
