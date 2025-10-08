import re
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.cache import cache
from django.db.models import Q
from django.db.models.functions import Lower
from .forms import CadastroUsuarioForm, CadastroAnimalForm, EditarPerfilForm
from .models import Animal
from unidecode import unidecode

# ------------------ PÁGINAS BÁSICAS ------------------

def index(request):
    return render(request, 'index.html')


@login_required
def perfil_usuario(request):
    return render(request, 'perfil_usuario.html', {'usuario': request.user})


def cadastro_usuario(request):
    if request.method == 'POST':
        form = CadastroUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cadastro realizado com sucesso!')
            return redirect('login')
        else:
            messages.error(request, 'Erro ao realizar cadastro. Verifique os dados informados.')
    else:
        form = CadastroUsuarioForm()
    return render(request, 'cadastro_usuario.html', {'form': form})


@login_required
def editar_usuario(request):
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Dados atualizados com sucesso!")
            return redirect('perfil_usuario')
        else:
            messages.error(request, "Erro ao atualizar os dados.")
    else:
        form = EditarPerfilForm(instance=request.user)
    return render(request, 'editar_usuario.html', {'form': form})


@login_required
def cadastro_animal(request):
    if request.method == 'POST':
        form = CadastroAnimalForm(request.POST)
        if form.is_valid():
            animal = form.save(commit=False)
            animal.cadastrado_por = request.user
            animal.save()
            messages.success(request, "Animal cadastrado com sucesso!")
            return redirect('cadastro_animal')
        else:
            messages.error(request, "Erro ao cadastrar animal. Verifique os dados.")
    else:
        form = CadastroAnimalForm()
    return render(request, 'cadastro_animal.html', {'form': form})


# ------------------ PESQUISA ------------------

def pesquisa_animal(request):
    """Renderiza a página de pesquisa."""
    return render(request, "pesquisa.html")


def autocomplete(request):
    """Retorna sugestões com nome comum e nome científico."""
    query = request.GET.get("q", "").strip()
    modo = request.GET.get("modo", "comum")

    if len(query) < 2:
        return JsonResponse([], safe=False)

    if modo == "cientifico":
        animais = Animal.objects.filter(nome_cientifico__icontains=query)
    else:
        animais = Animal.objects.filter(nome_comum__icontains=query)

    resultados = [
        {"comum": a.nome_comum, "cientifico": a.nome_cientifico}
        for a in animais.distinct()[:10]
    ]

    return JsonResponse(resultados, safe=False)


def resultado_pesquisa(request, nome_cientifico):
    """
    Exibe o resultado da pesquisa do animal (com tolerância total de acentos e capitalização).
    """

    termo = unidecode(nome_cientifico.strip().lower())
    print(f"[DEBUG] Termo pesquisado: {termo}")

    # Pré-filtragem (ignora case e espaços extras)
    animais = Animal.objects.filter(
        Q(nome_cientifico__iexact=nome_cientifico.strip()) |
        Q(nome_cientifico__icontains=nome_cientifico.strip())
    )

    # 🔍 Se ainda não achou, aplica unidecode (busca sem acentuação)
    if not animais.exists():
        animais_candidatos = Animal.objects.all()
        correspondentes = [
            a for a in animais_candidatos
            if unidecode(a.nome_cientifico.strip().lower()) == termo
        ]
        if not correspondentes:
            correspondentes = [
                a for a in animais_candidatos
                if termo in unidecode(a.nome_cientifico.strip().lower())
            ]
        animais = correspondentes

    # 🐢 Se ainda não achou nada:
    if not animais:
        print(f"[WARN] Nenhum animal encontrado para: {nome_cientifico}")
        messages.warning(request, f"Nenhum registro encontrado para '{nome_cientifico}'.")
        return render(request, "resultado_pesquisa.html", {"animais": []})

    # 🦁 Achou o animal
    if isinstance(animais, list):
        animal = animais[0]
    else:
        animal = animais.first()

    print(f"[INFO] Animal encontrado: {animal.nome_cientifico}")

    # Busca imagem (com cache)
    animal.imagem_url = buscar_imagem_animal(animal.nome_cientifico)

    return render(request, "resultado_pesquisa.html", {"animal": animal})
    """
    Exibe o resultado da pesquisa com tolerância a acentos e capitalização.
    """
    termo = unidecode(nome_cientifico.strip().lower())

    # Busca ignorando acentuação e capitalização
    animais = Animal.objects.all()
    encontrado = None
    for a in animais:
        if unidecode(a.nome_cientifico.strip().lower()) == termo:
            encontrado = a
            break

    if not encontrado:
        messages.warning(request, f"Nenhum registro encontrado para '{nome_cientifico}'.")
        return render(request, "resultado_pesquisa.html", {"animais": []})

    # Busca imagem
    encontrado.imagem_url = buscar_imagem_animal(encontrado.nome_cientifico)

    return render(request, "resultado_pesquisa.html", {"animal": encontrado})

# ------------------ BUSCA DE IMAGEM ------------------

def buscar_imagem_animal(nome):
    """
    Busca uma imagem pública do animal na Wikimedia Commons.
    Usa cache e fallback para imagem padrão.
    """
    nome = nome.strip()
    cache_key = "img_" + re.sub(r'[^a-zA-Z0-9_]', '_', nome.lower())

    # Cache check
    if cache.get(cache_key):
        return cache.get(cache_key)

    base_url = "https://commons.wikimedia.org/w/api.php"
    termos_busca = [nome, nome.capitalize(), nome.title(), nome.lower()]

    for termo in termos_busca:
        params = {
            "action": "query",
            "format": "json",
            "prop": "pageimages",
            "piprop": "original",
            "titles": termo
        }
        try:
            response = requests.get(base_url, params=params, timeout=5)
            if response.status_code != 200:
                continue

            data = response.json()
            pages = data.get("query", {}).get("pages", {})
            for page in pages.values():
                if "original" in page:
                    image_url = page["original"]["source"]
                    cache.set(cache_key, image_url, timeout=86400)
                    return image_url

        except Exception as e:
            print(f"[ERRO] Falha ao buscar imagem de '{termo}': {e}")

    # Fallback padrão
    imagem_padrao = "/static/img/animais/sem-registro.jpg"
    cache.set(cache_key, imagem_padrao, timeout=86400)
    return imagem_padrao


# ------------------ OUTRAS PÁGINAS ------------------

def sair(request):
    logout(request)
    messages.info(request, "Você saiu da sua conta com sucesso.")
    return redirect('login')


def sobre(request):
    return render(request, 'sobre.html')


def contato(request):
    return render(request, 'contato.html')
