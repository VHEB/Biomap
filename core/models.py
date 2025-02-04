from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=128)
    tipo_usuario = models.CharField(max_length=20, choices=[
        ('comum', 'Usuário Comum'),
        ('pesquisador', 'Pesquisador'),
        ('instituicao', 'Instituição de Educação')
    ])

    def cadastrar(self):
        pass  # Implementar lógica

    def recuperar_senha(self):
        pass  # Implementar lógica

    def excluir_conta(self):
        pass  # Implementar lógica

class UsuarioComum(Usuario):
    def pesquisar_animais(self):
        pass

    def visualizar_resultados(self):
        pass

class InstituicaoEducacao(Usuario):
    nome = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18, unique=True)
    endereco = models.TextField()
    contato = models.CharField(max_length=50)
    website = models.URLField()

    def validar_dados(self):
        pass

class Pesquisador(Usuario):
    data_nascimento = models.DateField()
    formacao = models.CharField(max_length=255)
    instituicao_atuante = models.CharField(max_length=255)
    lattes = models.URLField()
    # Associação opcional com Instituição:
    instituicao = models.ForeignKey(InstituicaoEducacao, on_delete=models.SET_NULL, null=True, blank=True, related_name="pesquisadores")

    def cadastrar_animal(self, animal):
        pass

    def alterar_informacoes_animal(self, animal):
        pass

    def validar_dados(self):
        pass

class Animal(models.Model):
    reino = models.CharField(max_length=100)
    filo = models.CharField(max_length=100)
    classe = models.CharField(max_length=100)
    ordem = models.CharField(max_length=100)
    familia = models.CharField(max_length=100)
    genero = models.CharField(max_length=100)
    nome_cientifico = models.CharField(max_length=255)
    nome_cientifico_anterior = models.CharField(max_length=255, blank=True, null=True)
    autor = models.CharField(max_length=255)
    nome_comum = models.CharField(max_length=255)
    grupo = models.CharField(max_length=100)
    mes_ano_avaliacao = models.CharField(max_length=50)
    categoria = models.CharField(max_length=100)
    possivelmente_extinta = models.BooleanField(default=False)
    criterio = models.CharField(max_length=255)
    justificativa = models.TextField()
    endemica_brasil = models.BooleanField(default=False)
    consta_lista_nacional_oficial = models.BooleanField(default=False)
    estado = models.CharField(max_length=100)
    regiao = models.CharField(max_length=100)
    bioma = models.CharField(max_length=100)
    bacia_hidrografica = models.CharField(max_length=100)
    uc_federal = models.CharField(max_length=100)
    uc_estadual = models.CharField(max_length=100)
    rppn = models.CharField(max_length=100)
    migratoria = models.BooleanField(default=False)
    tendencia_populacional = models.CharField(max_length=100)
    ameaca = models.CharField(max_length=100)
    uso = models.CharField(max_length=100)
    acao_conservacao = models.TextField()
    plano_acao = models.TextField()
    listas_convencoes = models.TextField()
    # Relação de cadastro: tanto pesquisadores quanto instituições são usuários.
    cadastrado_por = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="animais")

    def cadastrar(self):
        pass

    def alterar(self):
        pass
