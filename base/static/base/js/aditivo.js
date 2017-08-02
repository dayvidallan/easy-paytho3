 function exibir_esconder_campo() {

    if ($('#id_opcoes').val() == 'Reajuste Econômico-financeiro') {

        $("#id_indice_reajuste").parent().parent().show();
        $("#id_percentual_acrescimo_valor").parent().parent().hide();
        $("#id_percentual_acrescimo_quantitativos").parent().parent().hide();
        $("#itens").hide();
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
        if($('#id_opcoes').val() == 'Acréscimo de Quantitativos'){
            $('.coluna_quantidade_soma').show();
            $('.coluna_quantidade_subtrai').hide();

        }
        if($('#id_opcoes').val() == 'Supressão de Quantitativos'){
            $('.coluna_quantidade_soma').hide();
            $('.coluna_quantidade_subtrai').show();

        }
    }

    if ($('#id_opcoes').val() == '') {

        $("#id_indice_reajuste").parent().parent().hide();
        $("#id_percentual_acrescimo_quantitativos").parent().parent().hide();
        $("#id_percentual_acrescimo_valor").parent().parent().hide();
        $("#itens").hide();
    }



 }
  $(document).ready(function() {
    exibir_esconder_campo();
    $("#id_opcoes").on('change', function(){
      exibir_esconder_campo();
    });


});
