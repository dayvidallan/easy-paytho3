$(document).ready(function() {
	$('#mensagem_erro').hide();

	$("#buscapessoa").click(function(event) {
		$("#mensagem_erro").hide();
		$('#dados').show();
		botao = $("#buscapessoa");
		valor_antigo = botao.html();
		pessoa = $('#id_campo_busca').val();
		botao.html('<span class="fa fa-spinner fa-spin"></span>');

		$.ajax({
			method: "GET",
			url: "/busca_pessoa/",
			data: { "pessoa": pessoa },
			success: function(result, textStatus, jqXHR) {
				$("#id_cnpj").val(result[0].fields.cnpj);
				$("#id_cpf").val(result[0].fields.cpf);
				$("#id_nome").val(result[0].fields.nome);
				$("#id_responsavel").val(result[0].fields.responsavel);
				$("#id_endereco").val(result[0].fields.endereco);
				$("#id_email").val(result[0].fields.email);
				$("#id_telefone").val(result[0].fields.telefone);
				//$("#id_estado option:eq("+result[0].fields.estado+")").attr("selected", "selected");
				$("#id_estado").val(result[0].fields.estado).change();
				//$('#id_estado option')[result[0].fields.estado].selected = true;
				$("#id_municipio").val(result[0].fields.municipio);

				botao.html(valor_antigo);
			},
			error: function() {
				$("#dados").show();
				$('#mensagem_erro').html('Nenhum Registro Encontrado. Preencha as Infomações Abaixo.');
				$('#mensagem_erro').show();
				botao.html(valor_antigo);
			}
		});

		event.preventDefault();
	});



});
