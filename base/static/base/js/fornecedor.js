 function exibir_esconder_campo() {
    if ($('#id_suspenso').is(':checked')) {
        $("#id_suspenso_ate").parent().parent().show();
        $("#id_motivo_suspensao").parent().parent().show();


    } else {
        $("#id_suspenso_ate").parent().parent().hide();
        $("#id_motivo_suspensao").parent().parent().hide();

    }

 }


  $(document).ready(function() {

     exibir_esconder_campo();

     $('#id_suspenso').on('change', function(){
        exibir_esconder_campo();
    });
});