# core/admin.py
from django.contrib import admin
from .models import Usuario, InstituicaoEducacao, UsuarioComum, Pesquisador, Animal

admin.site.register(Usuario)
admin.site.register(InstituicaoEducacao)
admin.site.register(UsuarioComum)
admin.site.register(Pesquisador)
admin.site.register(Animal)
