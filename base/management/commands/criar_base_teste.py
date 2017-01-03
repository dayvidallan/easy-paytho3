# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from base.models import *
import datetime

class Command(BaseCommand):

    def handle(self, *args, **options):

        grupo_secretaria = Group.objects.get_or_create(name=u'Secretaria')[0]
        grupo_pregao = Group.objects.get_or_create(name=u'Licitação')[0]
        grupo_compras = Group.objects.get_or_create(name=u'Compras')[0]
        grupo_juridico = Group.objects.get_or_create(name=u'Jurídico')[0]
        grupo_protocolo = Group.objects.get_or_create(name=u'Protocolo')[0]
        grupo_gerente = Group.objects.get_or_create(name=u'Gerente')[0]

        secretaria = Secretaria.objects.get_or_create(nome=u'Secretaria de Planejamento', sigla=u'SEMPLA')[0]
        secretaria2 = Secretaria.objects.get_or_create(nome=u'Secretaria de Tributação', sigla=u'SEMUT')[0]
        secretaria3 = Secretaria.objects.get_or_create(nome=u'Secretaria da Saúde', sigla=u'SMS')[0]

        uni1 = TipoUnidade.objects.get_or_create(nome=u'Rolo')[0]
        uni2 = TipoUnidade.objects.get_or_create(nome=u'Caixa')[0]
        uni3 = TipoUnidade.objects.get_or_create(nome=u'Unidade')[0]

        setor_licitacao = Setor.objects.get_or_create(nome=u'Setor de Licitação', sigla=u'SECLIC', secretaria=secretaria)[0]
        setor_compras = Setor.objects.get_or_create(nome=u'Setor de Compras', sigla=u'SECCOMP', secretaria=secretaria)[0]
        setor_secretaria = Setor.objects.get_or_create(nome=u'Setor Administrativo', sigla=u'SECADM', secretaria=secretaria)[0]
        setor_juridico = Setor.objects.get_or_create(nome=u'Setor Jurídico', sigla=u'SECJUR', secretaria=secretaria)[0]
        setor_protocolo = Setor.objects.get_or_create(nome=u'Setor de Protocolo', sigla=u'SECPROT', secretaria=secretaria)[0]

        setor_licitacao2 = Setor.objects.get_or_create(nome=u'Setor de Licitação', sigla=u'SECLIC', secretaria=secretaria2)[0]
        setor_compras2 = Setor.objects.get_or_create(nome=u'Setor de Compras', sigla=u'SECCOMP', secretaria=secretaria2)[0]
        setor_secretaria2 = Setor.objects.get_or_create(nome=u'Setor Administrativo', sigla=u'SECADM', secretaria=secretaria2)[0]
        setor_juridico2 = Setor.objects.get_or_create(nome=u'Setor Jurídico', sigla=u'SECJUR', secretaria=secretaria2)[0]
        setor_protocolo2 = Setor.objects.get_or_create(nome=u'Setor de Protocolo', sigla=u'SECPROT', secretaria=secretaria2)[0]

        setor_licitacao3 = Setor.objects.get_or_create(nome=u'Setor de Licitação', sigla=u'SECLIC', secretaria=secretaria3)[0]
        setor_compras3 = Setor.objects.get_or_create(nome=u'Setor de Compras', sigla=u'SECCOMP', secretaria=secretaria3)[0]
        setor_secretaria3 = Setor.objects.get_or_create(nome=u'Setor Administrativo', sigla=u'SECADM', secretaria=secretaria3)[0]
        setor_juridico3 = Setor.objects.get_or_create(nome=u'Setor Jurídico', sigla=u'SECJUR', secretaria=secretaria3)[0]
        setor_protocolo3 = Setor.objects.get_or_create(nome=u'Setor de Protocolo', sigla=u'SECPROT', secretaria=secretaria3)[0]


        user_secretaria = User.objects.get_or_create(username=u'secretaria',is_active=True,is_superuser=False, is_staff=True,password=u'pbkdf2_sha256$20000$THrN7vMCbCch$hvQF8rxuA0EZ6A0Z/q2+izYd4u226ic/XaHXHQ/rJhg=', date_joined=u'2016-06-06T15:52:27.985')[0]
        #pessoa = PessoaFisica.objects.get_or_create(nome=u'Secretário do Planejamento', cpf=u'12345678900',sexo=PessoaFisica.SEXO_MASCULINO, setor=setor_secretaria, user=user_secretaria)[0]
        pessoa = PessoaFisica()
        pessoa.nome = u'Secretário do Planejamento'
        pessoa.cpf = u'12345678900'
        pessoa.sexo = PessoaFisica.SEXO_MASCULINO
        pessoa.setor = setor_secretaria
        pessoa.user = user_secretaria
        pessoa.save()

        user_secretaria.groups.add(grupo_secretaria)

        user_licitacao = User.objects.get_or_create(username=u'pregoeiro',is_active=True,is_superuser=False, is_staff=True,password=u'pbkdf2_sha256$20000$THrN7vMCbCch$hvQF8rxuA0EZ6A0Z/q2+izYd4u226ic/XaHXHQ/rJhg=', date_joined=u'2016-06-06T15:52:27.985')[0]
        #pessoa = PessoaFisica.objects.get_or_create(nome=u'Pregoeiro do Planejamento', cpf=u'12345678900',sexo=PessoaFisica.SEXO_MASCULINO, setor=setor_licitacao, user=user_licitacao)[0]
        pessoa = PessoaFisica()
        pessoa.nome = u'Pregoeiro do Planejamento'
        pessoa.cpf = u'12345678900'
        pessoa.sexo = PessoaFisica.SEXO_MASCULINO
        pessoa.setor = setor_licitacao
        pessoa.user = user_licitacao
        pessoa.save()


        user_licitacao.groups.add(grupo_pregao)

        user_compras = User.objects.get_or_create(username=u'compras',is_active=True,is_superuser=False, is_staff=True,password=u'pbkdf2_sha256$20000$THrN7vMCbCch$hvQF8rxuA0EZ6A0Z/q2+izYd4u226ic/XaHXHQ/rJhg=', date_joined=u'2016-06-06T15:52:27.985')[0]
        #pessoa = PessoaFisica.objects.get_or_create(nome=u'Comprador do Planejamento', cpf=u'12345678900',sexo=PessoaFisica.SEXO_MASCULINO, setor=setor_compras, user=user_compras)[0]

        pessoa = PessoaFisica()
        pessoa.nome = u'Comprador do Planejamento'
        pessoa.cpf = u'12345678900'
        pessoa.sexo = PessoaFisica.SEXO_MASCULINO
        pessoa.setor = setor_compras
        pessoa.user = user_compras
        pessoa.save()

        user_compras.groups.add(grupo_compras)

        user_juridico = User.objects.get_or_create(username=u'juridico',is_active=True,is_superuser=False, is_staff=True,password=u'pbkdf2_sha256$20000$THrN7vMCbCch$hvQF8rxuA0EZ6A0Z/q2+izYd4u226ic/XaHXHQ/rJhg=', date_joined=u'2016-06-06T15:52:27.985')[0]
        #pessoa = PessoaFisica.objects.get_or_create(nome=u'Jurídico do Planejamento', cpf=u'12345678900',sexo=PessoaFisica.SEXO_MASCULINO, setor=setor_juridico, user=user_juridico)[0]
        pessoa = PessoaFisica()
        pessoa.nome = u'Jurídico do Planejamento'
        pessoa.cpf = u'12345678900'
        pessoa.sexo = PessoaFisica.SEXO_MASCULINO
        pessoa.setor = setor_juridico
        pessoa.user = user_juridico
        pessoa.save()

        user_juridico.groups.add(grupo_juridico)

        user_protocolo = User.objects.get_or_create(username=u'protocolo',is_active=True,is_superuser=False, is_staff=True,password=u'pbkdf2_sha256$20000$THrN7vMCbCch$hvQF8rxuA0EZ6A0Z/q2+izYd4u226ic/XaHXHQ/rJhg=', date_joined=u'2016-06-06T15:52:27.985')[0]
        #pessoa = PessoaFisica.objects.get_or_create(nome=u'Protocolo do Planejamento', cpf=u'12345678900',sexo=PessoaFisica.SEXO_MASCULINO, setor=setor_protoloco, user=user_protocolo)[0]
        pessoa = PessoaFisica()
        pessoa.nome = u'Protocolo do Planejamento'
        pessoa.cpf = u'12345678900'
        pessoa.sexo = PessoaFisica.SEXO_MASCULINO
        pessoa.setor = setor_protocolo
        pessoa.user = user_protocolo
        pessoa.save()

        user_protocolo.groups.add(grupo_protocolo)



        user_gerente = User.objects.get_or_create(username=u'gerente',is_active=True,is_superuser=False, is_staff=True,password=u'pbkdf2_sha256$20000$THrN7vMCbCch$hvQF8rxuA0EZ6A0Z/q2+izYd4u226ic/XaHXHQ/rJhg=', date_joined=u'2016-06-06T15:52:27.985')[0]
        #pessoa = PessoaFisica.objects.get_or_create(nome=u'Secretário do Planejamento', cpf=u'12345678900',sexo=PessoaFisica.SEXO_MASCULINO, setor=setor_secretaria, user=user_secretaria)[0]
        pessoa = PessoaFisica()
        pessoa.nome = u'Gerente de Contratos'
        pessoa.cpf = u'12345678900'
        pessoa.sexo = PessoaFisica.SEXO_MASCULINO
        pessoa.setor = setor_secretaria
        pessoa.user = user_gerente
        pessoa.save()

        user_gerente.groups.add(grupo_gerente)


        user_secretaria2 = User.objects.get_or_create(username=u'secretaria2',is_active=True,is_superuser=False, is_staff=True,password=u'pbkdf2_sha256$20000$THrN7vMCbCch$hvQF8rxuA0EZ6A0Z/q2+izYd4u226ic/XaHXHQ/rJhg=', date_joined=u'2016-06-06T15:52:27.985')[0]
        #pessoa = PessoaFisica.objects.get_or_create(nome=u'Secretário da Tributação', cpf=u'12345678900',sexo=PessoaFisica.SEXO_MASCULINO, setor=setor_secretaria2, user=user_secretaria2)[0]
        pessoa = PessoaFisica()
        pessoa.nome = u'Secretário da Tributação'
        pessoa.cpf = u'12345678900'
        pessoa.sexo = PessoaFisica.SEXO_MASCULINO
        pessoa.setor = setor_secretaria2
        pessoa.user = user_secretaria2
        pessoa.save()


        user_secretaria2.groups.add(grupo_secretaria)

        user_licitacao2 = User.objects.get_or_create(username=u'pregoeiro2',is_active=True,is_superuser=False, is_staff=True,password=u'pbkdf2_sha256$20000$THrN7vMCbCch$hvQF8rxuA0EZ6A0Z/q2+izYd4u226ic/XaHXHQ/rJhg=', date_joined=u'2016-06-06T15:52:27.985')[0]
        #pessoa = PessoaFisica.objects.get_or_create(nome=u'Pregoeiro da Tributação', cpf=u'12345678900',sexo=PessoaFisica.SEXO_MASCULINO, setor=setor_licitacao2, user=user_licitacao2)[0]
        pessoa = PessoaFisica()
        pessoa.nome = u'Pregoeiro da Tributação'
        pessoa.cpf = u'12345678900'
        pessoa.sexo = PessoaFisica.SEXO_MASCULINO
        pessoa.setor = setor_licitacao2
        pessoa.user = user_licitacao2
        pessoa.save()


        user_licitacao2.groups.add(grupo_pregao)

        user_compras2 = User.objects.get_or_create(username=u'compras2',is_active=True,is_superuser=False, is_staff=True,password=u'pbkdf2_sha256$20000$THrN7vMCbCch$hvQF8rxuA0EZ6A0Z/q2+izYd4u226ic/XaHXHQ/rJhg=', date_joined=u'2016-06-06T15:52:27.985')[0]
        #pessoa = PessoaFisica.objects.get_or_create(nome=u'Comprador da Tributação', cpf=u'12345678900',sexo=PessoaFisica.SEXO_MASCULINO, setor=setor_compras2, user=user_compras2)[0]
        pessoa = PessoaFisica()
        pessoa.nome = u'Comprador da Tributação'
        pessoa.cpf = u'12345678900'
        pessoa.sexo = PessoaFisica.SEXO_MASCULINO
        pessoa.setor = setor_compras2
        pessoa.user = user_compras2
        pessoa.save()

        user_compras2.groups.add(grupo_compras)

        user_juridico2 = User.objects.get_or_create(username=u'juridico2',is_active=True,is_superuser=False, is_staff=True,password=u'pbkdf2_sha256$20000$THrN7vMCbCch$hvQF8rxuA0EZ6A0Z/q2+izYd4u226ic/XaHXHQ/rJhg=', date_joined=u'2016-06-06T15:52:27.985')[0]
        #pessoa = PessoaFisica.objects.get_or_create(nome=u'Jurídico da Tributação', cpf=u'12345678900',sexo=PessoaFisica.SEXO_MASCULINO, setor=setor_juridico2, user=user_juridico2)[0]

        pessoa = PessoaFisica()
        pessoa.nome = u'Jurídico da Tributação'
        pessoa.cpf = u'12345678900'
        pessoa.sexo = PessoaFisica.SEXO_MASCULINO
        pessoa.setor = setor_juridico2
        pessoa.user = user_juridico2
        pessoa.save()
        user_juridico2.groups.add(grupo_juridico)


        user_protocolo2 = User.objects.get_or_create(username=u'protocolo2',is_active=True,is_superuser=False, is_staff=True,password=u'pbkdf2_sha256$20000$THrN7vMCbCch$hvQF8rxuA0EZ6A0Z/q2+izYd4u226ic/XaHXHQ/rJhg=', date_joined=u'2016-06-06T15:52:27.985')[0]
        #pessoa = PessoaFisica.objects.get_or_create(nome=u'Protocolo da Tributação', cpf=u'12345678900',sexo=PessoaFisica.SEXO_MASCULINO, setor=setor_protoloco, user=user_protocolo2)[0]

        pessoa = PessoaFisica()
        pessoa.nome = u'Protocolo da Tributação'
        pessoa.cpf = u'12345678900'
        pessoa.sexo = PessoaFisica.SEXO_MASCULINO
        pessoa.setor = setor_protocolo2
        pessoa.user = user_protocolo2
        pessoa.save()
        user_protocolo2.groups.add(grupo_protocolo)


        user_secretaria3 = User.objects.get_or_create(username=u'secretaria3',is_active=True,is_superuser=False, is_staff=True,password=u'pbkdf2_sha256$20000$THrN7vMCbCch$hvQF8rxuA0EZ6A0Z/q2+izYd4u226ic/XaHXHQ/rJhg=', date_joined=u'2016-06-06T15:52:27.985')[0]
        #pessoa = PessoaFisica.objects.get_or_create(nome=u'Secretário da Saúde', cpf=u'12345678900',sexo=PessoaFisica.SEXO_MASCULINO, setor=setor_secretaria3, user=user_secretaria3)[0]

        pessoa = PessoaFisica()
        pessoa.nome = u'Secretário da Saúde'
        pessoa.cpf = u'12345678900'
        pessoa.sexo = PessoaFisica.SEXO_MASCULINO
        pessoa.setor = setor_secretaria3
        pessoa.user = user_secretaria3
        pessoa.save()


        user_secretaria3.groups.add(grupo_secretaria)

        user_licitacao3 = User.objects.get_or_create(username=u'pregoeiro3',is_active=True,is_superuser=False, is_staff=True,password=u'pbkdf2_sha256$20000$THrN7vMCbCch$hvQF8rxuA0EZ6A0Z/q2+izYd4u226ic/XaHXHQ/rJhg=', date_joined=u'2016-06-06T15:52:27.985')[0]
        #pessoa = PessoaFisica.objects.get_or_create(nome=u'Pregoeiro da Saúde', cpf=u'12345678900',sexo=PessoaFisica.SEXO_MASCULINO, setor=setor_licitacao3, user=user_licitacao3)[0]

        pessoa = PessoaFisica()
        pessoa.nome = u'Pregoeiro da Saúde'
        pessoa.cpf = u'12345678900'
        pessoa.sexo = PessoaFisica.SEXO_MASCULINO
        pessoa.setor = setor_licitacao3
        pessoa.user = user_licitacao3
        pessoa.save()
        user_licitacao3.groups.add(grupo_pregao)

        user_compras3 = User.objects.get_or_create(username=u'compras3',is_active=True,is_superuser=False, is_staff=True,password=u'pbkdf2_sha256$20000$THrN7vMCbCch$hvQF8rxuA0EZ6A0Z/q2+izYd4u226ic/XaHXHQ/rJhg=', date_joined=u'2016-06-06T15:52:27.985')[0]
        #pessoa = PessoaFisica.objects.get_or_create(nome=u'Compras da Saúde', cpf=u'12345678900',sexo=PessoaFisica.SEXO_MASCULINO, setor=setor_compras3, user=user_compras3)[0]

        pessoa = PessoaFisica()
        pessoa.nome = u'Comprador da Saúde'
        pessoa.cpf = u'12345678900'
        pessoa.sexo = PessoaFisica.SEXO_MASCULINO
        pessoa.setor = setor_compras3
        pessoa.user = user_compras3
        pessoa.save()
        user_compras3.groups.add(grupo_compras)

        user_juridico3 = User.objects.get_or_create(username=u'juridico3',is_active=True,is_superuser=False, is_staff=True,password=u'pbkdf2_sha256$20000$THrN7vMCbCch$hvQF8rxuA0EZ6A0Z/q2+izYd4u226ic/XaHXHQ/rJhg=', date_joined=u'2016-06-06T15:52:27.985')[0]
        #pessoa = PessoaFisica.objects.get_or_create(nome=u'Jurídico da Saúde', cpf=u'12345678900',sexo=PessoaFisica.SEXO_MASCULINO, setor=setor_juridico3, user=user_juridico3)[0]

        pessoa = PessoaFisica()
        pessoa.nome = u'Jurídico da Saúde'
        pessoa.cpf = u'12345678900'
        pessoa.sexo = PessoaFisica.SEXO_MASCULINO
        pessoa.setor = setor_juridico3
        pessoa.user = user_juridico3
        pessoa.save()
        user_juridico3.groups.add(grupo_juridico)


        user_protocolo3 = User.objects.get_or_create(username=u'protocolo3',is_active=True,is_superuser=False, is_staff=True,password=u'pbkdf2_sha256$20000$THrN7vMCbCch$hvQF8rxuA0EZ6A0Z/q2+izYd4u226ic/XaHXHQ/rJhg=', date_joined=u'2016-06-06T15:52:27.985')[0]
        #pessoa = PessoaFisica.objects.get_or_create(nome=u'Protocolo da Saúde', cpf=u'12345678900',sexo=PessoaFisica.SEXO_MASCULINO, setor=setor_protoloco, user=user_protocolo3)[0]

        pessoa = PessoaFisica()
        pessoa.nome = u'Protocolo da Saúde'
        pessoa.cpf = u'12345678900'
        pessoa.sexo = PessoaFisica.SEXO_MASCULINO
        pessoa.setor = setor_protocolo3
        pessoa.user = user_protocolo3
        pessoa.save()
        user_protocolo3.groups.add(grupo_protocolo)


        user_ordenador = User.objects.get_or_create(username=u'ordenador',is_active=True,is_superuser=False, is_staff=True,password=u'pbkdf2_sha256$20000$THrN7vMCbCch$hvQF8rxuA0EZ6A0Z/q2+izYd4u226ic/XaHXHQ/rJhg=', date_joined=u'2016-06-06T15:52:27.985')[0]
        #pessoa = PessoaFisica.objects.get_or_create(nome=u'Protocolo da Saúde', cpf=u'12345678900',sexo=PessoaFisica.SEXO_MASCULINO, setor=setor_protoloco, user=user_protocolo3)[0]

        ordenador = PessoaFisica()
        ordenador.nome = u'Ordenador de Despesa'
        ordenador.cpf = u'12345678900'
        ordenador.sexo = PessoaFisica.SEXO_MASCULINO
        ordenador.setor = setor_secretaria
        ordenador.user = user_ordenador
        ordenador.save()




        ramo1 = RamoAtividade.objects.get_or_create(nome=u'Ramo de Atividade 1')[0]
        ramo2 = RamoAtividade.objects.get_or_create(nome=u'Ramo de Atividade 2')[0]

        empresa1 = Fornecedor.objects.get_or_create(cnpj=u'01.111.2345/0001-89', razao_social=u'Empresa 1',endereco=u'Endereco da empresa 1',ramo_atividade=ramo1)[0]
        empresa2 = Fornecedor.objects.get_or_create(cnpj=u'02.222.253/0001-90', razao_social=u'Empresa 2',endereco=u'Endereco da empresa 2',ramo_atividade=ramo1)[0]
        empresa3 = Fornecedor.objects.get_or_create(cnpj=u'03.333.253/0001-90', razao_social=u'Empresa 3',endereco=u'Endereco da empresa 3',ramo_atividade=ramo1)[0]
        empresa4 = Fornecedor.objects.get_or_create(cnpj=u'04.444.253/0001-90', razao_social=u'Empresa 4',endereco=u'Endereco da empresa 4',ramo_atividade=ramo2)[0]
        empresa5 = Fornecedor.objects.get_or_create(cnpj=u'05.555.253/0001-90', razao_social=u'Empresa 5',endereco=u'Endereco da empresa 5',ramo_atividade=ramo2)[0]
        empresa6 = Fornecedor.objects.get_or_create(cnpj=u'06.666.253/0001-90', razao_social=u'Empresa 6',endereco=u'Endereco da empresa 6',ramo_atividade=ramo2)[0]

        # solicitacao1= SolicitacaoLicitacao.objects.get_or_create(num_memorando=u'123/DI_RN', objeto=u'Objeto da licitacao 1', objetivo=u'Objetivo da licit. 1', justificativa=u'Justificativa da licitacao 1', data_cadastro=datetime.datetime.now())[0]
        # item1sol1 = ItemSolicitacaoLicitacao.objects.get_or_create(codigo=u'134', solicitacao=solicitacao1,item=u'1', especificacao=u'Especificacaodo item 1', unidade=uni1, quantidade=100, valor_medio=10.50, total=1050.00)[0]
        # item2sol1 = ItemSolicitacaoLicitacao.objects.get_or_create(codigo=u'222', solicitacao=solicitacao1,item=u'2', especificacao=u'Especificacaodo item 2', unidade=uni2, quantidade=50, valor_medio=20.00, total=1000.00)[0]
        # item3sol1 = ItemSolicitacaoLicitacao.objects.get_or_create(codigo=u'5687', solicitacao=solicitacao1,item=u'3', especificacao=u'Especificacaodo item 3', unidade=uni3, quantidade=10, valor_medio=5.00, total=50.00)[0]
        #
        #
        #
        # solicitacao2= SolicitacaoLicitacao.objects.get_or_create(num_memorando=u'987/DI_RN', objeto=u'Objeto da licitacao 2', objetivo=u'Objetivo da licit. 2', justificativa=u'Justificativa da licitacao 2', data_cadastro=datetime.datetime.now())[0]

        municipio = Municipio.objects.get(nome=u'GUAMARE')

        Configuracao.objects.get_or_create(nome=u'PREFEITURA MUNICIPAL DE GUAMARÉ', endereco=u'RUA LUIZ DE SOUZA MIRANDA', email=u'cpl.guamare@gmail.com', municipio=municipio, telefones=u'8435252966', ordenador_despesa=ordenador, logo=u'upload/logo/logo.jpg')