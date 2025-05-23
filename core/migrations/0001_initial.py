# Generated by Django 5.1.5 on 2025-02-04 13:19

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('senha', models.CharField(max_length=128)),
                ('tipo_usuario', models.CharField(choices=[('comum', 'Usuário Comum'), ('pesquisador', 'Pesquisador'), ('instituicao', 'Instituição de Educação')], max_length=20)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='InstituicaoEducacao',
            fields=[
                ('usuario_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('nome', models.CharField(max_length=255)),
                ('cnpj', models.CharField(max_length=18, unique=True)),
                ('endereco', models.TextField()),
                ('contato', models.CharField(max_length=50)),
                ('website', models.URLField()),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            bases=('core.usuario',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='UsuarioComum',
            fields=[
                ('usuario_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            bases=('core.usuario',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Animal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reino', models.CharField(max_length=100)),
                ('filo', models.CharField(max_length=100)),
                ('classe', models.CharField(max_length=100)),
                ('ordem', models.CharField(max_length=100)),
                ('familia', models.CharField(max_length=100)),
                ('genero', models.CharField(max_length=100)),
                ('nome_cientifico', models.CharField(max_length=255)),
                ('nome_cientifico_anterior', models.CharField(blank=True, max_length=255, null=True)),
                ('autor', models.CharField(max_length=255)),
                ('nome_comum', models.CharField(max_length=255)),
                ('grupo', models.CharField(max_length=100)),
                ('mes_ano_avaliacao', models.CharField(max_length=50)),
                ('categoria', models.CharField(max_length=100)),
                ('possivelmente_extinta', models.BooleanField(default=False)),
                ('criterio', models.CharField(max_length=255)),
                ('justificativa', models.TextField()),
                ('endemica_brasil', models.BooleanField(default=False)),
                ('consta_lista_nacional_oficial', models.BooleanField(default=False)),
                ('estado', models.CharField(max_length=100)),
                ('regiao', models.CharField(max_length=100)),
                ('bioma', models.CharField(max_length=100)),
                ('bacia_hidrografica', models.CharField(max_length=100)),
                ('uc_federal', models.CharField(max_length=100)),
                ('uc_estadual', models.CharField(max_length=100)),
                ('rppn', models.CharField(max_length=100)),
                ('migratoria', models.BooleanField(default=False)),
                ('tendencia_populacional', models.CharField(max_length=100)),
                ('ameaca', models.CharField(max_length=100)),
                ('uso', models.CharField(max_length=100)),
                ('acao_conservacao', models.TextField()),
                ('plano_acao', models.TextField()),
                ('listas_convencoes', models.TextField()),
                ('cadastrado_por', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='animais', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Pesquisador',
            fields=[
                ('usuario_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('data_nascimento', models.DateField()),
                ('formacao', models.CharField(max_length=255)),
                ('instituicao_atuante', models.CharField(max_length=255)),
                ('lattes', models.URLField()),
                ('instituicao', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pesquisadores', to='core.instituicaoeducacao')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            bases=('core.usuario',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
