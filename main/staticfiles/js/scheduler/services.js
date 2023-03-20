var services = {};

services.sleep = function (ms) {
    var now = new Date().getTime();
    while (new Date().getTime() < now + ms) { /* Do nothing */ }
}

services.save_new_scheduling = function (new_scheduling_config) {
    let parsed_data = JSON.stringify(new_scheduling_config);

    $.ajax({
        url: '/api/scheduler/tasks/',
        type: 'post',
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        async: false,
        data: parsed_data,
        success: function (data) {
            $('#toast-success-text').text('Agendamento realizado com sucesso!');
            $('#toast').toast('show');
            
            TASKS[data.id] = data;
            
            fill_task_list();
            update_view();

        },
        error: function (data) {
            alert('Houve um erro no agendamento, tente novamente!');
            console.error(data.responseText);
        }
    });
}

services.get_tasks_in_interval = function (start_date, end_date) {
    $.ajax({
        url: `/api/scheduler/tasks/filter?start_date=${start_date}&end_date=${end_date}`,
        type: 'get',
        async: false,
        success: function (data) {
            tasks_by_date = data;
            console.log('Tasks received!', tasks_by_date);
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
        url: `/api/scheduler/tasks/${task_id}`,
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

services.delete_task = function(task_id) {
    excluded_tasks.push(task_id);

    // Remove task from view
    $(`#more-showing-task-${task_id}`).remove();

    $.ajax({
        url: `/api/scheduler/tasks/${task_id}`,
        type: 'delete',
        async: false,
        success: function (data) {
            update_view();
        },
        error: function (data) {
            console.error(data.responseText);
        }
    });   
}

services.save_updated_scheduling = function (task_being_edited) {

    let task_id = task_being_edited.id;
    let parsed_data = JSON.stringify(task_being_edited);

    $.ajax({
        url: `/api/scheduler/tasks/${task_id}/`,
        type: 'put',
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        async: false,
        data: parsed_data,
        success: function (data) {
            $('#toast-success-text').text('Agendamento alterado com sucesso!');
            $('#toast').toast('show');

            TASKS[task_id] = data;
            update_view();
        },
        error: function (data) {
            console.error(data.responseText);
        }
    });
}