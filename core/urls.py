from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from .views import index, cadastro_usuario, cadastro_animal, perfil_usuario

urlpatterns = [
    path('', index, name='index'),
    path('cadastro/', cadastro_usuario, name='cadastro_usuario'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('cadastro-animal/', cadastro_animal, name='cadastro_animal'),
    path('perfil/', perfil_usuario, name='perfil_usuario'),
    path('logout/', LogoutView.as_view(next_page='/login/'), name='logout'),
    path('editar-usuario/', cadastro_usuario, name='editar_usuario'),
]
