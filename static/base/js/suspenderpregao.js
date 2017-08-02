 function exibir_esconder_campo() {
    if ($('#id_sine_die').is(':checked')) {
        $("#id_data_retorno").parent().parent().hide();
        $("#id_hora_retorno").parent().parent().hide();

    } else {
        $("#id_data_retorno").parent().parent().show();
        $("#id_hora_retorno").parent().parent().show();

    }

 }


  $(document).ready(function() {

     exibir_esconder_campo();

     $('#id_sine_die').on('change', function(){
        exibir_esconder_campo();
    });
});
