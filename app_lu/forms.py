# forms.py
from django import forms

class MatrixForm(forms.Form):
    linhas = forms.IntegerField()
    colunas = forms.IntegerField()
    matriz = forms.CharField(widget=forms.Textarea)
