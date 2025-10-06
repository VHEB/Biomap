from django.contrib.auth.views import LoginView
from django.urls import path
from .views import index, cadastro_usuario, cadastro_animal, perfil_usuario, editar_usuario, pesquisa_animal, resultado_pesquisa, autocomplete, sair, sobre, contato

urlpatterns = [
    path('', index, name='index'),
    path('cadastro/', cadastro_usuario, name='cadastro_usuario'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('cadastro-animal/', cadastro_animal, name='cadastro_animal'),
    path('perfil/', perfil_usuario, name='perfil_usuario'),
    path('logout/', sair, name='logout'),
    path('editar-usuario/', editar_usuario, name='editar_usuario'),
    path("pesquisa/", pesquisa_animal, name="pesquisa"),
    path("autocomplete/", autocomplete, name="animal-autocomplete"),
    path("resultado/<str:nome_cientifico>/", resultado_pesquisa, name="resultado_pesquisa"),
    path("sobre/", sobre, name="sobre"),
    path("contato/", contato, name="contato"),
]
