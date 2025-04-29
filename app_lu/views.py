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

import numpy as np
from fractions import Fraction

def to_fraction(val):
    return str(Fraction(val).limit_denominator())

def lu_step_by_step(A):
    n = A.shape[0]
    L = np.zeros_like(A, dtype=float)
    U = np.zeros_like(A, dtype=float)
    passos_U = []
    passos_L = []

    for i in range(n):
        # Passos para U (linha i)
        for j in range(i, n):
            soma = sum(L[i, k] * U[k, j] for k in range(i))
            termos_soma = [f"{to_fraction(L[i, k])} \\times {to_fraction(U[k, j])}" for k in range(i)]
            termos_str = " + ".join(termos_soma) if termos_soma else "0"
            U[i, j] = A[i, j] - soma

            explicacao = f"""
            \\[
            U_{{{i+1},{j+1}}} = A_{{{i+1},{j+1}}} - ({termos_str}) = {to_fraction(A[i,j])} - ({to_fraction(soma)}) = {to_fraction(U[i,j])}
            \\]
            """
            passos_U.append(explicacao)

        # Diagonal de L é 1
        L[i, i] = 1
        passos_L.append(f"\\[ L_{{{i+1},{i+1}}} = 1 \\]")

        # Passos para L (coluna i)
        for j in range(i+1, n):
            soma = sum(L[j, k] * U[k, i] for k in range(i))
            termos_soma = [f"{to_fraction(L[j, k])} \\times {to_fraction(U[k, i])}" for k in range(i)]
            termos_str = " + ".join(termos_soma) if termos_soma else "0"

            if U[i, i] == 0:
                raise ValueError("Matriz singular: fatoração LU impossível.")

            L[j, i] = (A[j, i] - soma) / U[i, i]

            explicacao = f"""
            \\[
            L_{{{j+1},{i+1}}} = \\frac{{A_{{{j+1},{i+1}}} - ({termos_str})}}{{{to_fraction(U[i,i])}}} = \\frac{{{to_fraction(A[j,i])} - {to_fraction(soma)}}}{{{to_fraction(U[i,i])}}} = {to_fraction(L[j,i])}
            \\]
            """
            passos_L.append(explicacao)

    return L, U, passos_L, passos_U


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

                L, U, passos_L, passos_U = lu_step_by_step(A)


                # Converter para frações
                A_frac = [[to_fraction(x) for x in row] for row in A]
                L_frac = [[to_fraction(np.round(x, 10)) for x in row] for row in L]
                U_frac = [[to_fraction(np.round(x, 10)) for x in row] for row in U]



                return render(request, 'app_lu/resultado.html', {
                    'A': A_frac,
                    'L': L_frac,
                    'U': U_frac,
                    'passos_L': passos_L,
                    'passos_U': passos_U
                })


    else:
        form = MatrixForm()

    return render(request, 'app_lu/home.html', {'form': form})
