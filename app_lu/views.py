from django.shortcuts import render
from .forms import MatrixForm
import numpy as np
from fractions import Fraction

# Função para conversão segura de string para float
def safe_float_conversion(value):
    try:
        return float(value)
    except ValueError:
        return 0.0

# Função para converter decimal para fração
def to_fraction(value):
    if float(value).is_integer():
        return str(int(value))
    else:
        return str(Fraction(value).limit_denominator(10000))

# Função que realiza a decomposição LU passo a passo
def lu_step_by_step(A):
    n = A.shape[0]
    L = np.zeros_like(A)
    U = np.zeros_like(A)
    passos = []

    for i in range(n):
        # Preencher a linha da matriz U
        for j in range(i, n):
            soma = sum(L[i, k] * U[k, j] for k in range(i))
            U[i, j] = A[i, j] - soma

            explicacao = f"""
            \\[
            U_{{{i+1},{j+1}}} = {A[i,j]} - ({' + '.join([f'{to_fraction(L[i,k])} \\times {to_fraction(U[k,j])}' for k in range(i)]) if i > 0 else '0'}) = {to_fraction(U[i,j])}
            \\]
            """
            passos.append(explicacao)

        # Preencher a coluna da matriz L
        L[i, i] = 1
        passos.append(f"\\[ L_{{{i+1},{i+1}}} = 1 \\]")

        for j in range(i+1, n):
            soma = sum(L[j, k] * U[k, i] for k in range(i))
            if U[i, i] == 0:
                raise ValueError("Matriz singular: fatoração LU impossível.")
            L[j, i] = (A[j, i] - soma) / U[i, i]

            explicacao = f"""
            \\[
            L_{{{j+1},{i+1}}} = \\frac{{{A[j,i]} - ({' + '.join([f'{to_fraction(L[j,k])} \\times {to_fraction(U[k,i])}' for k in range(i)]) if i > 0 else '0'})}}{{{to_fraction(U[i,i])}}} = {to_fraction(L[j,i])}
            \\]
            """
            passos.append(explicacao)

    return L, U, passos


# Função principal para o request
def home(request):
    if request.method == 'POST':
        form = MatrixForm(request.POST)
        if form.is_valid():
            linhas = form.cleaned_data['linhas']
            colunas = form.cleaned_data['colunas']
            matriz_texto = form.cleaned_data['matriz']

            linhas_texto = matriz_texto.strip().split(';')

            if len(linhas_texto) != linhas:
                form.add_error('matriz', 'O número de linhas não corresponde ao valor informado.')
            else:
                matriz = []
                for linha in linhas_texto:
                    valores = linha.strip().split(',')
                    if len(valores) != colunas:
                        form.add_error('matriz', 'O número de colunas não corresponde ao valor informado.')
                    matriz.append([safe_float_conversion(x) for x in valores])

                A = np.array(matriz)

                if A.shape[0] != A.shape[1]:
                    form.add_error('matriz', 'A matriz deve ser quadrada para realizar a fatoração LU.')
                    return render(request, 'app_lu/home.html', {'form': form})

                L, U, passos = lu_step_by_step(A)

                # Converter para frações
                A_frac = [[to_fraction(x) for x in row] for row in A]
                L_frac = [[to_fraction(x) for x in row] for row in np.round(L, decimals=6)]
                U_frac = [[to_fraction(x) for x in row] for row in np.round(U, decimals=6)]

                return render(request, 'app_lu/resultado.html', {
                    'A': A_frac,
                    'L': L_frac,
                    'U': U_frac,
                    'passos': passos
                })

    else:
        form = MatrixForm()

    return render(request, 'app_lu/home.html', {'form': form})
