from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CadastroUsuarioForm, CadastroAnimalForm, EditarPerfilForm
from .models import Animal
from django.db.models import Q

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

@login_required
def editar_usuario(request):
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Dados atualizados com sucesso!")
            return redirect('perfil_usuario')
        else:
            messages.error(request, "Houve um problema ao atualizar os dados.")
    else:
        form = EditarPerfilForm(instance=request.user)
    
    return render(request, 'editar_usuario.html', {'form': form})


def pesquisa_animal(request):
    return render(request, "pesquisa.html")


def animal_suggestions(request):
    query = request.GET.get("q", "").strip()
    
    if query:
        animais = Animal.objects.filter(
            Q(nome_cientifico__icontains=query) | Q(nome_comum__icontains=query)
        )[:10]  # Limita a 10 sugestões

        suggestions = list(animais.values_list("nome_cientifico", flat=True))
        if not suggestions:
            suggestions = ["Nenhum resultado encontrado"]
    else:
        suggestions = []
    
    return JsonResponse(suggestions, safe=False)


def resultado_pesquisa(request, nome_cientifico):
    animais = Animal.objects.filter(
        Q(nome_cientifico__iexact=nome_cientifico) | Q(nome_comum__icontains=nome_cientifico)
    )
    return render(request, "resultado_pesquisa.html", {"animais": animais, "termo": nome_cientifico})