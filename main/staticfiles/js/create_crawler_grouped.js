$(function(){

    // habilita ou desabilita toda lista de crawlers
    $('#check_all_crawlers').change(function() {
        
        if (this.checked) {
            // $("input[name=crawler_id]").prop("checked", true);
            $("input[name=crawler_id]").each(function(index){
                let $checkbox = $(this);
                // navega até a linha pai e a partir dali desabilita os inputs
                $checkbox.parents(".row:eq(0)").find("input[type=text]").prop("disabled", false);
                $checkbox.prop("checked", true);
            });
        } else {
            // $("input[name=crawler_id]").prop("checked", false);
            $("input[name=crawler_id]").each(function(index){
                let $checkbox = $(this);
                // navega até a linha pai e a partir dali desabilita os inputs
                $checkbox.parents(".row:eq(0)").find("input[type=text]").prop("disabled", true);
                $checkbox.prop("checked", false);
            });
        }
    });

    // habilita ou desabilita um crawler específico ao clicar no checkbox
    $(".grouped_crawlers_container").on("change", "input[name=crawler_id]", function(){
        let $checkbox = $(this);
        if(this.checked){
            $checkbox.parents(".row:eq(0)").find("input[type=text]").prop("disabled", false);
        } else {
            $checkbox.parents(".row:eq(0)").find("input[type=text]").prop("disabled", true);
        }
    });

    // adiciona uma linha com novo crawler
    $("#btn-add-crawler").click(function(){
        let $template = $($("#crawler-line-template").html());
        $template.find("input").each(function(i){
            $(this).attr("name", $(this).attr("name").replace("template-", ""));
        });
        let $container = $(".grouped_crawlers_container");
        $container.append($template);
        $container.animate({ scrollTop: $container.prop("scrollHeight")}, 1000);
        checkBasicInfo();
    });

    // remove uma linha com novo crawler
    $(".grouped_crawlers_container").on("click", ".btn-remove-crawler", function(){
        $(this).parents(".row:eq(0)").remove();
        checkBasicInfo();
    });
});

