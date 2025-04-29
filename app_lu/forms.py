from django import forms

class MatrixForm(forms.Form):
    linhas = forms.IntegerField(
        label="Número de Linhas", 
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    colunas = forms.IntegerField(
        label="Número de Colunas", 
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    matriz = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'cols': 30}),
        label="Valores da Matriz",
    )
