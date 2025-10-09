import re
import requests
import geopandas as gpd
import matplotlib.pyplot as plt
from pathlib import Path
from unidecode import unidecode

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.cache import cache
from django.db.models import Q

from .forms import CadastroUsuarioForm, CadastroAnimalForm, EditarPerfilForm
from .models import Animal


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
    return render(request, "pesquisa.html")


def autocomplete(request):
    """Retorna sugestões de nomes comuns ou científicos."""
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
    """Exibe o resultado da pesquisa e gera mapa e imagem do animal."""
    termo = unidecode(nome_cientifico.strip().lower())
    print(f"[DEBUG] Termo pesquisado: {termo}")

    # Busca ignorando acentos
    animal = None
    for a in Animal.objects.all():
        if unidecode(a.nome_cientifico.strip().lower()) == termo:
            animal = a
            break

    if not animal:
        messages.warning(request, f"Nenhum registro encontrado para '{nome_cientifico}'.")
        return render(request, "resultado_pesquisa.html", {"animal": None, "mapa_path": None})

    print(f"[INFO] Animal encontrado: {animal.nome_cientifico}")

    # 🖼️ Busca imagem
    animal.imagem_url = buscar_imagem_animal(animal.nome_cientifico)

    # 🗺️ Gera mapa se houver região
    mapa_path = None
    if animal.regiao and animal.regiao.strip():
        mapa_path = gerar_mapa_animal(animal.regiao, animal.nome_cientifico)

    return render(request, "resultado_pesquisa.html", {"animal": animal, "mapa_path": mapa_path})


# ------------------ BUSCA DE IMAGEM ------------------

def buscar_imagem_animal(nome):
    """Busca imagem pública na Wikimedia Commons."""
    nome = nome.strip()
    cache_key = "img_" + re.sub(r'[^a-zA-Z0-9_]', '_', nome.lower())

    imagem_em_cache = cache.get(cache_key)
    if imagem_em_cache:
        return imagem_em_cache

    base_url = "https://commons.wikimedia.org/w/api.php"
    headers = {"User-Agent": "BioMap/1.0 (https://biomap.example.com)"}
    termos = [nome, nome.title(), nome.lower()]

    for termo in termos:
        try:
            response = requests.get(base_url, params={
                "action": "query",
                "format": "json",
                "prop": "pageimages",
                "piprop": "original",
                "titles": termo
            }, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                for page in data.get("query", {}).get("pages", {}).values():
                    if "original" in page:
                        image_url = page["original"]["source"]
                        cache.set(cache_key, image_url, 86400)
                        print(f"[OK] Imagem encontrada para {nome}: {image_url}")
                        return image_url
        except Exception as e:
            print(f"[ERRO IMG] Falha ao buscar imagem de {nome}: {e}")

    imagem_padrao = "/static/img/animais/sem-registro.jpg"
    cache.set(cache_key, imagem_padrao, 86400)
    return imagem_padrao


# ------------------ MAPA ------------------

def gerar_mapa_animal(regioes, nome_cientifico):
    """Gera mapa destacando estados onde o animal ocorre."""
    try:
        pasta = Path("media/mapas")
        pasta.mkdir(parents=True, exist_ok=True)

        # ✅ URL corrigida — shapefile completo do Brasil (por UF)
        url_geojson = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
        brasil = gpd.read_file(url_geojson)

        # Normaliza estados
        if isinstance(regioes, str):
            regioes = [r.strip().upper() for r in regioes.split(",") if r.strip()]
        regioes_set = set(regioes)

        # Corrige nome da coluna com o estado (no shapefile é “name”)
        brasil["color"] = brasil["name"].apply(
            lambda uf: "green" if uf.upper() in regioes_set else "#DDDDDD"
        )

        # Cria o mapa
        fig, ax = plt.subplots(figsize=(8, 6))
        brasil.plot(ax=ax, color=brasil["color"], edgecolor="black")
        ax.set_title(f"Distribuição geográfica de {nome_cientifico}", fontsize=10)
        ax.axis("off")

        mapa_path = pasta / f"mapa_{nome_cientifico.replace(' ', '_')}.png"
        plt.savefig(mapa_path, bbox_inches="tight", dpi=150)
        plt.close(fig)
        print(f"[OK MAPA] Mapa salvo em {mapa_path}")

        return str(mapa_path)

    except Exception as e:
        print(f"[ERRO MAPA] Falha ao gerar mapa de {nome_cientifico}: {e}")
        return None


# ------------------ OUTRAS PÁGINAS ------------------

def sair(request):
    logout(request)
    messages.info(request, "Você saiu da sua conta com sucesso.")
    return redirect('login')


def sobre(request):
    return render(request, 'sobre.html')


def contato(request):
    return render(request, 'contato.html')
