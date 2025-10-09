import re
import requests
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")  
import matplotlib.pyplot as plt
from django.conf import settings
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

MAPA_REGIOES_BRASIL_COMPLETO = {
    # Chave: Nome da Região | Estados | Cor (em formato hexadecimal)
    "SUL": {
        "estados": ["PARANA", "SANTA CATARINA", "RIO GRANDE DO SUL"],
        "cor": "#007bff"  # Azul
    },
    "SUDESTE": {
        "estados": ["MINAS GERAIS", "SAO PAULO", "RIO DE JANEIRO", "ESPIRITO SANTO"],
        "cor": "#ffc107"  # Amarelo/Ouro
    },
    "NORDESTE": {
        "estados": ["MARANHAO", "PIAUI", "CEARA", "RIO GRANDE DO NORTE", "PARAIBA", "PERNAMBUCO", "ALAGOAS", "SERGIPE", "BAHIA"],
        "cor": "#ff5722"  # Laranja/Vermelho (para contraste com o Norte)
    },
    "NORTE": {
        "estados": ["RONDONIA", "ACRE", "AMAZONAS", "RORAIMA", "PARA", "AMAPA", "TOCANTINS"],
        "cor": "#28a745"  # Verde
    },
    "CENTRO-OESTE": {
        "estados": ["MATO GROSSO", "MATO GROSSO DO SUL", "GOIAS", "DISTRITO FEDERAL"],
        "cor": "#6f42c1"  # Roxo
    },
}
MAPA_ESTADO_PARA_COR = {}
for regiao, dados in MAPA_REGIOES_BRASIL_COMPLETO.items():
    for estado in dados["estados"]:
        MAPA_ESTADO_PARA_COR[estado] = dados["cor"]

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
    # O código duplicado do folium e a segunda definição da função foram removidos.

    termo = unidecode(nome_cientifico.strip().lower())
    print(f"[DEBUG] Termo pesquisado: {termo}")

    # Busca o animal ignorando acentos
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
        # Usa a função corrigir com o novo mapeamento
        mapa_path = gerar_mapa_animal(animal.regiao, animal.nome_cientifico)

    # Passa a variável 'mapa_path' que contém o caminho relativo do PNG
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
    """Gera mapa destacando estados onde o animal ocorre com cores por macrorregião."""
    try:
        pasta = Path("media/mapas")
        pasta.mkdir(parents=True, exist_ok=True)

        # Shapefile do Brasil (por estado)
        url_geojson = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
        brasil = gpd.read_file(url_geojson)

        # Corrige nomes e acentuação
        brasil["name_norm"] = brasil["name"].apply(lambda x: unidecode(x).upper())

        # 1. Normaliza e processa o campo 'regioes'
        regioes_estados_a_pintar = set() # Usamos um set para evitar duplicatas e otimizar busca
        
        if isinstance(regioes, str):
            # Divide por VÍRGULA ou BARRA VERTICAL e limpa a string
            partes_originais = re.split(r'[,|]', regioes)
            partes_limpas = [unidecode(r.strip().upper()) for r in partes_originais if r.strip()]
            
            # 2. Mapeia as partes para a lista final de estados
            for parte in partes_limpas:
                # Se for uma das macrorregiões (ex: "SUL"), adiciona todos os seus estados ao set
                if parte in MAPA_REGIOES_BRASIL_COMPLETO:
                    regioes_estados_a_pintar.update(MAPA_REGIOES_BRASIL_COMPLETO[parte]["estados"])
                # Se não for uma região, assume que é um nome de estado e o adiciona
                else:
                    regioes_estados_a_pintar.add(parte)


        # 3. Pinta o mapa usando o mapeamento de Estado -> Cor
        def get_estado_color(uf):
            """Retorna a cor se o estado for de ocorrência, senão retorna cinza."""
            if uf in regioes_estados_a_pintar:
                # Se o estado está na lista de ocorrência, pegamos a cor definida no MAPA_ESTADO_PARA_COR
                return MAPA_ESTADO_PARA_COR.get(uf, "#00796b") # Cor padrão caso falhe (verde padrão)
            return "#DDDDDD" # Cinza para estados sem ocorrência

        brasil["color"] = brasil["name_norm"].apply(get_estado_color)


        fig, ax = plt.subplots(figsize=(8, 6))
        brasil.plot(ax=ax, color=brasil["color"], edgecolor="black")
        ax.set_title(f"Distribuição geográfica de {nome_cientifico}", fontsize=10)
        ax.axis("off")

        # Caminho do mapa
        mapa_path = pasta / f"mapa_{nome_cientifico.replace(' ', '_')}.png"
        plt.savefig(mapa_path, bbox_inches="tight", dpi=150)
        plt.close(fig)
        print(f"[OK MAPA] Mapa salvo em {mapa_path}")

        # Retorna o caminho relativo para o template
        return f"mapas/{mapa_path.name}"

    except Exception as e:
        print(f"[ERRO MAPA] Falha ao gerar mapa de {nome_cientifico}: {e}")
        return None
    """Gera mapa destacando estados onde o animal ocorre.
       Aceita regiões (ex: 'SUL') ou estados (ex: 'PARANA, SAO PAULO')."""
    try:
        pasta = Path("media/mapas")
        pasta.mkdir(parents=True, exist_ok=True)

        # ✅ Shapefile do Brasil (por estado)
        url_geojson = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
        brasil = gpd.read_file(url_geojson)

        # Corrige nomes e acentuação
        brasil["name_norm"] = brasil["name"].apply(lambda x: unidecode(x).upper())

        # 1. Normaliza e processa o campo 'regioes'
        regioes_estados_a_pintar = []
        
        if isinstance(regioes, str):
            # ⚠️ NOVO: Usa re.split para dividir por VÍRGULA ou BARRA VERTICAL
            # Isso trata entradas como "Sul, Sudeste" E "|Centro-Oeste|Nordeste|Sul|"
            
            # Divide e remove caracteres indesejados (incluindo as barras verticais se não forem usadas como separadores)
            partes_originais = re.split(r'[,|]', regioes)
            partes_limpas = [unidecode(r.strip().upper()) for r in partes_originais if r.strip()]
            
            # 2. Mapeia as partes para a lista final de estados
            for parte in partes_limpas:
                # Se for uma região definida (ex: "SUL"), adiciona todos os seus estados
                if parte in MAPA_REGIOES_BRASIL:
                    regioes_estados_a_pintar.extend(MAPA_REGIOES_BRASIL[parte])
                # Se não for uma região, assume que é um nome de estado e o adiciona
                else:
                    regioes_estados_a_pintar.append(parte)

        # Remove duplicatas e cria o conjunto final de estados a pintar
        regioes_set = set(regioes_estados_a_pintar)
        
        # 3. Pinta o mapa
        # Pinta de 'green' se o estado normalizado estiver no nosso conjunto de regiões
        brasil["color"] = brasil["name_norm"].apply(
            lambda uf: "green" if uf in regioes_set else "#DDDDDD"
        )

        fig, ax = plt.subplots(figsize=(8, 6))
        brasil.plot(ax=ax, color=brasil["color"], edgecolor="black")
        ax.set_title(f"Distribuição geográfica de {nome_cientifico}", fontsize=10)
        ax.axis("off")

        # Caminho do mapa
        mapa_path = pasta / f"mapa_{nome_cientifico.replace(' ', '_')}.png"
        plt.savefig(mapa_path, bbox_inches="tight", dpi=150)
        plt.close(fig)
        print(f"[OK MAPA] Mapa salvo em {mapa_path}")

        # 🔹 Retorna o caminho relativo para o template
        return f"mapas/{mapa_path.name}"

    except Exception as e:
        print(f"[ERRO MAPA] Falha ao gerar mapa de {nome_cientifico}: {e}")
        return None
    """Gera mapa destacando estados onde o animal ocorre.
       Aceita regiões (ex: 'SUL') ou estados (ex: 'PARANA, SAO PAULO')."""
    try:
        pasta = Path("media/mapas")
        pasta.mkdir(parents=True, exist_ok=True)

        # ✅ Shapefile do Brasil (por estado)
        url_geojson = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
        brasil = gpd.read_file(url_geojson)

        # Corrige nomes e acentuação
        brasil["name_norm"] = brasil["name"].apply(lambda x: unidecode(x).upper())

        # 1. Normaliza e processa o campo 'regioes'
        regioes_estados_a_pintar = []
        
        if isinstance(regioes, str):
            # Divide por vírgula e remove acentos/limpa espaços/remove "|", tratando a entrada
            partes_originais = [unidecode(r.strip().upper()).replace("|", "") for r in regioes.split(",") if r.strip()]
            
            # 2. Mapeia as partes para a lista final de estados
            for parte in partes_originais:
                # Se for uma região definida (ex: "SUL"), adiciona todos os seus estados
                if parte in MAPA_REGIOES_BRASIL:
                    regioes_estados_a_pintar.extend(MAPA_REGIOES_BRASIL[parte])
                # Se não for uma região, assume que é um nome de estado e o adiciona
                else:
                    regioes_estados_a_pintar.append(parte)

        # Remove duplicatas e cria o conjunto final de estados a pintar
        regioes_set = set(regioes_estados_a_pintar)
        
        # 3. Pinta o mapa
        # Pinta de 'green' se o estado normalizado estiver no nosso conjunto de regiões
        brasil["color"] = brasil["name_norm"].apply(
            lambda uf: "green" if uf in regioes_set else "#DDDDDD"
        )

        fig, ax = plt.subplots(figsize=(8, 6))
        brasil.plot(ax=ax, color=brasil["color"], edgecolor="black")
        ax.set_title(f"Distribuição geográfica de {nome_cientifico}", fontsize=10)
        ax.axis("off")

        # Caminho do mapa
        mapa_path = pasta / f"mapa_{nome_cientifico.replace(' ', '_')}.png"
        plt.savefig(mapa_path, bbox_inches="tight", dpi=150)
        plt.close(fig)
        print(f"[OK MAPA] Mapa salvo em {mapa_path}")

        # 🔹 Retorna o caminho relativo para o template
        return f"mapas/{mapa_path.name}"

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