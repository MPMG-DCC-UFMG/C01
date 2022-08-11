var services = {};

services.save_new_scheduling = function (new_scheduling_config) {
    $('#newScheduling').modal('hide');

    let parsed_data = JSON.stringify(new_scheduling_config);

    $.ajax({
        url: '/api/tasks/',
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

services.get_tasks_in_interval = function (start_date, end_date) {
    $.ajax({
        url: `/api/tasks/filter?start_date=${start_date}&end_date=${end_date}`,
        type: 'get',
        async: false,
        success: function (data) {
            tasks_by_date = data;
            
        },
        error: function (data) {
            console.error(data.responseText);
        }
    });

    return tasks_by_date;
}

services.get_task = function (task_id) {
    let task;
    $.ajax({
        url: `/api/tasks/${task_id}`,
        type: 'get',
        async: false,
        success: function (data) {
            task = data;
        },
        error: function (data) {
            console.error(data.responseText);
        }
    });

    return task;
}

services.update_tasks = function (tarks_ids) {

    tasks = {};
    let task_id;
    for (let i=0;i<tarks_ids.length;i++) {
        task_id = tarks_ids[i];
        tasks[task_id] = this.get_task(task_id);
    }
}