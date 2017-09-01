$("#id_data_inicial").parent().parent().parent().parent().parent().hide();
$("#id_opcoes").parent().parent().parent().parent().parent().hide();
$('.controls').hide();

 function exibir_esconder_campo() {

    if ($('#id_opcoes').val() == 'Reajuste Econômico-financeiro') {

        $("#id_indice_reajuste").parent().parent().show();
        $("#id_percentual_acrescimo_valor").parent().parent().hide();
        $("#id_percentual_acrescimo_quantitativos").parent().parent().hide();
        $("#itens").hide();
        $("#valores_contratos").show();

    }

    if($('#id_opcoes').val() == 'Acréscimo de Valor' | $('#id_opcoes').val() == 'Supressão de Valor') {

        $("#id_indice_reajuste").parent().parent().hide();
        $("#id_percentual_acrescimo_quantitativos").parent().parent().hide();
        $("#id_percentual_acrescimo_valor").parent().parent().show();
        $("#itens").show();
        $('.coluna_valor').show();
        $('.coluna_quantidade').hide();
        $('.coluna_quantidade_subtrai').hide();
        $('.coluna_quantidade_soma').hide();
        $("#valores_contratos").hide();




        if($('#id_opcoes').val() == 'Acréscimo de Valor'){
            $('.coluna_valor_soma').show();
            $('.coluna_valor_subtrai').hide();

        }
        if($('#id_opcoes').val() == 'Supressão de Valor'){
            $('.coluna_valor_soma').hide();
            $('.coluna_valor_subtrai').show();

        }

    }

    if($('#id_opcoes').val() == 'Acréscimo de Quantitativos' | $('#id_opcoes').val() == 'Supressão de Quantitativo') {

        $("#id_indice_reajuste").parent().parent().hide();
        $("#id_percentual_acrescimo_quantitativos").parent().parent().show();
        $("#id_percentual_acrescimo_valor").parent().parent().hide();
        $("#itens").show();
        $('.coluna_valor').hide();
        $('.coluna_quantidade').show();
        $('.coluna_valor_subtrai').hide();
        $('.coluna_valor_soma').hide();
        $("#valores_contratos").hide();
        if($('#id_opcoes').val() == 'Acréscimo de Quantitativos'){
            $('.coluna_quantidade_soma').show();
            $('.coluna_quantidade_subtrai').hide();

        }
        if($('#id_opcoes').val() == 'Supressão de Quantitativo'){
            $('.coluna_quantidade_soma').hide();
            $('.coluna_quantidade_subtrai').show();

        }
    }

    if ($('#id_opcoes').val() == '') {

        $("#id_indice_reajuste").parent().parent().hide();
        $("#id_percentual_acrescimo_quantitativos").parent().parent().hide();
        $("#id_percentual_acrescimo_valor").parent().parent().hide();
        $("#itens").hide();
        $("#valores_contratos").hide();
    }

    if ($('#id_tipo_aditivo').val() == 'Valor') {
        $("#id_data_inicial").parent().parent().parent().parent().parent().hide();
        $("#id_opcoes").parent().parent().parent().parent().parent().show();
        $('.controls').show();

    }
    if ($('#id_tipo_aditivo').val() == 'Prazo') {
        $("#id_data_inicial").parent().parent().parent().parent().parent().show();
        $("#id_opcoes").parent().parent().parent().parent().parent().hide();
        $('.controls').show();
    }
    if ($('#id_tipo_aditivo').val() == 'Todos') {
        $("#id_data_inicial").parent().parent().parent().parent().parent().show();
        $("#id_opcoes").parent().parent().parent().parent().parent().show();
        $('.controls').show();
    }



 }
  $(document).ready(function() {
    exibir_esconder_campo();
    $("#id_opcoes").on('change', function(){
      exibir_esconder_campo();
    });
    $("#id_tipo_aditivo").on('change', function(){
      exibir_esconder_campo();
    });


});
