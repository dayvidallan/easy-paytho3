# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import newadmin.utils
import django.contrib.auth.models
import django.utils.timezone
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, max_length=30, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, verbose_name='username')),
                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
                ('email', models.EmailField(max_length=254, verbose_name='email address', blank=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'auth_user',
                'permissions': (('pode_cadastrar_solicitacao', 'Pode Cadastrar Solicita\xe7\xe3o'), ('pode_cadastrar_pregao', 'Pode Cadastrar Preg\xe3o'), ('pode_cadastrar_pesquisa_mercadologica', 'Pode Cadastrar Pesquisa Mercadol\xf3gica'), ('pode_ver_minuta', 'Pode Ver Minuta'), ('pode_avaliar_minuta', 'Pode Avaliar Minuta'), ('pode_abrir_processo', 'Pode Abrir Processo')),
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='AnexoPregao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=500, verbose_name='Nome')),
                ('data', models.DateField(verbose_name='Data')),
                ('arquivo', models.FileField(max_length=255, null=True, upload_to='upload/pregao/editais/anexos/', blank=True)),
                ('cadastrado_em', models.DateTimeField(verbose_name='Cadastrado em')),
                ('cadastrado_por', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Anexo do Preg\xe3o',
                'verbose_name_plural': 'Anexos do Preg\xe3o',
            },
        ),
        migrations.CreateModel(
            name='ComissaoLicitacao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=80, verbose_name='Identifica\xe7\xe3o')),
                ('portaria', models.CharField(max_length=80, verbose_name='Portaria')),
            ],
            options={
                'verbose_name': 'Comiss\xe3o de Licita\xe7\xe3o',
                'verbose_name_plural': 'Comiss\xf5es de Licita\xe7\xe3o',
            },
        ),
        migrations.CreateModel(
            name='CriterioPregao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=80, verbose_name='Nome')),
            ],
            options={
                'verbose_name': 'Crit\xe9rio de Julgamento do Preg\xe3o',
                'verbose_name_plural': 'Crit\xe9rios de Julgamento de Preg\xe3o',
            },
        ),
        migrations.CreateModel(
            name='Estado',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=80, verbose_name='Nome')),
                ('sigla', models.CharField(max_length=2, verbose_name='Sigla')),
            ],
        ),
        migrations.CreateModel(
            name='Fornecedor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cnpj', models.CharField(help_text='Utilize pontos e tra\xe7os.', max_length=255, verbose_name='CNPJ/CPF')),
                ('razao_social', models.CharField(max_length=255, verbose_name='Raz\xe3o Social')),
                ('endereco', models.CharField(max_length=255, verbose_name='Endere\xe7o')),
            ],
            options={
                'verbose_name': 'Fornecedor',
                'verbose_name_plural': 'Fornecedores',
            },
        ),
        migrations.CreateModel(
            name='HistoricoPregao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data', models.DateTimeField(verbose_name='Data')),
                ('obs', models.CharField(max_length=2500, null=True, verbose_name='Observa\xe7\xe3o', blank=True)),
            ],
            options={
                'ordering': ['data'],
                'verbose_name': 'Hist\xf3rico do Preg\xe3o',
                'verbose_name_plural': 'Hist\xf3ricos do Preg\xe3o',
            },
        ),
        migrations.CreateModel(
            name='InteressadoEdital',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('responsavel', models.CharField(max_length=200, verbose_name='Respons\xe1vel')),
                ('nome_empresarial', models.CharField(max_length=200, verbose_name='Nome Empresarial')),
                ('cpf', models.CharField(max_length=80, verbose_name='CPF')),
                ('cnpj', models.CharField(max_length=80, verbose_name='CNPK')),
                ('endereco', models.CharField(max_length=80, verbose_name='Endere\xe7o')),
                ('telefone', models.CharField(max_length=80, verbose_name='Telefone')),
                ('email', models.CharField(max_length=80, verbose_name='Email')),
                ('interesse', models.CharField(max_length=80, verbose_name='Interesse', choices=[('Participante', 'Participar da Licita\xe7\xe3o'), ('Interessado', 'Apenas Consulta')])),
                ('data_acesso', models.DateTimeField(verbose_name='Data de Acesso')),
            ],
            options={
                'verbose_name': 'Interessado na Licita\xe7\xe3o',
                'verbose_name_plural': 'Interessados na Licita\xe7\xe3o',
            },
        ),
        migrations.CreateModel(
            name='ItemLote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('numero_item', models.IntegerField(verbose_name='N\xfamero do Item')),
            ],
            options={
                'verbose_name': 'Item do Lote',
                'verbose_name_plural': 'Itens dos Lotes',
            },
        ),
        migrations.CreateModel(
            name='ItemPesquisaMercadologica',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('marca', models.CharField(max_length=255, verbose_name='Marca')),
                ('valor_maximo', models.DecimalField(null=True, verbose_name='Valor M\xe1ximo', max_digits=10, decimal_places=2, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ItemPregao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('unidade', models.CharField(max_length=500, verbose_name='Unidade de Medida')),
                ('quantidade', models.PositiveIntegerField(verbose_name='Quantidade')),
                ('valor_medio', models.DecimalField(verbose_name='Valor M\xe9dio', max_digits=12, decimal_places=2)),
                ('total', models.DecimalField(verbose_name='Total', max_digits=12, decimal_places=2)),
            ],
            options={
                'ordering': ['pregao', 'id'],
                'verbose_name': 'Item do Preg\xe3o',
                'verbose_name_plural': 'Itens do Preg\xe3o',
            },
        ),
        migrations.CreateModel(
            name='ItemQuantidadeSecretaria',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantidade', models.IntegerField(verbose_name='Quantidade')),
                ('aprovado', models.BooleanField(default=False, verbose_name='Aprovado')),
                ('justificativa_reprovacao', models.CharField(max_length=1000, null=True, verbose_name='Motivo da Nega\xe7\xe3o do Pedido', blank=True)),
                ('avaliado_em', models.DateTimeField(null=True, verbose_name='Avaliado Em', blank=True)),
                ('avaliado_por', models.ForeignKey(related_name='pedido_avaliado_por', to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ItemSolicitacaoLicitacao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('item', models.CharField(max_length=50, verbose_name='Item')),
                ('quantidade', models.PositiveIntegerField(verbose_name='Quantidade')),
                ('valor_medio', models.DecimalField(null=True, verbose_name='Valor M\xe9dio', max_digits=10, decimal_places=2, blank=True)),
                ('total', models.DecimalField(null=True, verbose_name='Total', max_digits=10, decimal_places=2, blank=True)),
                ('situacao', models.CharField(default='Cadastrado', max_length=50, verbose_name='Situa\xe7\xe3o', choices=[('Cadastrado', 'Cadastrado'), ('Deserto', 'Deserto'), ('Fracassado', 'Fracassado'), ('Conclu\xeddo', 'Conclu\xeddo')])),
                ('obs', models.CharField(max_length=3000, null=True, verbose_name='Observa\xe7\xe3o', blank=True)),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
                ('eh_lote', models.BooleanField(default=False, verbose_name='Lote')),
            ],
            options={
                'ordering': ['item'],
                'verbose_name': 'Item da Solicita\xe7\xe3o de Licita\xe7\xe3o',
                'verbose_name_plural': 'Itens da Solicita\xe7\xe3o de Licita\xe7\xe3o',
            },
        ),
        migrations.CreateModel(
            name='LanceItemRodadaPregao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('valor', models.DecimalField(null=True, verbose_name='Valor', max_digits=12, decimal_places=2, blank=True)),
                ('declinio', models.BooleanField(default=False, verbose_name='Decl\xednio')),
                ('item', models.ForeignKey(verbose_name='Item da Solicita\xe7\xe3o', to='base.ItemSolicitacaoLicitacao')),
            ],
            options={
                'ordering': ['-valor'],
                'verbose_name': 'Lance da Rodada do Preg\xe3o',
                'verbose_name_plural': 'Lances da Rodada do Preg\xe3o',
            },
        ),
        migrations.CreateModel(
            name='LogDownloadArquivo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=500, verbose_name='Nome Empresarial')),
                ('responsavel', models.CharField(max_length=500, verbose_name='Respons\xe1vel')),
                ('cpf', models.CharField(max_length=500, verbose_name='CPF')),
                ('cnpj', models.CharField(max_length=500, verbose_name='CNPJ')),
                ('endereco', models.CharField(max_length=500, verbose_name='Endere\xe7o')),
                ('telefone', models.CharField(max_length=500, verbose_name='Telefone')),
                ('email', models.CharField(max_length=500, verbose_name='Email')),
                ('interesse', models.CharField(max_length=100, verbose_name='Interesse', choices=[('Participar da Licita\xe7\xe3o', 'Participar da Licita\xe7\xe3o'), ('Apenas Consulta', 'Apenas Consulta')])),
                ('arquivo', models.ForeignKey(to='base.AnexoPregao')),
            ],
            options={
                'verbose_name': 'Log de Download de Arquivo',
                'verbose_name_plural': 'Logs de Download de Arquivo',
            },
        ),
        migrations.CreateModel(
            name='MaterialConsumo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.TextField(help_text='M\xe1ximo de 1024 caracteres.', unique=True, max_length=1024, verbose_name='Nome')),
                ('observacao', models.CharField(max_length=500, null=True, verbose_name='Observa\xe7\xe3o', blank=True)),
                ('codigo', models.CharField(max_length=6, verbose_name='C\xf3digo', blank=True)),
            ],
            options={
                'verbose_name': 'Material de Consumo',
                'verbose_name_plural': 'Materiais de Consumo',
            },
        ),
        migrations.CreateModel(
            name='ModalidadePregao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=80, verbose_name='Nome')),
            ],
            options={
                'verbose_name': 'Modalidade de Preg\xe3o',
                'verbose_name_plural': 'Modalidades de Preg\xe3o',
            },
        ),
        migrations.CreateModel(
            name='MovimentoSolicitacao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_envio', models.DateTimeField(null=True, verbose_name='Enviado Em', blank=True)),
                ('data_recebimento', models.DateTimeField(null=True, verbose_name='Recebido Em', blank=True)),
                ('obs', models.CharField(max_length=5000, null=True, verbose_name='Observa\xe7\xe3o', blank=True)),
                ('enviado_por', models.ForeignKey(related_name='movimentacao_enviado_por', to=settings.AUTH_USER_MODEL)),
                ('recebido_por', models.ForeignKey(related_name='movimentacao_recebido_por', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Movimento da Solicita\xe7\xe3o',
                'verbose_name_plural': 'Movimentos da Solicita\xe7\xe3o',
            },
        ),
        migrations.CreateModel(
            name='Municipio',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('codigo', models.CharField(max_length=7, verbose_name='C\xf3digo IBGE')),
                ('nome', models.CharField(max_length=80, verbose_name='Nome')),
                ('estado', models.ForeignKey(to='base.Estado')),
            ],
            options={
                'ordering': ('nome',),
                'verbose_name': 'Munic\xedpio',
                'verbose_name_plural': 'Munic\xedpios',
            },
        ),
        migrations.CreateModel(
            name='ParticipanteItemPregao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('item', models.ForeignKey(verbose_name='Item', to='base.ItemSolicitacaoLicitacao')),
            ],
            options={
                'verbose_name': 'Participante do Item do Preg\xe3o',
                'verbose_name_plural': 'Participantes do Item do Preg\xe3o',
            },
        ),
        migrations.CreateModel(
            name='ParticipantePregao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome_representante', models.CharField(max_length=255, null=True, verbose_name='Nome do Representante', blank=True)),
                ('cpf_representante', models.CharField(max_length=255, null=True, verbose_name='CPF do Representante', blank=True)),
                ('obs_ausencia_participante', models.CharField(max_length=1500, null=True, verbose_name='Motivo da Aus\xeancia do Representante', blank=True)),
                ('me_epp', models.BooleanField(verbose_name='Micro Empresa/Empresa de Peq.Porte')),
                ('desclassificado', models.BooleanField(default=False, verbose_name='Desclassificado')),
                ('motivo_desclassificacao', models.CharField(max_length=2000, null=True, verbose_name='Motivo da Desclassifica\xe7\xe3o', blank=True)),
                ('arquivo_propostas', models.FileField(upload_to='upload/propostas/', null=True, verbose_name='Arquivo com as Propostas', blank=True)),
                ('fornecedor', models.ForeignKey(verbose_name='Fornecedor', to='base.Fornecedor')),
            ],
            options={
                'ordering': ['desclassificado', 'fornecedor__razao_social'],
                'verbose_name': 'Participante do Preg\xe3o',
                'verbose_name_plural': 'Participantes do Preg\xe3o',
            },
        ),
        migrations.CreateModel(
            name='PesquisaMercadologica',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('razao_social', models.CharField(max_length=255, null=True, verbose_name='Raz\xe3o Social', blank=True)),
                ('cnpj', models.CharField(max_length=255, null=True, verbose_name='CNPJ', blank=True)),
                ('endereco', models.CharField(max_length=255, null=True, verbose_name='Endere\xe7o', blank=True)),
                ('ie', models.CharField(max_length=255, null=True, verbose_name='Inscri\xe7\xe3o Estadual', blank=True)),
                ('telefone', models.CharField(max_length=255, null=True, verbose_name='Telefone', blank=True)),
                ('email', models.CharField(max_length=255, null=True, verbose_name='Email', blank=True)),
                ('nome_representante', models.CharField(max_length=255, null=True, verbose_name='Representante Legal', blank=True)),
                ('cpf_representante', models.CharField(max_length=255, null=True, verbose_name='CPF do Representante Legal', blank=True)),
                ('rg_representante', models.CharField(max_length=255, null=True, verbose_name='RG do Representante Legal', blank=True)),
                ('endereco_representante', models.CharField(max_length=255, null=True, verbose_name='Endere\xe7o do Representante Legal', blank=True)),
                ('validade_proposta', models.IntegerField(null=True, verbose_name='Dias de Validade da Proposta', blank=True)),
                ('cadastrada_em', models.DateTimeField(null=True, verbose_name='Data de Envio da Proposta', blank=True)),
                ('arquivo', models.FileField(upload_to='upload/pesquisas/', null=True, verbose_name='Arquivo da Proposta', blank=True)),
                ('numero_ata', models.CharField(max_length=255, null=True, verbose_name='N\xfamero da Ata', blank=True)),
                ('vigencia_ata', models.DateField(null=True, verbose_name='Vig\xeancia da Ata', blank=True)),
                ('orgao_gerenciador_ata', models.CharField(max_length=255, null=True, verbose_name='\xd3rg\xe3o Gerenciador da Ata', blank=True)),
                ('origem', models.CharField(blank=True, max_length=100, null=True, verbose_name='Origem', choices=[('Ata de Registro de Pre\xe7o', 'Ata de Registro de Pre\xe7o'), ('Fornecedor', 'Fornecedor')])),
            ],
        ),
        migrations.CreateModel(
            name='PessoaFisica',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=80)),
                ('cpf', models.CharField(help_text='Digite o CPF sem pontos ou tra\xe7os.', max_length=15, verbose_name='CPF')),
                ('sexo', models.CharField(max_length=1, verbose_name='Sexo', choices=[('M', 'Masculino'), ('F', 'Feminino')])),
                ('data_nascimento', models.DateField(null=True, verbose_name='Data de Nascimento')),
                ('telefones', models.CharField(max_length=60, null=True, verbose_name='Telefones', blank=True)),
                ('celulares', models.CharField(max_length=60, null=True, verbose_name='Celulares', blank=True)),
                ('email', models.CharField(max_length=80, null=True, verbose_name='Email', blank=True)),
                ('logradouro', models.CharField(max_length=80, null=True, verbose_name='Logradouro', blank=True)),
                ('numero', models.CharField(max_length=10, null=True, verbose_name='N\xfamero', blank=True)),
                ('complemento', models.CharField(max_length=80, null=True, verbose_name='Complemento', blank=True)),
                ('bairro', models.CharField(max_length=80, null=True, verbose_name='Bairro', blank=True)),
                ('cep', newadmin.utils.CepModelField(max_length=9, null=True, verbose_name='CEP', blank=True)),
                ('municipio', models.ForeignKey(blank=True, to='base.Municipio', null=True)),
            ],
            options={
                'verbose_name': 'Pessoa',
                'verbose_name_plural': 'Pessoas',
            },
        ),
        migrations.CreateModel(
            name='Pregao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('num_pregao', models.CharField(max_length=255, verbose_name='N\xfamero do Preg\xe3o')),
                ('num_processo', models.CharField(max_length=255, verbose_name='N\xfamero do Processo')),
                ('data_inicio', models.DateField(null=True, verbose_name='Data de In\xedcio da Retirada das Propostas')),
                ('data_termino', models.DateField(null=True, verbose_name='Data de T\xe9rmino da Retirada das Propostas')),
                ('data_abertura', models.DateField(null=True, verbose_name='Data de Abertura das Propostas')),
                ('hora_abertura', models.TimeField(null=True, verbose_name='Hora de Abertura das Propostas')),
                ('local', models.CharField(max_length=1500, verbose_name='Local')),
                ('responsavel', models.CharField(max_length=255, verbose_name='Respons\xe1vel')),
                ('situacao', models.CharField(default='Cadastrado', max_length=50, verbose_name='Situa\xe7\xe3o', choices=[('Cadastrado', 'Cadastrado'), ('Deserto', 'Deserto'), ('Fracassado', 'Fracassado'), ('Suspenso', 'Suspenso'), ('Conclu\xeddo', 'Conclu\xeddo')])),
                ('obs', models.CharField(max_length=3000, null=True, verbose_name='Observa\xe7\xe3o', blank=True)),
                ('criterio', models.ForeignKey(verbose_name='Crit\xe9rio de Julgamento', to='base.CriterioPregao')),
                ('modalidade', models.ForeignKey(verbose_name='Modalidade', to='base.ModalidadePregao')),
            ],
            options={
                'verbose_name': 'Preg\xe3o',
                'verbose_name_plural': 'Preg\xf5es',
            },
        ),
        migrations.CreateModel(
            name='Processo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_cadastro', models.DateTimeField(auto_now_add=True)),
                ('numero', models.CharField(unique=True, max_length=25, verbose_name='N\xfamero do Processo')),
                ('objeto', models.CharField(max_length=100)),
                ('tipo', models.PositiveIntegerField(choices=[[1, 'Memorando'], [2, 'Of\xedcio'], [3, 'Requerimento']])),
                ('status', models.PositiveIntegerField(default=1, verbose_name='Situa\xe7\xe3o', choices=[[1, 'Em tr\xe2mite'], [2, 'Finalizado'], [3, 'Arquivado']])),
                ('palavras_chave', models.TextField(null=True, verbose_name='Palavras-chave')),
                ('data_finalizacao', models.DateTimeField(null=True, editable=False)),
                ('observacao_finalizacao', models.TextField(null=True, verbose_name='Despacho', blank=True)),
                ('pessoa_cadastro', models.ForeignKey(related_name='pessoa_cadastro_set', to=settings.AUTH_USER_MODEL)),
                ('pessoa_finalizacao', models.ForeignKey(related_name='pessoa_finalizacao_set', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Processo',
                'verbose_name_plural': 'Processos',
            },
        ),
        migrations.CreateModel(
            name='PropostaItemPregao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('valor', models.DecimalField(verbose_name='Valor', max_digits=12, decimal_places=2)),
                ('marca', models.CharField(max_length=200, null=True, verbose_name='Marca')),
                ('desclassificado', models.BooleanField(default=False, verbose_name='Desclassificado')),
                ('motivo_desclassificacao', models.CharField(max_length=2000, null=True, verbose_name='Motivo da Desclassifica\xe7\xe3o', blank=True)),
                ('desistencia', models.BooleanField(default=False, verbose_name='Desist\xeancia')),
                ('motivo_desistencia', models.CharField(max_length=2000, null=True, verbose_name='Motivo da Desist\xeancia', blank=True)),
                ('concorre', models.BooleanField(default=True, verbose_name='Concorre')),
                ('item', models.ForeignKey(verbose_name='Solicita\xe7\xe3o', to='base.ItemSolicitacaoLicitacao')),
                ('participante', models.ForeignKey(verbose_name='Participante', to='base.ParticipantePregao')),
                ('pregao', models.ForeignKey(verbose_name='Preg\xe3o', to='base.Pregao')),
            ],
            options={
                'verbose_name': 'Valor do Item do Preg\xe3o',
                'verbose_name_plural': 'Valores do Item do Preg\xe3o',
            },
        ),
        migrations.CreateModel(
            name='RamoAtividade',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=200, verbose_name='Nome')),
            ],
            options={
                'verbose_name': 'Ramo de Atividade',
                'verbose_name_plural': 'Ramos de Atividade',
            },
        ),
        migrations.CreateModel(
            name='ResultadoItemPregao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('valor', models.DecimalField(verbose_name='Valor', max_digits=12, decimal_places=2)),
                ('marca', models.CharField(max_length=200, null=True, verbose_name='Marca')),
                ('ordem', models.IntegerField(verbose_name='Classifica\xe7\xe3o')),
                ('situacao', models.CharField(max_length=100, verbose_name='Situa\xe7\xe3o', choices=[('Classificado', 'Classificado'), ('Inabilitado', 'Inabilitado'), ('Desclassificado', 'Desclassificado')])),
                ('observacoes', models.CharField(max_length=5000, null=True, verbose_name='Observa\xe7\xe3o', blank=True)),
                ('empate', models.BooleanField(default=False, verbose_name='Empate')),
                ('item', models.ForeignKey(verbose_name='Solicita\xe7\xe3o', to='base.ItemSolicitacaoLicitacao')),
                ('participante', models.ForeignKey(verbose_name='Participante', to='base.ParticipantePregao')),
            ],
            options={
                'verbose_name': 'Resultado da Licita\xe7\xe3o',
                'verbose_name_plural': 'Resultados da Licita\xe7\xe3o',
            },
        ),
        migrations.CreateModel(
            name='RodadaPregao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rodada', models.IntegerField(verbose_name='Rodada de Lances')),
                ('atual', models.BooleanField(default=False, verbose_name='Rodada Atual')),
                ('item', models.ForeignKey(verbose_name='Item da Solicita\xe7\xe3o', to='base.ItemSolicitacaoLicitacao')),
                ('pregao', models.ForeignKey(verbose_name='Preg\xe3o', to='base.Pregao')),
            ],
            options={
                'verbose_name': 'Rodada do Preg\xe3o',
                'verbose_name_plural': 'Rodadas do Preg\xe3o',
            },
        ),
        migrations.CreateModel(
            name='Secretaria',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=80, verbose_name='Nome')),
                ('sigla', models.CharField(max_length=20, null=True, verbose_name='Sigla', blank=True)),
                ('responsavel', models.ForeignKey(verbose_name='Respons\xe1vel', blank=True, to='base.PessoaFisica', null=True)),
            ],
            options={
                'verbose_name': 'Secretaria',
                'verbose_name_plural': 'Secretarias',
            },
        ),
        migrations.CreateModel(
            name='Setor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=80, verbose_name='Nome')),
                ('sigla', models.CharField(max_length=20, null=True, verbose_name='Sigla', blank=True)),
                ('secretaria', models.ForeignKey(verbose_name='Secretaria', to='base.Secretaria')),
            ],
            options={
                'verbose_name': 'Setor',
                'verbose_name_plural': 'Setores',
            },
        ),
        migrations.CreateModel(
            name='SolicitacaoLicitacao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('num_memorando', models.CharField(max_length=80, verbose_name='N\xfamero do Memorando')),
                ('objeto', models.CharField(max_length=1500, verbose_name='Descri\xe7\xe3o do Objeto')),
                ('objetivo', models.CharField(max_length=1500, verbose_name='Objetivo')),
                ('justificativa', models.CharField(max_length=1500, verbose_name='Justificativa')),
                ('situacao', models.CharField(default='Cadastrado', max_length=50, verbose_name='Situa\xe7\xe3o', choices=[('Cadastrado', 'Cadastrado'), ('Aguardando Recebimento', 'Aguardando Recebimento'), ('Recebido', 'Recebido'), ('Devolvido', 'Devolvido'), ('Enviado para Licita\xe7\xe3o', 'Enviado para Licita\xe7\xe3o'), ('Em Licita\xe7\xe3o', 'Em Licita\xe7\xe3o'), ('Negada', 'Negada')])),
                ('data_cadastro', models.DateTimeField(verbose_name='Cadastrada em')),
                ('obs_negacao', models.CharField(max_length=1500, null=True, verbose_name='Justificativa da Nega\xe7\xe3o', blank=True)),
                ('data_inicio_pesquisa', models.DateField(null=True, verbose_name='In\xedcio das Pesquisas', blank=True)),
                ('data_fim_pesquisa', models.DateField(null=True, verbose_name='Fim das Pesquisas', blank=True)),
                ('prazo_resposta_interessados', models.DateField(null=True, verbose_name='Prazo para retorno dos interessados', blank=True)),
                ('arquivo_minuta', models.FileField(upload_to='upload/minutas/', null=True, verbose_name='Arquivo da Minuta', blank=True)),
                ('minuta_aprovada', models.BooleanField(default=False, verbose_name='Minuta Aprovada')),
                ('data_avaliacao_minuta', models.DateTimeField(null=True, verbose_name='Minuta Aprovada em', blank=True)),
                ('obs_avaliacao_minuta', models.CharField(max_length=1500, null=True, verbose_name='Observa\xe7\xe3o - Minuta', blank=True)),
                ('arquivo_parecer_minuta', models.FileField(upload_to='upload/minutas/', null=True, verbose_name='Arquivo com o Parecer', blank=True)),
                ('prazo_aberto', models.NullBooleanField(default=False, verbose_name='Aberto para Recebimento de Pesquisa')),
                ('cadastrado_por', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('interessados', models.ManyToManyField(to='base.Secretaria')),
                ('minuta_avaliada_por', models.ForeignKey(related_name='aprova_minuta', verbose_name='Minuta Aprovada Por', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('processo', models.ForeignKey(to='base.Processo', null=True)),
                ('setor_atual', models.ForeignKey(related_name='setor_atual', verbose_name='Setor Atual', blank=True, to='base.Setor', null=True)),
                ('setor_origem', models.ForeignKey(related_name='setor_origem', verbose_name='Setor de Origem', blank=True, to='base.Setor', null=True)),
            ],
            options={
                'verbose_name': 'Solicita\xe7\xe3o de Licita\xe7\xe3o',
                'verbose_name_plural': 'Solicita\xe7\xf5es de Licita\xe7\xe3o',
            },
        ),
        migrations.CreateModel(
            name='TipoPregao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=80, verbose_name='Nome')),
            ],
            options={
                'verbose_name': 'Tipo de Preg\xe3o',
                'verbose_name_plural': 'Tipos de Preg\xe3o',
            },
        ),
        migrations.CreateModel(
            name='TipoUnidade',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=80, verbose_name='Unidade')),
            ],
            options={
                'verbose_name': 'Tipo de Unidade',
                'verbose_name_plural': 'Tipos de Unidade',
            },
        ),
        migrations.AddField(
            model_name='processo',
            name='setor_origem',
            field=models.ForeignKey(verbose_name='Setor de Origem', to='base.Setor'),
        ),
        migrations.AddField(
            model_name='pregao',
            name='solicitacao',
            field=models.ForeignKey(verbose_name='Solicita\xe7\xe3o', to='base.SolicitacaoLicitacao'),
        ),
        migrations.AddField(
            model_name='pregao',
            name='tipo',
            field=models.ForeignKey(verbose_name='Tipo', to='base.TipoPregao'),
        ),
        migrations.AddField(
            model_name='pessoafisica',
            name='setor',
            field=models.ForeignKey(verbose_name='Setor', to='base.Setor'),
        ),
        migrations.AddField(
            model_name='pessoafisica',
            name='user',
            field=models.OneToOneField(null=True, blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='pesquisamercadologica',
            name='solicitacao',
            field=models.ForeignKey(to='base.SolicitacaoLicitacao'),
        ),
        migrations.AddField(
            model_name='participantepregao',
            name='pregao',
            field=models.ForeignKey(verbose_name='Preg\xe3o', to='base.Pregao'),
        ),
        migrations.AddField(
            model_name='participanteitempregao',
            name='participante',
            field=models.ForeignKey(verbose_name='Participante', to='base.ParticipantePregao'),
        ),
        migrations.AddField(
            model_name='movimentosolicitacao',
            name='setor_destino',
            field=models.ForeignKey(related_name='movimentacao_setor_destino', to='base.Setor', null=True),
        ),
        migrations.AddField(
            model_name='movimentosolicitacao',
            name='setor_origem',
            field=models.ForeignKey(related_name='movimentacao_setor_origem', to='base.Setor'),
        ),
        migrations.AddField(
            model_name='movimentosolicitacao',
            name='solicitacao',
            field=models.ForeignKey(to='base.SolicitacaoLicitacao'),
        ),
        migrations.AddField(
            model_name='logdownloadarquivo',
            name='municipio',
            field=models.ForeignKey(verbose_name='Cidade', to='base.Municipio'),
        ),
        migrations.AddField(
            model_name='lanceitemrodadapregao',
            name='participante',
            field=models.ForeignKey(verbose_name='Participante', to='base.ParticipantePregao'),
        ),
        migrations.AddField(
            model_name='lanceitemrodadapregao',
            name='rodada',
            field=models.ForeignKey(verbose_name='Rodada', to='base.RodadaPregao'),
        ),
        migrations.AddField(
            model_name='itemsolicitacaolicitacao',
            name='material',
            field=models.ForeignKey(to='base.MaterialConsumo', null=True),
        ),
        migrations.AddField(
            model_name='itemsolicitacaolicitacao',
            name='solicitacao',
            field=models.ForeignKey(verbose_name='Solicita\xe7\xe3o', to='base.SolicitacaoLicitacao'),
        ),
        migrations.AddField(
            model_name='itemsolicitacaolicitacao',
            name='unidade',
            field=models.ForeignKey(verbose_name='Unidade', to='base.TipoUnidade', null=True),
        ),
        migrations.AddField(
            model_name='itemquantidadesecretaria',
            name='item',
            field=models.ForeignKey(to='base.ItemSolicitacaoLicitacao'),
        ),
        migrations.AddField(
            model_name='itemquantidadesecretaria',
            name='secretaria',
            field=models.ForeignKey(to='base.Secretaria'),
        ),
        migrations.AddField(
            model_name='itemquantidadesecretaria',
            name='solicitacao',
            field=models.ForeignKey(verbose_name='Solicita\xe7\xe3o', to='base.SolicitacaoLicitacao'),
        ),
        migrations.AddField(
            model_name='itempregao',
            name='material',
            field=models.ForeignKey(to='base.MaterialConsumo'),
        ),
        migrations.AddField(
            model_name='itempregao',
            name='pregao',
            field=models.ForeignKey(verbose_name='Preg\xe3o', to='base.Pregao'),
        ),
        migrations.AddField(
            model_name='itempesquisamercadologica',
            name='item',
            field=models.ForeignKey(to='base.ItemSolicitacaoLicitacao'),
        ),
        migrations.AddField(
            model_name='itempesquisamercadologica',
            name='pesquisa',
            field=models.ForeignKey(verbose_name='Pesquisa', to='base.PesquisaMercadologica'),
        ),
        migrations.AddField(
            model_name='itemlote',
            name='item',
            field=models.ForeignKey(related_name='item_do_lote', to='base.ItemSolicitacaoLicitacao'),
        ),
        migrations.AddField(
            model_name='itemlote',
            name='lote',
            field=models.ForeignKey(related_name='lote', to='base.ItemSolicitacaoLicitacao'),
        ),
        migrations.AddField(
            model_name='interessadoedital',
            name='municipio',
            field=models.ForeignKey(verbose_name='Munic\xedpio', to='base.Municipio'),
        ),
        migrations.AddField(
            model_name='interessadoedital',
            name='pregao',
            field=models.ForeignKey(to='base.Pregao'),
        ),
        migrations.AddField(
            model_name='historicopregao',
            name='pregao',
            field=models.ForeignKey(to='base.Pregao'),
        ),
        migrations.AddField(
            model_name='fornecedor',
            name='ramo_atividade',
            field=models.ForeignKey(verbose_name='Ramo de Atividade', to='base.RamoAtividade'),
        ),
        migrations.AddField(
            model_name='comissaolicitacao',
            name='membro',
            field=models.ManyToManyField(related_name='Membros', to='base.PessoaFisica'),
        ),
        migrations.AddField(
            model_name='anexopregao',
            name='pregao',
            field=models.ForeignKey(to='base.Pregao'),
        ),
    ]
