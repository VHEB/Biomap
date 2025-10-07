from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .forms import CadastroUsuarioForm, CadastroAnimalForm, EditarPerfilForm
from .models import Animal
from django.db.models import Q
import requests
from django.core.cache import cache

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


def autocomplete(request):
    query = request.GET.get("q", "").strip()
    modo = request.GET.get("modo", "comum")

    if not query:
        return JsonResponse([], safe=False)

    if modo == "cientifico":
        resultados = Animal.objects.filter(
            nome_cientifico__icontains=query
        ).values_list("nome_cientifico", flat=True).distinct()
    else:
        resultados = Animal.objects.filter(
            nome_comum__icontains=query
        ).values_list("nome_comum", flat=True).distinct()

    if not resultados:
        return JsonResponse(["Nenhum resultado encontrado"], safe=False)

    return JsonResponse(list(resultados), safe=False)


def resultado_pesquisa(request, termo):
    termos = [t.strip() for t in termo.split(',')]
    consulta = Q()

    for t in termos:
        consulta |= Q(nome_comum__icontains=t) | Q(nome_cientifico__icontains=t)

    animais = Animal.objects.filter(consulta).distinct()

    for animal in animais:
        animal.imagem_url = buscar_imagem_animal(animal.nome_cientifico or animal.nome_comum)

    return render(request, "resultado_pesquisa.html", {"animais": animais, "termo": termo})

def buscar_imagem_animal(nome):
    nome = nome.strip()
    cache_key = f"img_{nome.lower()}"
    if cache.get(cache_key):
        return cache.get(cache_key)

    termos_busca = [
        nome,
        nome.capitalize(),
        nome.title(),
        nome.lower(),
    ]

    for termo in termos_busca:
        url = "https://commons.wikimedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "prop": "pageimages",
            "piprop": "original",
            "titles": termo,
        }
        try:
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            pages = data.get("query", {}).get("pages", {})
            for page in pages.values():
                if "original" in page:
                    image_url = page["original"]["source"]
                    cache.set(cache_key, image_url, timeout=86400)
                    return image_url
        except Exception as e:
            print(f"Erro ao buscar '{termo}': {e}")

    # fallback
    imagem_padrao = "/static/img/animais/sem-registro.jpg"
    cache.set(cache_key, imagem_padrao, timeout=86400)
    return imagem_padrao

    """
    Busca uma imagem pública do animal na Wikimedia Commons,
    com cache automático e fallback caso não encontre.
    """
    nome = nome.strip()
    cache_key = f"imagem_{nome.lower()}"
    
    # Verifica se já temos em cache
    if cache.get(cache_key):
        return cache.get(cache_key)
    
    url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "pageimages",
        "piprop": "original",
        "titles": nome
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        pages = data.get("query", {}).get("pages", {})

        for page in pages.values():
            if "original" in page:
                image_url = page["original"]["source"]
                cache.set(cache_key, image_url, timeout=86400)  # 24h de cache
                return image_url

    except Exception as e:
        print(f"[ERRO] Falha ao buscar imagem de '{nome}': {e}")

    # Retorna imagem padrão se não encontrar
    imagem_padrao = "/static/img/animais/sem-registro.jpg"
    cache.set(cache_key, imagem_padrao, timeout=86400)
    return imagem_padrao

def sair(request):
    logout(request)
    messages.info(request, "Você saiu da sua conta com sucesso.")
    return redirect('login')

def sobre(request):
    return render(request, 'sobre.html')

def contato(request):
    return render(request, 'contato.html')