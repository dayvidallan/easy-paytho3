$(document).ready(function() {
	$("#dados").hide();


	$("#buscapessoa").click(function(event) {
		$("#mensagem_erro").hide();
		botao = $("#buscapessoa");
		valor_antigo = botao.html();
		pessoa = $('#id_campo_busca').val();
		botao.html('<span class="fa fa-spinner fa-spin"></span>');
		console.log('aaaaaaaaaa');

		$.ajax({
			method: "GET",
			url: "/busca_pessoa/",
			data: { "pessoa": pessoa },
			success: function(result, textStatus, jqXHR) {
				$("#nome_do_medico").parent().parent().show();
				$("#id_medico_especialidade").parent().parent().show();
				$("#id_receita").parent().parent().show();
				$("#ativar-webcam").parent().parent().show();
				$("#id_obs").parent().parent().show();
				$("#nome_do_medico").val(result[0].fields.nome);
				$('#id_medico').val(result[0].pk);
				update_select($('select[name=medico_especialidade]'), crm_medico);
				botao.html(valor_antigo);
			},
			error: function() {
				$('#mensagem_erro').html('Nenhum Médico Encontrado.');
				$('#mensagem_erro').show();
				$("#nome_do_medico").parent().parent().hide();
				$("#id_medico_especialidade").parent().parent().hide();
				$("#id_receita").parent().parent().hide();
				$("#ativar-webcam").parent().parent().hide();
				$("#id_obs").parent().parent().hide();
				botao.html(valor_antigo);
			}
		});

		event.preventDefault();
	});

	$("input[name=tem_diabetes]:radio").on('change', function(){
		if ($('#id_tem_diabetes_0').is(':checked')) {
			$("#id_qual_tipo_diabetes_0").parent().parent().parent().parent().show();
			$("#id_qual_tipo_diabetes_0").prop( "checked", true );
			$("#id_usa_insulina_0").parent().parent().parent().parent().show();
		} else {
			$( "#id_qual_tipo_diabetes_0" ).prop( "checked", false );
			$( "#id_qual_tipo_diabetes_1" ).prop( "checked", false );
			$( "#id_usa_insulina_0" ).prop( "checked", false );
			$("#id_qual_tipo_diabetes_0").parent().parent().parent().parent().hide();
			$("#id_usa_insulina_0").parent().parent().parent().parent().hide();

		}
	});

	$("input[name=tem_glaucoma_na_familia]:radio").on('change', function(){
		if ($('#id_tem_glaucoma_na_familia_0').is(':checked')) {
			$("#id_glaucoma_na_familia").parent().parent().show();
		} else {
			$("#id_glaucoma_na_familia").val('');
			$("#id_glaucoma_na_familia").parent().parent().hide();
		}
	});

	$("input[name=faz_uso_colirio]:radio").on('change', function(){
		if ($('#id_faz_uso_colirio_0').is(':checked')) {
			$("#id_usa_colirio").parent().parent().show();
		} else {
			$("#id_usa_colirio").val('');
			$("#id_usa_colirio").parent().parent().hide();
		}
	});

	$("input[name=ja_fez_cirurgia]:radio").on('change', function(){
		if ($('#id_ja_fez_cirurgia_0').is(':checked')) {
			$("#id_fez_cirurgia_ocular_qual_e_quando").parent().parent().show();

		} else {
			$("#id_fez_cirurgia_ocular_qual_e_quando").val('');
			$("#id_fez_cirurgia_ocular_qual_e_quando").parent().parent().hide();
		}
	});
});
