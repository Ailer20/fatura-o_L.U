from django.shortcuts import render
from .forms import MatrixForm
import numpy as np
from fractions import Fraction

# Conversão segura de string para float
def safe_float_conversion(value):
    try:
        return float(value)
    except ValueError:
        return 0.0

# Conversão para fração
def to_fraction(val):
    return str(Fraction(val).limit_denominator())

# Fatoração LU passo a passo
def lu_step_by_step(A):
    n = A.shape[0]
    L = np.zeros_like(A, dtype=float)
    U = np.zeros_like(A, dtype=float)
    passos_U = []
    passos_L = []

    for i in range(n):
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

        L[i, i] = 1
        passos_L.append(f"\\[ L_{{{i+1},{i+1}}} = 1 \\]")

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

# Resolver Ly = b
def resolver_Ly(L, b):
    n = len(b)
    y = np.zeros_like(b, dtype=float)
    passos_y = []

    for i in range(n):
        soma = sum(L[i][j] * y[j] for j in range(i))
        y[i] = b[i] - soma
        termos = " + ".join([f"{to_fraction(L[i][j])} \\cdot {to_fraction(y[j])}" for j in range(i)])
        termos = termos if termos else "0"
        passo = f"\\[ y_{{{i+1}}} = b_{{{i+1}}} - ({termos}) = {to_fraction(b[i])} - {to_fraction(soma)} = {to_fraction(y[i])} \\]"
        passos_y.append(passo)
    return y, passos_y

# Resolver Ux = y
def resolver_Ux(U, y):
    n = len(y)
    x = np.zeros_like(y, dtype=float)
    passos_x = []

    epsilon = 1e-10  # Regularização

    for i in reversed(range(n)):
        soma = sum(U[i][j] * x[j] for j in range(i + 1, n))
        if abs(U[i][i]) < epsilon:
            U[i][i] = epsilon
        x[i] = (y[i] - soma) / U[i][i]
        termos = " + ".join([f"{to_fraction(U[i][j])} \\cdot {to_fraction(x[j])}" for j in range(i + 1, n)])
        termos = termos if termos else "0"
        passo = f"\\[ x_{{{i+1}}} = \\frac{{y_{{{i+1}}} - ({termos})}}{{{to_fraction(U[i][i])}}} = \\frac{{{to_fraction(y[i])} - {to_fraction(soma)}}}{{{to_fraction(U[i][i])}}} = {to_fraction(x[i])} \\]"
        passos_x.append(passo)

    return x, passos_x

# Gerar vetor b automaticamente
def gerar_vetor_b(A):
    n = A.shape[0]
    x = np.ones(n)  # x padrão [1, 1, ..., 1]
    b = A @ x
    return b, x

# View principal
def home(request):
    if request.method == 'POST':
        form = MatrixForm(request.POST)
        if form.is_valid():
            linhas = form.cleaned_data['linhas']
            colunas = form.cleaned_data['colunas']
            matriz_texto = form.cleaned_data['matriz']
            vetor_b_texto = form.cleaned_data.get('vetor_b')

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

                # Vetores e passos
                b_frac = y_frac = x_frac = []
                passos_y = passos_x = []
                x_gerado_frac = []

                if vetor_b_texto:
                    b_lista = [safe_float_conversion(x) for x in vetor_b_texto.strip().split(',')]
                    if len(b_lista) != A.shape[0]:
                        form.add_error('vetor_b', 'O vetor b deve ter o mesmo número de linhas da matriz A.')
                        return render(request, 'app_lu/home.html', {'form': form})
                    b = np.array(b_lista)
                    x = None
                else:
                    b, x = gerar_vetor_b(A)
                    x_gerado_frac = [to_fraction(val) for val in x]

                y, passos_y = resolver_Ly(L, b)
                x_solucao, passos_x = resolver_Ux(U, y)

                b_frac = [to_fraction(val) for val in b]
                y_frac = [to_fraction(val) for val in y]
                x_frac = [to_fraction(val) for val in x_solucao]

                A_frac = [[to_fraction(x) for x in row] for row in A]
                L_frac = [[to_fraction(np.round(x, 10)) for x in row] for row in L]
                U_frac = [[to_fraction(np.round(x, 10)) for x in row] for row in U]

                return render(request, 'app_lu/resultado.html', {
                    'A': A_frac,
                    'L': L_frac,
                    'U': U_frac,
                    'passos_L': passos_L,
                    'passos_U': passos_U,
                    'passos_y': passos_y,
                    'passos_x': passos_x,
                    'b': b_frac,
                    'y': y_frac,
                    'x': x_frac,
                    'x_gerado': x_gerado_frac,
                })

    else:
        form = MatrixForm()

    return render(request, 'app_lu/home.html', {'form': form})
