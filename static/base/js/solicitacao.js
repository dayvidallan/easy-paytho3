 function exibir_esconder_campo() {
    if ($('#id_outros_interessados').is(':checked')) {
        $("#id_interessados").parent().parent().show();
        $("#id_prazo_resposta_interessados").parent().parent().show();

    } else {
        $("#id_interessados").parent().parent().hide();
        $("#id_prazo_resposta_interessados").parent().parent().hide();

    }

 }


  $(document).ready(function() {

     exibir_esconder_campo();

     $('#id_outros_interessados').on('change', function(){
        exibir_esconder_campo();
    });
});