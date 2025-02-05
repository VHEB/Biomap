from django.contrib.auth.views import LoginView
from django.urls import path
from .views import cadastro_usuario

urlpatterns = [
    path('cadastro/', cadastro_usuario, name='cadastro_usuario'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
]
