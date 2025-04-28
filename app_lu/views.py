from django.shortcuts import render
from .forms import MatrixForm
import numpy as np
from fractions import Fraction

# Função para conversão segura de string para float
def safe_float_conversion(value):
    try:
        return float(value)
    except ValueError:
        return 0.0  # Ou outro valor padrão, dependendo da sua lógica

# Função para converter decimal para fração, mas manter números inteiros
def to_fraction(value):
    if value.is_integer():
        return str(int(value))  # Retorna como número inteiro
    else:
        return str(Fraction(value).limit_denominator(10000))

# Função que realiza a decomposição LU manualmente
def lu_step_by_step(A):
    n = A.shape[0]  # Número de linhas
    L = np.zeros_like(A)
    U = np.zeros_like(A)

    # Fatoração LU
    for i in range(n):
        # Preencher a linha da matriz U
        for j in range(i, n):
            U[i, j] = A[i, j] - np.dot(L[i, :i], U[:i, j])

        # Preencher a coluna da matriz L
        L[i, i] = 1  # A diagonal de L é sempre 1
        for j in range(i + 1, n):
            if U[i, i] != 0:
                L[j, i] = (A[j, i] - np.dot(L[j, :i], U[:i, i])) / U[i, i]
            else:
                raise ValueError("A matriz A não é invertível, portanto a decomposição LU não é possível.")

    return L, U

# Função principal para o request e processamento da matriz
def home(request):
    if request.method == 'POST':
        form = MatrixForm(request.POST)
        if form.is_valid():
            linhas = form.cleaned_data['linhas']
            colunas = form.cleaned_data['colunas']
            matriz_texto = form.cleaned_data['matriz']

            # Processar matriz
            linhas_texto = matriz_texto.strip().split(';')

            # Verificar se o número de linhas e colunas coincide com os dados inseridos
            if len(linhas_texto) != linhas:
                form.add_error('matriz', 'O número de linhas não corresponde ao valor informado.')
            else:
                matriz = []
                for linha in linhas_texto:
                    valores = linha.strip().split(',')
                    if len(valores) != colunas:
                        form.add_error('matriz', 'O número de colunas não corresponde ao valor informado.')
                    matriz.append([safe_float_conversion(x) for x in valores])

                # Converter a matriz para um array numpy
                A = np.array(matriz)

                # Verificar se a matriz A é quadrada
                if A.shape[0] != A.shape[1]:
                    form.add_error('matriz', 'A matriz deve ser quadrada para realizar a fatoração LU.')
                    return render(request, 'app_lu/home.html', {'form': form})

                # Fazer a fatoração LU passo a passo
                L, U = lu_step_by_step(A)

                # Ajustar para garantir que as matrizes sejam corretas
                L_fixed = np.round(L, decimals=6)  # Ajuste para mostrar os valores corretos com 6 casas decimais
                U_fixed = np.round(U, decimals=6)

                # Converter as matrizes para frações
                A_frac = [[to_fraction(x) for x in row] for row in A]
                L_frac = [[to_fraction(x) for x in row] for row in L_fixed]
                U_frac = [[to_fraction(x) for x in row] for row in U_fixed]

                return render(request, 'app_lu/resultado.html', {
                    'A': A_frac,
                    'L': L_frac,
                    'U': U_frac
                })

    else:
        form = MatrixForm()

    return render(request, 'app_lu/home.html', {'form': form})
