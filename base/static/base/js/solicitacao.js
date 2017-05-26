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

 }


  $(document).ready(function() {

     exibir_esconder_campo();

     $('#id_outros_interessados').on('change', function(){
        exibir_esconder_campo();
    });
    $('#id_todos_interessados').on('change', function(){
        exibir_esconder_campo();
    });
});