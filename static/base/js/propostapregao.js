 function exibir_esconder_campo() {
    if ($('#id_preencher').is(':checked')) {
        $("#preencher_itens").show();
        $("#botao_cadastrar").parent().hide();
        $("#id_arquivo").parent().parent().hide();



    } else {
        $("#preencher_itens").hide();
        $("#botao_cadastrar").parent().show();
        $("#id_arquivo").parent().parent().show();

    }

 }


  $(document).ready(function() {

     exibir_esconder_campo();

     $('#id_preencher').on('change', function(){
        exibir_esconder_campo();
    });
});