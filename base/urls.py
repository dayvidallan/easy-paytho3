# coding: utf-8

from django.conf.urls import patterns, url
from base import views
from base.views import SecretariaAutocomplete, ParticipantePregaoAutocomplete, PessoaFisicaAutocomplete, MaterialConsumoAutocomplete

urlpatterns = patterns('base.views',
    url(r'^$', views.index, name='index'),
    url(r'^solicitacoes/$', views.solicitacoes, name='solicitacoes'),
    url(r'^cadastros/$', views.cadastros, name='cadastros'),
    url(r'^licitacoes/$', views.licitacoes, name='licitacoes'),
    url(r'^pedidos_e_controle/$', views.pedidos_e_controle, name='pedidos_e_controle'),
    url(r'^administracao/$', views.administracao, name='administracao'),
    url(r'^pregao/(?P<pregao_id>\d+)/$', views.pregao, name='pregao'),
    url(r'^itens_solicitacao/(?P<solicitacao_id>\d+)/$', views.itens_solicitacao, name='itens_solicitacao'),
    url(r'^cadastrar_item_solicitacao/(?P<solicitacao_id>\d+)/$', views.cadastrar_item_solicitacao, name='cadastrar_item_solicitacao'),
    url(r'^cadastra_proposta_pregao/(?P<pregao_id>\d+)/$', views.cadastra_proposta_pregao, name='cadastra_proposta_pregao'),
    url(r'^propostas_item/(?P<item_id>\d+)/$', views.propostas_item, name='propostas_item'),
    url(r'^lances_item/(?P<item_id>\d+)/$', views.lances_item, name='lances_item'),
    url(r'^rodada_pregao/(?P<item_id>\d+)/$', views.rodada_pregao, name='rodada_pregao'),
    url(r'^declinar_lance/(?P<rodada_id>\d+)/(?P<item_id>\d+)/(?P<participante_id>\d+)/$', views.declinar_lance, name='declinar_lance'),
    url(r'^baixar_editais/$', views.baixar_editais, name='baixar_editais'),
    url(r'^ver_solicitacoes/$', views.ver_solicitacoes, name='ver_solicitacoes'),
    url(r'^rejeitar_solicitacao/(?P<solicitacao_id>\d+)/$', views.rejeitar_solicitacao, name='rejeitar_solicitacao'),
    url(r'^cadastrar_pregao/(?P<solicitacao_id>\d+)/$', views.cadastrar_pregao, name='cadastrar_pregao'),
    url(r'^enviar_para_licitacao/(?P<solicitacao_id>\d+)/$', views.enviar_para_licitacao, name='enviar_para_licitacao'),
    url(r'^movimentar_solicitacao/(?P<solicitacao_id>\d+)/(?P<tipo>\d+)/$', views.movimentar_solicitacao, name='movimentar_solicitacao'),
    url(r'^registrar_preco_item/(?P<item_id>\d+)/$', views.registrar_preco_item, name='registrar_preco_item'),
    url(r'^cadastra_participante_pregao/(?P<pregao_id>\d+)/$', views.cadastra_participante_pregao, name='cadastra_participante_pregao'),
    url(r'^ver_fornecedores/$', views.ver_fornecedores, name='ver_fornecedores'),
    url(r'^ver_fornecedores/(?P<fornecedor_id>\d+)/$', views.ver_fornecedores, name='ver_fornecedores'),
    url(r'^ver_pregoes/$', views.ver_pregoes, name='ver_pregoes'),
    url(r'^cadastrar_solicitacao/$', views.cadastrar_solicitacao, name='cadastrar_solicitacao'),
    url(r'^pesquisa_mercadologica/(?P<solicitacao_id>\d+)/$', views.pesquisa_mercadologica, name='pesquisa_mercadologica'),
    url(r'^preencher_pesquisa_mercadologica/(?P<solicitacao_id>\d+)/$', views.preencher_pesquisa_mercadologica, name='preencher_pesquisa_mercadologica'),
    url(r'^preencher_itens_pesquisa_mercadologica/(?P<pesquisa_id>\d+)/$', views.preencher_itens_pesquisa_mercadologica, name='preencher_itens_pesquisa_mercadologica'),
    url(r'^upload_pesquisa_mercadologica/(?P<pesquisa_id>\d+)/$', views.upload_pesquisa_mercadologica, name='upload_pesquisa_mercadologica'),
    url(r'^imprimir_pesquisa/(?P<pesquisa_id>\d+)/$', views.imprimir_pesquisa, name='imprimir_pesquisa'),
    url(r'^ver_pesquisa_mercadologica/(?P<item_id>\d+)/$', views.ver_pesquisa_mercadologica, name='ver_pesquisa_mercadologica'),
    url(r'^resultado_classificacao/(?P<item_id>\d+)/$', views.resultado_classificacao, name='resultado_classificacao'),
    url(r'^desclassificar_do_pregao/(?P<participante_id>\d+)/$', views.desclassificar_do_pregao, name='desclassificar_do_pregao'),
    url(r'^planilha_propostas/(?P<solicitacao_id>\d+)/$', views.planilha_propostas, name='planilha_propostas'),
    url(r'^remover_participante/(?P<proposta_id>\d+)/(?P<situacao>\d+)/$', views.remover_participante, name='remover_participante'),
    url(r'^adicionar_por_discricionaridade/(?P<proposta_id>\d+)/$', views.adicionar_por_discricionaridade, name='adicionar_por_discricionaridade'),
    url(r'^gerar_resultado/(?P<item_id>\d+)/$', views.gerar_resultado, name='gerar_resultado'),
    url(r'^resultado_alterar/(?P<resultado_id>\d+)/(?P<situacao>\d+)/$', views.resultado_alterar, name='resultado_alterar'),
    url(r'^resultado_ajustar_preco/(?P<resultado_id>\d+)/$', views.resultado_ajustar_preco, name='resultado_ajustar_preco'),
    url(r'^desempatar_item/(?P<item_id>\d+)/$', views.desempatar_item, name='desempatar_item'),
    url(r'^definir_colocacao/(?P<resultado_id>\d+)/$', views.definir_colocacao, name='definir_colocacao'),
    url(r'^cadastrar_anexo_pregao/(?P<pregao_id>\d+)/$', views.cadastrar_anexo_pregao, name='cadastrar_anexo_pregao'),
    url(r'^baixar_arquivo/(?P<arquivo_id>\d+)/$', views.baixar_arquivo, name='baixar_arquivo'),
    url(r'^alterar_valor_lance/(?P<lance_id>\d+)/$', views.alterar_valor_lance, name='alterar_valor_lance'),
    url(r'^avancar_proximo_item/(?P<item_id>\d+)/$', views.avancar_proximo_item, name='avancar_proximo_item'),
    url(r'^cancelar_rodada/(?P<item_id>\d+)/$', views.cancelar_rodada, name='cancelar_rodada'),
    url(r'^editar_proposta/(?P<proposta_id>\d+)/$', views.editar_proposta, name='editar_proposta'),
    url(r'^encerrar_pregao/(?P<pregao_id>\d+)/(?P<motivo>\d+)/$', views.encerrar_pregao, name='encerrar_pregao'),
    url(r'^encerrar_itempregao/(?P<item_id>\d+)/(?P<motivo>\d+)/$', views.encerrar_itempregao, name='encerrar_itempregao'),
    url(r'^suspender_pregao/(?P<pregao_id>\d+)/$', views.suspender_pregao, name='suspender_pregao'),
    url(r'^prazo_pesquisa_mercadologica/(?P<solicitacao_id>\d+)/$', views.prazo_pesquisa_mercadologica, name='prazo_pesquisa_mercadologica'),
    url(r'^resultado_alterar_todos/(?P<pregao_id>\d+)/(?P<participante_id>\d+)/(?P<situacao>\d+)/$', views.resultado_alterar_todos, name='resultado_alterar_todos'),
    url(r'^modelo_memorando/(?P<solicitacao_id>\d+)/$', views.modelo_memorando, name='modelo_memorando'),
    url(r'^receber_solicitacao/(?P<solicitacao_id>\d+)/$', views.receber_solicitacao, name='receber_solicitacao'),
    url(r'^ver_movimentacao/(?P<solicitacao_id>\d+)/$', views.ver_movimentacao, name='ver_movimentacao'),
    url(r'^cadastrar_minuta/(?P<solicitacao_id>\d+)/$', views.cadastrar_minuta, name='cadastrar_minuta'),
    url(r'^avalia_minuta/(?P<solicitacao_id>\d+)/(?P<tipo>\d+)/$', views.avalia_minuta, name='avalia_minuta'),
    url(r'^retomar_lances/(?P<item_id>\d+)/$', views.retomar_lances, name='retomar_lances'),
    url(r'^informar_quantidades/(?P<solicitacao_id>\d+)/$', views.informar_quantidades, name='informar_quantidades'),
    url(r'^ver_pedidos_secretaria/(?P<item_id>\d+)/$', views.ver_pedidos_secretaria, name='ver_pedidos_secretaria'),
    url(r'^importar_itens/(?P<solicitacao_id>\d+)/$', views.importar_itens, name='importar_itens'),
    url(r'^planilha_pesquisa_mercadologica/(?P<solicitacao_id>\d+)/$', views.planilha_pesquisa_mercadologica, name='planilha_pesquisa_mercadologica'),
    url(r'^upload_itens_pesquisa_mercadologica/(?P<pesquisa_id>\d+)/$', views.upload_itens_pesquisa_mercadologica, name='upload_itens_pesquisa_mercadologica'),
    url(r'^relatorio_resultado_final/(?P<pregao_id>\d+)/$', views.relatorio_resultado_final, name='relatorio_resultado_final'),
    url(r'^relatorio_resultado_final_por_vencedor/(?P<pregao_id>\d+)/$', views.relatorio_resultado_final_por_vencedor, name='relatorio_resultado_final_por_vencedor'),
    url(r'^relatorio_lista_participantes/(?P<pregao_id>\d+)/$', views.relatorio_lista_participantes, name='relatorio_lista_participantes'),
    url(r'^relatorio_classificacao_por_item/(?P<pregao_id>\d+)/$', views.relatorio_classificacao_por_item, name='relatorio_classificacao_por_item'),
    url(r'^relatorio_ocorrencias/(?P<pregao_id>\d+)/$', views.relatorio_ocorrencias, name='relatorio_ocorrencias'),
    url(r'^relatorio_lances_item/(?P<pregao_id>\d+)/$', views.relatorio_lances_item, name='relatorio_lances_item'),
    url(r'^relatorio_ata_registro_preco/(?P<pregao_id>\d+)/$', views.relatorio_ata_registro_preco, name='relatorio_ata_registro_preco'),
    url(r'^pedido_outro_interessado/(?P<pedido_id>\d+)/(?P<opcao>\d+)/$', views.pedido_outro_interessado, name='pedido_outro_interessado'),
    url(r'^abrir_processo_para_solicitacao/(?P<solicitacao_id>\d+)/$', views.abrir_processo_para_solicitacao, name='abrir_processo_para_solicitacao'),
    url(r'^ver_processo/(?P<processo_id>\d+)/$', views.ver_processo, name='ver_processo'),
    url(r'^imprimir_capa_processo/(?P<processo_id>\d+)/$', views.imprimir_capa_processo, name='imprimir_capa_processo'),
    url(r'^criar_lote/(?P<pregao_id>\d+)/$', views.criar_lote, name='criar_lote'),
    url(r'^extrato_inicial/(?P<pregao_id>\d+)/$', views.extrato_inicial, name='extrato_inicial'),
    url(r'^termo_adjudicacao/(?P<pregao_id>\d+)/$', views.termo_adjudicacao, name='termo_adjudicacao'),
    url(r'^editar_meu_perfil/(?P<pessoa_id>\d+)/$', views.editar_meu_perfil, name='editar_meu_perfil'),
    url(r'^editar_pedido/(?P<pedido_id>\d+)/$', views.editar_pedido, name='editar_pedido'),
    url(r'^aprovar_todos_pedidos/(?P<item_id>\d+)/$', views.aprovar_todos_pedidos, name='aprovar_todos_pedidos'),
    url(r'^gestao_pedidos/$', views.gestao_pedidos, name='gestao_pedidos'),
    url(r'^avaliar_pedidos/(?P<solicitacao_id>\d+)/$', views.avaliar_pedidos, name='avaliar_pedidos'),
    url(r'^aprovar_todos_pedidos_secretaria/(?P<solicitacao_id>\d+)/(?P<secretaria_id>\d+)/$', views.aprovar_todos_pedidos_secretaria, name='aprovar_todos_pedidos_secretaria'),
    url(r'^novo_pedido_compra/(?P<solicitacao_id>\d+)/$', views.novo_pedido_compra, name='novo_pedido_compra'),
    url(r'^informar_quantidades_do_pedido/(?P<solicitacao_original>\d+)/(?P<nova_solicitacao>\d+)/$', views.informar_quantidades_do_pedido, name='informar_quantidades_do_pedido'),
    url(r'^apagar_anexo_pregao/(?P<item_id>\d+)/$', views.apagar_anexo_pregao, name='apagar_anexo_pregao'),
    url(r'^gerar_pedido_fornecedores/(?P<solicitacao_id>\d+)/$', views.gerar_pedido_fornecedores, name='gerar_pedido_fornecedores'),
    url(r'^apagar_lote/(?P<item_id>\d+)/(?P<pregao_id>\d+)/$', views.apagar_lote, name='apagar_lote'),
    url(r'^informar_valor_final_item_lote/(?P<item_id>\d+)/(?P<pregao_id>\d+)/$', views.informar_valor_final_item_lote, name='informar_valor_final_item_lote'),
    url(r'^gerar_ordem_compra/(?P<solicitacao_id>\d+)/$', views.gerar_ordem_compra, name='gerar_ordem_compra'),
    url(r'^ver_ordem_compra/(?P<solicitacao_id>\d+)/$', views.ver_ordem_compra, name='ver_ordem_compra'),



    url(r'^gerenciar_grupos/$', views.gerenciar_grupos, name='gerenciar_grupos'),
    url(r'^gerenciar_grupo_usuario/(?P<usuario_id>\d+)/(?P<grupo_id>\d+)/(?P<acao>\d+)/$', views.gerenciar_grupo_usuario, name='gerenciar_grupo_usuario'),


    url(r'^secretaria-autocomplete/$', SecretariaAutocomplete.as_view(), name='secretaria-autocomplete'),
    url(r'^participantepregao-autocomplete/$', ParticipantePregaoAutocomplete.as_view(), name='participantepregao-autocomplete'),
    url(r'^pessoafisica-autocomplete/$', PessoaFisicaAutocomplete.as_view(), name='pessoafisica-autocomplete'),
    url(r'^materialconsumo-autocomplete/$', MaterialConsumoAutocomplete.as_view(), name='materialconsumo-autocomplete'),

)


