from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Animal

class CadastroUsuarioForm(UserCreationForm):
    email = forms.EmailField(required=True)
    tipo_usuario = forms.ChoiceField(choices=[
        ('comum', 'Usuário Comum'),
        ('pesquisador', 'Pesquisador'),
        ('instituicao', 'Instituição de Educação')
    ])

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'tipo_usuario', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("As senhas não conferem.")
        return cleaned_data


class EditarPerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email']


class CadastroAnimalForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = [
            'reino', 'filo', 'classe', 'ordem', 'familia', 'genero', 'nome_cientifico',
            'nome_cientifico_anterior', 'autor', 'nome_comum', 'grupo', 'mes_ano_avaliacao',
            'categoria', 'possivelmente_extinta', 'criterio', 'justificativa', 'endemica_brasil',
            'consta_lista_nacional_oficial', 'estado', 'regiao', 'bioma', 'bacia_hidrografica',
            'uc_federal', 'uc_estadual', 'rppn', 'migratoria', 'tendencia_populacional', 'ameaca',
            'uso', 'acao_conservacao', 'plano_acao', 'listas_convencoes'
        ]
        widgets = {
            'possivelmente_extinta': forms.CheckboxInput(),
            'endemica_brasil': forms.CheckboxInput(),
            'consta_lista_nacional_oficial': forms.CheckboxInput(),
            'migratoria': forms.CheckboxInput()
        }
    
    def clean_nome_cientifico(self):
        nome_cientifico = self.cleaned_data.get('nome_cientifico')
        if Animal.objects.filter(nome_cientifico=nome_cientifico).exists():
            raise forms.ValidationError("Já existe um animal cadastrado com esse nome científico.")
        return nome_cientifico
