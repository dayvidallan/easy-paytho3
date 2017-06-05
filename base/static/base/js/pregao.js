 function exibir_esconder_campo() {


    if ($('#id_modalidade').val() == 1) {
        $('#id_fundamento_legal').val('Fundamento Legal – Lei 8.666/93, art. 22, II');
    }

    if ($('#id_modalidade').val() == 2) {
        $('#id_fundamento_legal').val('Fundamento Legal –Lei 8.666/93, art. 22, I');
    }

    if ($('#id_modalidade').val() == 3) {
        $('#id_fundamento_legal').val('Fundamento Legal – Lei 8.666/93, art. 22, IV');
    }




    if ($('#id_modalidade').val() == 4) {
        $('#id_fundamento_legal').val('Fundamento Legal – Lei 10.520/06, art. 1°');
    }
    if ($('#id_modalidade').val() == 6) {
        $('#id_fundamento_legal').val('Fundamento Legal – Lei 8.666/93, art. 25, caput');
    }
    if ($('#id_modalidade').val() == 7) {
        $('#id_fundamento_legal').val('Fundamento Legal – Lei 11.947/09, art. 14, § 1°');
    }
    if ($('#id_modalidade').val() == 8) {
        $('#id_fundamento_legal').val('');
    }
    if ($('#id_modalidade').val() == 9) {
        $('#id_fundamento_legal').val('Fundamento Legal – Lei 12.188/10, art. 19');
    }



    if ($('#id_modalidade').val() == 10) {
        $('#id_fundamento_legal').val('Fundamento Legal – Lei 10.520/06, art. 11');
    }
    if ($('#id_modalidade').val() == 11) {
        $('#id_fundamento_legal').val('Fundamento Legal – Lei 8.666/93, art. 15, II e §§ 1º a 6º');
    }



 }


  $(document).ready(function() {

    exibir_esconder_campo();

    $('#id_modalidade').on('change', function(){
        exibir_esconder_campo();
    });
  });
