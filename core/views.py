from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CadastroUsuarioForm, CadastroAnimalForm

def index(request):
    return render(request, 'index.html')

@login_required
def perfil_usuario(request):
    # Como o usuário está autenticado, request.user contém suas informações.
    return render(request, 'perfil_usuario.html', {'usuario': request.user})

def cadastro_usuario(request):
    if request.method == 'POST':
        form = CadastroUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cadastro realizado com sucesso!')
            return redirect('login')  # Redirecionar para a página de login ou home
        else:
            messages.error(request, 'Erro ao realizar cadastro. Verifique os dados informados.')
    else:
        form = CadastroUsuarioForm()
    
    return render(request, 'cadastro_usuario.html', {'form': form})


def cadastro_animal(request):
    if request.method == 'POST':
        form = CadastroAnimalForm(request.POST)
        if form.is_valid():
            animal = form.save(commit=False)
            # Atribui o usuário que está logado como responsável pelo cadastro
            animal.cadastrado_por = request.user
            animal.save()
            messages.success(request, "Animal cadastrado com sucesso!")
            return redirect('cadastro_animal')  # Você pode redirecionar para outra página, se preferir
        else:
            messages.error(request, "Erro ao cadastrar animal. Verifique os dados e tente novamente.")
    else:
        form = CadastroAnimalForm()
    
    return render(request, 'cadastro_animal.html', {'form': form})

