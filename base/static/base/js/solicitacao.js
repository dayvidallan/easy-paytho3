 function exibir_esconder_campo() {

    if ($('#id_outros_interessados').is(':checked')) {


        $("#id_todos_interessados").parent().parent().show();
        $("#id_prazo_resposta_interessados").parent().parent().show();

    } else {

        $("#id_interessados").parent().parent().hide();
        $("#id_todos_interessados").parent().parent().hide();
        $("#id_prazo_resposta_interessados").parent().parent().hide();

    }

    if ($('#id_todos_interessados').is(':checked')) {
        $("#id_interessados").parent().parent().hide();

    }
    else {
        if ($('#id_outros_interessados').is(':checked')) {
            $("#id_interessados").parent().parent().show();
        }
    }


    if ($('#id_contratacao_global').is(':checked')) {
        $("#id_numero_meses_contratacao_global").parent().parent().show();

    }
    else {
        $("#id_numero_meses_contratacao_global").parent().parent().hide();
    }

 }


  $(document).ready(function() {

     exibir_esconder_campo();

     $('#id_outros_interessados').on('change', function(){
        exibir_esconder_campo();
    });
    $('#id_todos_interessados').on('change', function(){
        exibir_esconder_campo();
    });

    $('#id_contratacao_global').on('change', function(){
        exibir_esconder_campo();
    });
});
