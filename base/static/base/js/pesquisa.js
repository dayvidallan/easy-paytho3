 function exibir_esconder_campo() {
    if ($('#id_origem_opcao_0').is(':checked')) {

         $("#id_razao_social").parent().parent().show();
         $("#id_cnpj").parent().parent().show();
         $("#id_endereco").parent().parent().show();
         $("#id_ie").parent().parent().show();
         $("#id_telefone").parent().parent().show();
         $("#id_email").parent().parent().show();
         $("#id_nome_representante").parent().parent().show();
         $("#id_cpf_representante").parent().parent().show();
         $("#id_rg_representante").parent().parent().show();
         $("#id_endereco_representante").parent().parent().show();


         $("#id_numero_ata").parent().parent().hide();
         $("#id_vigencia_ata").parent().parent().hide();
         $("#id_orgao_gerenciador_ata").parent().parent().hide();




    }
    if ($('#id_origem_opcao_1').is(':checked')) {

            $("#id_numero_ata").parent().parent().show();
         $("#id_vigencia_ata").parent().parent().show();
         $("#id_orgao_gerenciador_ata").parent().parent().show();


        $("#id_razao_social").parent().parent().hide();
         $("#id_cnpj").parent().parent().hide();
         $("#id_endereco").parent().parent().hide();
         $("#id_ie").parent().parent().hide();
         $("#id_telefone").parent().parent().hide();
         $("#id_email").parent().parent().hide();
         $("#id_nome_representante").parent().parent().hide();
         $("#id_cpf_representante").parent().parent().hide();
         $("#id_rg_representante").parent().parent().hide();
         $("#id_endereco_representante").parent().parent().hide();
    }

 }


  $(document).ready(function() {

     $("#id_razao_social").parent().parent().hide();
     $("#id_cnpj").parent().parent().hide();
     $("#id_endereco").parent().parent().hide();
     $("#id_ie").parent().parent().hide();
     $("#id_telefone").parent().parent().hide();
     $("#id_email").parent().parent().hide();
     $("#id_nome_representante").parent().parent().hide();
     $("#id_cpf_representante").parent().parent().hide();
     $("#id_rg_representante").parent().parent().hide();
     $("#id_endereco_representante").parent().parent().hide();

     $("#id_numero_ata").parent().parent().hide();
     $("#id_vigencia_ata").parent().parent().hide();
     $("#id_orgao_gerenciador_ata").parent().parent().hide();

     exibir_esconder_campo();

     $("input[name=origem_opcao]:radio").on('change', function(){
      exibir_esconder_campo();
    });
});