 function exibir_esconder_campo() {
    if ($('#id_republicar').is(':checked')) {

        $("#id_hora").parent().parent().show();
        $("#id_data").parent().parent().show();
    }

    else {
        $("#id_hora").parent().parent().hide();
        $("#id_data").parent().parent().hide();

    }

 }
  $(document).ready(function() {
     exibir_esconder_campo();

     $("#id_republicar").on('change', function(){
      exibir_esconder_campo();
    });
});
