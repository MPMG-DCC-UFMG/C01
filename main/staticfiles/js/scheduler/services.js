var services = {};

services.save_new_scheduling = function (new_scheduling_config) {
    $('#newScheduling').modal('hide');

    let parsed_data = JSON.stringify(new_scheduling_config);

    $.ajax({
        url: '/scheduler/jobs/',
        type: 'post',
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        async: false,
        data: parsed_data,
        success: function (data) {
            $('.toast').toast('show');
        },
        error: function (data) {
            alert('Houve um erro no agendamento, tente novamente!');
            console.error(data.responseText);
        }
    });
}