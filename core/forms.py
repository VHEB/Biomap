from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Usuario, Animal, Pesquisador, InstituicaoEducacao

# Obtém o modelo de usuário configurado
User = get_user_model() 



class CadastroUsuarioForm(UserCreationForm):
    
    # === CAMPOS BASE PERSONALIZADOS ===
    tipo_usuario = forms.ChoiceField(
        choices=[
            ('comum', 'Usuário Comum'),
            ('pesquisador', 'Pesquisador'),
            ('instituicao', 'Instituição de Educação')
        ],
        label="Tipo de Usuário"
    )
    email = forms.EmailField(label="E-mail", required=True)

    # === CAMPOS EXTRAS PARA PESQUISADOR ===
    data_nascimento = forms.DateField(
        label="Data de Nascimento", required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    formacao = forms.CharField(label="Formação", max_length=255, required=False)
    instituicao_atuante = forms.CharField(label="Instituição Atuante", max_length=255, required=False)
    lattes = forms.URLField(label="Currículo Lattes", required=False)

    # === CAMPOS EXTRAS PARA INSTITUIÇÃO ===
    nome_instituicao = forms.CharField(label="Nome da Instituição", max_length=255, required=False)
    cnpj = forms.CharField(label="CNPJ", max_length=18, required=False)
    endereco = forms.CharField(label="Endereço", widget=forms.Textarea, required=False)
    contato = forms.CharField(label="Contato", max_length=50, required=False)
    website = forms.URLField(label="Website", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # ✅ NOVO: Adiciona help_text para a primeira senha (password)
        if 'password' in self.fields:
             self.fields['password'].help_text = '''
                Sua senha não pode ser parecida com outras informações pessoais. 
                Deve conter pelo menos 8 caracteres, incluindo letras, números e símbolos (@, !, #, $, etc.).
            '''
        
        # Garante que os campos de nome sejam obrigatórios, pois o UserCreationForm os omite por padrão
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    # === VALIDAÇÕES (CLEAN METHODS) ===

    def clean_username(self):
        # Garante que o username seja único
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nome de usuário já está em uso.")
        return username

    def clean_email(self):
        # Garante que o email seja único
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado.")
        return email

    # === LÓGICA DE SALVAMENTO (SAVE) ===

    def save(self, commit=True):
        # 1. Salva o usuário base (que é o modelo Usuario)
        user = super().save(commit=False)
        user.tipo_usuario = self.cleaned_data['tipo_usuario']
        user.email = self.cleaned_data['email'] 
        
        if commit:
            # Precisa salvar o objeto base para obter o 'id' que será referenciado
            user.save()

            # 2. Cria o perfil extra (Pesquisador ou InstituicaoEducacao) usando herança
            tipo = self.cleaned_data.get('tipo_usuario')
            
            if tipo == 'pesquisador':
                # Cria a instância Pesquisador, preenchendo os campos extras
                # A herança de múltiplos modelos (multi-table inheritance) faz a ligação via PK/OneToOne
                Pesquisador.objects.create(
                    usuario_ptr=user, 
                    data_nascimento=self.cleaned_data.get('data_nascimento'),
                    formacao=self.cleaned_data.get('formacao'),
                    instituicao_atuante=self.cleaned_data.get('instituicao_atuante'),
                    lattes=self.cleaned_data.get('lattes'),
                    # É necessário passar os campos herdados para garantir a integridade da tabela filha
                    username=user.username, email=user.email, first_name=user.first_name, 
                    last_name=user.last_name, tipo_usuario=user.tipo_usuario,
                )
                
            elif tipo == 'instituicao':
                # Cria a instância InstituicaoEducacao, preenchendo os campos extras
                InstituicaoEducacao.objects.create(
                    usuario_ptr=user,
                    nome=self.cleaned_data.get('nome_instituicao'),
                    cnpj=self.cleaned_data.get('cnpj'),
                    endereco=self.cleaned_data.get('endereco'),
                    contato=self.cleaned_data.get('contato'),
                    website=self.cleaned_data.get('website'),
                    # Campos herdados:
                    username=user.username, email=user.email, first_name=user.first_name, 
                    last_name=user.last_name, tipo_usuario=user.tipo_usuario,
                )

        return user

    class Meta(UserCreationForm.Meta):
        model = Usuario
        # Incluir TODOS os campos (base e customizados)
        fields = ('username', 'email', 'first_name', 'last_name', 'tipo_usuario',
                  'data_nascimento', 'formacao', 'instituicao_atuante', 'lattes',
                  'nome_instituicao', 'cnpj', 'endereco', 'contato', 'website')

    tipo_usuario = forms.ChoiceField(
        choices=[
            ('comum', 'Usuário Comum'),
            ('pesquisador', 'Pesquisador'),
            ('instituicao', 'Instituição de Educação')
        ],
        label="Tipo de Usuário"
    )
    email = forms.EmailField(label="E-mail", required=True)

    # Campos extras para pesquisador
    data_nascimento = forms.DateField(
        label="Data de Nascimento", required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    formacao = forms.CharField(label="Formação", max_length=255, required=False)
    instituicao_atuante = forms.CharField(label="Instituição Atuante", max_length=255, required=False)
    lattes = forms.URLField(label="Currículo Lattes", required=False)

    # Campos extras para instituição
    nome_instituicao = forms.CharField(label="Nome da Instituição", max_length=255, required=False)
    cnpj = forms.CharField(label="CNPJ", max_length=18, required=False)
    endereco = forms.CharField(label="Endereço", widget=forms.Textarea, required=False)
    contato = forms.CharField(label="Contato", max_length=50, required=False)
    website = forms.URLField(label="Website", required=False)

    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'password1', 'password2',
            'tipo_usuario', 'data_nascimento', 'formacao',
            'instituicao_atuante', 'lattes',
            'nome_instituicao', 'cnpj', 'endereco', 'contato', 'website'
        ]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado.")
        return email

    def save(self, commit=True):
        usuario = super().save(commit=False)
        tipo = self.cleaned_data.get('tipo_usuario')
        usuario.tipo_usuario = tipo
        usuario.email = self.cleaned_data.get('email')

        if commit:
            usuario.save()

            # Criar registros extras dependendo do tipo
            if tipo == 'pesquisador':
                Pesquisador.objects.create(
                    username=usuario.username,
                    email=usuario.email,
                    tipo_usuario='pesquisador',
                    data_nascimento=self.cleaned_data.get('data_nascimento'),
                    formacao=self.cleaned_data.get('formacao'),
                    instituicao_atuante=self.cleaned_data.get('instituicao_atuante'),
                    lattes=self.cleaned_data.get('lattes'),
                )

            elif tipo == 'instituicao':
                InstituicaoEducacao.objects.create(
                    username=usuario.username,
                    email=usuario.email,
                    tipo_usuario='instituicao',
                    nome=self.cleaned_data.get('nome_instituicao'),
                    cnpj=self.cleaned_data.get('cnpj'),
                    endereco=self.cleaned_data.get('endereco'),
                    contato=self.cleaned_data.get('contato'),
                    website=self.cleaned_data.get('website'),
                )

        return usuario
    tipo_usuario = forms.ChoiceField(
        choices=[
            ('comum', 'Usuário Comum'),
            ('pesquisador', 'Pesquisador'),
            ('instituicao', 'Instituição de Educação')
        ],
        label="Tipo de Usuário"
    )

    # Campos básicos comuns
    email = forms.EmailField(label="E-mail")
    first_name = forms.CharField(label="Nome", max_length=150)
    last_name = forms.CharField(label="Sobrenome", max_length=150)

    # Campos adicionais para pesquisador
    data_nascimento = forms.DateField(label="Data de Nascimento", required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    formacao = forms.CharField(label="Formação", max_length=255, required=False)
    instituicao_atuante = forms.CharField(label="Instituição Atuante", max_length=255, required=False)
    lattes = forms.URLField(label="Currículo Lattes", required=False)

    # Campos adicionais para instituição
    nome_instituicao = forms.CharField(label="Nome da Instituição", max_length=255, required=False)
    cnpj = forms.CharField(label="CNPJ", max_length=18, required=False)
    endereco = forms.CharField(label="Endereço", widget=forms.Textarea, required=False)
    contato = forms.CharField(label="Contato", max_length=50, required=False)
    website = forms.URLField(label="Website", required=False)

    class Meta:
        model = Usuario  # ou User, se estiver usando o padrão
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'tipo_usuario', 'data_nascimento', 'formacao',
            'instituicao_atuante', 'lattes', 'nome_instituicao',
            'cnpj', 'endereco', 'contato', 'website',
        ]

    def save(self, commit=True):
        tipo = self.cleaned_data.get("tipo_usuario")
        usuario_base = super().save(commit=False)
        usuario_base.tipo_usuario = tipo
        usuario_base.email = self.cleaned_data.get("email")

        if commit:
            usuario_base.save()

            # Cria submodelo conforme tipo
            if tipo == "pesquisador":
                Pesquisador.objects.create(
                    id=usuario_base.id,
                    username=usuario_base.username,
                    email=usuario_base.email,
                    tipo_usuario=tipo,
                    data_nascimento=self.cleaned_data.get("data_nascimento"),
                    formacao=self.cleaned_data.get("formacao"),
                    instituicao_atuante=self.cleaned_data.get("instituicao_atuante"),
                    lattes=self.cleaned_data.get("lattes"),
                )
            elif tipo == "instituicao":
                InstituicaoEducacao.objects.create(
                    id=usuario_base.id,
                    username=usuario_base.username,
                    email=usuario_base.email,
                    tipo_usuario=tipo,
                    nome=self.cleaned_data.get("nome_instituicao"),
                    cnpj=self.cleaned_data.get("cnpj"),
                    endereco=self.cleaned_data.get("endereco"),
                    contato=self.cleaned_data.get("contato"),
                    website=self.cleaned_data.get("website"),
                )
        return usuario_base
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
