from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from .views import index, cadastro_usuario, cadastro_animal, perfil_usuario, editar_usuario, pesquisa_animal, resultado_pesquisa, animal_suggestions

urlpatterns = [
    path('', index, name='index'),
    path('cadastro/', cadastro_usuario, name='cadastro_usuario'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('cadastro-animal/', cadastro_animal, name='cadastro_animal'),
    path('perfil/', perfil_usuario, name='perfil_usuario'),
    path('logout/', LogoutView.as_view(next_page='/login/'), name='logout'),
    path('editar-usuario/', editar_usuario, name='editar_usuario'),
    path("pesquisa/", pesquisa_animal, name="pesquisa"),
    path("autocomplete/", animal_suggestions, name="animal-autocomplete"),
    path("resultado/", resultado_pesquisa, name="resultado_pesquisa"),
]
