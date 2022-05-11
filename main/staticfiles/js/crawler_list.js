$(function(){
    // limpa os campos do formulário
    $('.clear-form').on('click', function(e){
        var form_obj = $(this).parents('form');
        form_obj.find("select").find('option:selected').removeAttr('selected');
        form_obj.find("select").val("");
        form_obj.find("input[type=text]").val("");
        form_obj.find("input[type=date]").val("");
        return true;
    });

});