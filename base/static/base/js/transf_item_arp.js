

$("#id_quantidade_atual").parent().parent().hide();

$(document).ready(function() {

	$("#id_quantidade_atual").parent().parent().hide();


	$("#id_secretaria_origem").on('change', function(event) {
		$("#mensagem_erro").hide();
		botao = $("#buscaestabelecimento");
		valor_antigo = botao.html();
		secretaria = $('#id_secretaria_origem').val();
		item = $('#id_id_do_item').val();
		botao.html('<span class="fa fa-spinner fa-spin"></span>');

		$.ajax({
			method: "GET",
			url: "/base/busca_saldo_atual/",
			data: { "secretaria": secretaria, "item": item },
			success: function(result, textStatus, jqXHR) {
				$("#id_quantidade_atual").parent().parent().show();
				console.log(result);
				$("#id_quantidade_atual").val(result);

				botao.html(valor_antigo);
			},
			error: function() {
				$('#mensagem_erro').html('Nenhum Estabelecimento Encontrado.');
				$('#mensagem_erro').show();
				$("#nome_do_estabelecimento").parent().parent().hide();

				botao.html(valor_antigo);
			}
		});

		event.preventDefault();
	});

});





