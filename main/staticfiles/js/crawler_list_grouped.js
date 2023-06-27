$(function(){
    // limpa os campos do formulário ao clicar no botão "limpar"
    $(".clear-form").on("click", function(e){
        var $form_obj = $(this).parents("form");
        $form_obj.find("select").find("option:selected").removeAttr("selected");
        $form_obj.find("select").val("");
        $form_obj.find("input[type=text]").val("");
        $form_obj.find("input[type=date]").val("");
        return true;
    });

    // callback quando o conteúdo é exibido
    // faz um ajax pra buscar o conteúdo de um grupo de coletores
    $("#crawlers-grouped-accordion").on("show.bs.collapse", function (e) {
        let crawler_id = $(e.target).data("crawler-id");
        let $group_content = $($(e.target).find(".group-content"));
        let $loading = $($(e.target).find(".loading"));
        let $content_template = $($("#group-content-template").html());
        
        let url = `${window.location.origin}/api/crawler/${crawler_id}/group`;
        console.log('>>', url);

        let ajax_request = $.ajax(url);

        ajax_request.done(function (json_response){
            let table = $content_template.clone();
            $group_content.html(table);
            for (let i = 0; i < json_response.length; i++) {
                const item = json_response[i];
                table.append("<tr><td>"+item.source_name+"</td><td>"+item.id+"</td><td>"+item.base_url+"</td></tr>");
            }
            $group_content.removeClass("d-none");
            $loading.addClass("d-none");
        });
    });

    // callback pra esconder o conteúdo
    // limpa o conteúdo
    $('#crawlers-grouped-accordion').on("hide.bs.collapse", function (e) {
        let $group_content = $($(e.target).find(".group-content"));
        let $loading = $($(e.target).find(".loading"));
        $loading.removeClass("d-none");
        $group_content.html("");
        $group_content.addClass("d-none");
    });
});