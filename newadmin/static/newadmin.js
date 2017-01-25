function modal_submit(elem) {
    var form = $(elem).parents("form");
    $.ajax({
        type: form.attr("method"),
        url: form.attr("action"),
        data: form.serialize(),
        dataType: "html",
        success: function(data, textStatus, jqXHR) {
            var is_popup_response = data.indexOf('opener.dismissAddAnotherPopup') != -1;
            if (is_popup_response) {
                var update_id = $("#modal").attr("data-update");
                $.get(location.href, function(data) {
                    data = $(data);
                    $("#"+update_id).html(data.find("#"+update_id).html());
                });
                $('#modal button.close').click();
                $.growl('Operação realizada com sucesso.', {type: 'success'});
            } else {
                $("#modal .modal-content").html(data);
                modal_form_init(form.attr("action"));
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            var content = '<div class="modal-header"><button type="button" class="close" data-dismiss="modal" aria-label="Close">' +
                '<span aria-hidden="true">&times;</span></button> <h4 class="modal-title" id="exampleModalLabel">'+
                textStatus + ' - ' + errorThrown +
                '</h4></div><div class="modal-body">' +
                jqXHR.responseText.replace('\n', '<br/>') +
                '</div>'
            $("#modal .modal-content").html(content);
        }
    });
}

function modal_form_init(href) {
    var form = $("#modal form");
    if (!form.attr("action")) {
        form.attr("action", href);
    }
    form.submit(function(event){
        event.preventDefault();
        modal_submit($('#modal form input[type=submit]'));
    });
}

// $(document).ready(function() {
//     $(".add-another:not(.click-binded)").click(function(event){
//         event.preventDefault();
//         var elem = $(this);
//         elem.addClass('click-binded');
//         var href = elem.attr("href");
//         if (href.indexOf('_popup=1') == -1) {
//             if (href.indexOf('?') == -1) {
//                 href += '?_popup=1';
//             } else {
//                 href  += '&_popup=1';
//             }
//             elem.attr("href", href);
//         }
//         var modal_html = '<div class="modal fade" id="modal" tabindex="-1" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true" data-update="'+ elem.prev().attr("id") +'">' +
//             '<div class="modal-dialog"> <div class="modal-content"></div></div></div>';
//         $("#modal").remove();
//         $("body").append(modal_html);
//         $("#modal .modal-content").load(href, function(){
//             modal_form_init(href);
//             $("#modal").modal('show');
//         });
//     });
//     $('.modal.reload-on-close').on('hidden.bs.modal', function () {
//         location.reload();
//     })
// });

$(document).ready(function($){
    if ($('.cep').length) {
        $('.cep').mask('00000-000');
    }
    if ($('.cpf').length) {
        $('.cpf').mask('000.000.000-00');
    }
    if ($('.date').length) {
        $('.date').mask('00/00/0000');
    }
    if ($('.datetime').length) {
        $('.datetime').mask('00/00/0000 00:00:00');
    }
    if ($('.money').length) {
        $('.money').mask("#.##0,00", {reverse: true});
    }
})
