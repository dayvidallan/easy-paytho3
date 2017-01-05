 function exibir_esconder_campo() {
    if ($('#id_dotacao').is(':checked')) {
        $("#id_projeto_atividade_num").parent().parent().show();
        $("#id_projeto_atividade_descricao").parent().parent().show();
        $("#id_programa_num").parent().parent().show();
        $("#id_programa_descricao").parent().parent().show();
        $("#id_fonte_num").parent().parent().show();
        $("#id_fonte_descricao").parent().parent().show();
        $("#id_elemento_despesa_num").parent().parent().show();
        $("#id_elemento_despesa_descricao").parent().parent().show();

    } else {
        $("#id_projeto_atividade_num").parent().parent().hide();
        $("#id_projeto_atividade_descricao").parent().parent().hide();
        $("#id_programa_num").parent().parent().hide();
        $("#id_programa_descricao").parent().parent().hide();
        $("#id_fonte_num").parent().parent().hide();
        $("#id_fonte_descricao").parent().parent().hide();
        $("#id_elemento_despesa_num").parent().parent().hide();
        $("#id_elemento_despesa_descricao").parent().parent().hide();

    }

 }


  $(document).ready(function() {

     exibir_esconder_campo();

     $('#id_dotacao').on('change', function(){
        exibir_esconder_campo();
    });
});