 function exibir_esconder_campo() {
    if ($('#id_sem_representante').is(':checked')) {
        $("#id_obs_ausencia_participante").parent().parent().show();
        $("#id_nome_representante").parent().parent().hide();
        $("#id_cpf_representante").parent().parent().hide();

    } else {
        $("#id_obs_ausencia_participante").parent().parent().hide();
        $("#id_nome_representante").parent().parent().show();
        $("#id_cpf_representante").parent().parent().show();

    }

 }


  $(document).ready(function() {

     exibir_esconder_campo();

     $('#id_sem_representante').on('change', function(){
        exibir_esconder_campo();
    });
});