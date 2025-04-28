from django import forms

class MatrixForm(forms.Form):
    linhas = forms.IntegerField(label="Número de Linhas", min_value=1)
    colunas = forms.IntegerField(label="Número de Colunas", min_value=1)
    matriz = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'cols': 30}),
        label="Valores da Matriz",
        help_text="Insira os valores da matriz separados por vírgula em cada linha. Exemplo: 1,2,3;4,5,6;7,8,9"
    )
