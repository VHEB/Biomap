import csv
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Animal

class Command(BaseCommand):
    help = 'Importa animais de um arquivo CSV para o banco de dados.'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help='Caminho do arquivo CSV a ser importado.')

    def handle(self, *args, **options):
        csv_path = options['csv_path']

        # Mapeamento entre as colunas do CSV e os campos do model
        map_fields = {
            "Reino": "reino",
            "Filo": "filo",
            "Classe": "classe",
            "Ordem": "ordem",
            "Familia": "familia",
            "Genero": "genero",
            "Nome_Cientifico": "nome_cientifico",
            "Nome_Cientifico_Anterior": "nome_cientifico_anterior",
            "Autor": "autor",
            "Nome_Comum": "nome_comum",
            "Grupo": "grupo",
            "Mes_Ano_Avaliacao": "mes_ano_avaliacao",
            "Categoria": "categoria",
            "Possivemente_Extinta": "possivelmente_extinta",
            "Criterio": "criterio",
            "Justificativa": "justificativa",
            "Endemica_Brasil": "endemica_brasil",
            "Consta_em_Lista_Nacional_Oficial": "consta_lista_nacional_oficial",
            "Estado": "estado",
            "Regiao": "regiao",
            "Bioma": "bioma",
            "Bacia_Hidrografica": "bacia_hidrografica",
            "Unidade_de_Conservacao_Federal": "uc_federal",
            "Unidade_de_Conservacao_Estadual": "uc_estadual",
            "RPPN": "rppn",
            "Migratoria": "migratoria",
            "Tendencia_Populacional": "tendencia_populacional",
            "Ameaca": "ameaca",
            "Uso": "uso",
            "Acao_Conservacao": "acao_conservacao",
            "Plano_de_Acao": "plano_acao",
            "Listas_e_Convencoes": "listas_convencoes"
        }

        # Campos que são booleanos no model
        bool_fields = [
            "possivelmente_extinta",
            "endemica_brasil",
            "consta_lista_nacional_oficial",
            "migratoria"
        ]

        self.stdout.write(self.style.NOTICE(f"Iniciando importação do arquivo: {csv_path}"))

        animals_to_create = []
        with open(csv_path, newline='', encoding='latin-1') as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            for row in reader:
                count += 1
                animal_data = {}
                for csv_col, model_field in map_fields.items():
                    valor = row.get(csv_col, "").strip()
                    if model_field in bool_fields:
                        if valor.lower() == "sim":
                            animal_data[model_field] = True
                        else:
                            animal_data[model_field] = False
                    else:
                        animal_data[model_field] = valor
                animals_to_create.append(Animal(**animal_data))

        self.stdout.write(self.style.NOTICE(f"{count} linhas processadas do CSV."))
        self.stdout.write(self.style.NOTICE(f"{len(animals_to_create)} registros preparados para importação."))

        Animal.objects.bulk_create(animals_to_create, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS("Importação concluída com sucesso!"))