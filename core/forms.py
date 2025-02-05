from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario

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
