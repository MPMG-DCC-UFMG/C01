var el_days_of_week_repeat_option = $('#days-week-repeat-wrapper');
var el_montly_repeat_option = $('#monthly-repeat-wrapper');

var repeat_option_selected = null;

var days_selected_to_repeat = {
    0: false,
    1: false,
    2: false,
    3: false,
    4: false,
    5: false,
    6: false
};

var day_number_to_weekday = {
    0: 'domingo',
    1: 'segunda-feira',
    2: 'terça-feira',
    3: 'quarta-feira',
    4: 'quinta-feira',
    5: 'sexta-feira',
    6: 'sábado'   
}

var new_scheduling_config = {
    crawl_request: null,
    crawler_queue_behavior: 'wait_on_last_queue_position',
    scheduler_config: {
        start_date: null,
        timezone: 'America/Sao_Paulo',
        repeat_mode: 'no_repeat',
        personalized_repeat: null
    }
}

var repeat = {};

var date = new Date();

var repeat_finish_occurrences = 1;
var montly_repeat_value = date.getDate();
var montly_repeat_mode = 'day-x';
var repeat_finish_date; 

// calendar
var calendar_mode = null; //daily, weekly, monthly or yearly

var task_being_edited = null;
 
var modal_open_callback;
var excluded_tasks = [];

function open_set_scheduling(creating_task = true) {
    
    if (creating_task) {
        init_default_options();
    }

    $('#setSchedulingModal').modal({ backdrop: 'static', keyboard: false }, 'show');
}

function hide_set_scheduling() {
    $('#setSchedulingModal').modal('hide');

    if (task_being_edited)
        task_being_edited = null;
}

function open_personalized_crawler_repeat() {
    $('#setSchedulingModal').modal('hide');
    $('#personalizedCrawlerRepetion').modal({ backdrop: 'static', keyboard: false }, 'show');
}

function show_days_of_week_repeat_options() {
    el_days_of_week_repeat_option.removeClass('d-none');
    el_days_of_week_repeat_option.addClass('d-flex');
}

function hide_days_of_week_repeat_options() {
    el_days_of_week_repeat_option.removeClass('d-flex');
    el_days_of_week_repeat_option.addClass('d-none');
}

function show_monthly_repeat_options() {
    el_montly_repeat_option.removeClass('d-none');
}

function hide_monthly_repeat_options() {
    el_montly_repeat_option.addClass('d-none');
}

function toggle_weekday_select(el) {
    let weekday = parseInt(el.getAttribute('weekday'));

    days_selected_to_repeat[weekday] = !days_selected_to_repeat[weekday];

    if (days_selected_to_repeat[weekday]) {
        el.classList.remove('text-muted', 'bg-white');
        el.classList.add('text-white', 'bg-primary');
    } else {
        el.classList.remove('text-white', 'bg-primary');
        el.classList.add('text-muted', 'bg-white');
    }

    repeat.data = [];
    for (let i in days_selected_to_repeat)
        if (days_selected_to_repeat[i])
            repeat.data.push(parseInt(i));
    
    update_repeat_info();
}

function init_default_options() {
    let curr_day = date.getDate();
    let weekday = date.getDay();

    $('#crawl-selector').multiselect('select', ['no_selected']);
    $('#no-repeat-sel-opt').prop('selected', true);
    $('#wait-last-sel-opt').prop('selected', true);
    $('#scheduling-time').val('')
    
    $(`#medx-${curr_day}`).prop('selected', true);
    $(`#mfws-${weekday}`).prop('selected', true);
    $(`#mlws-${weekday}`).prop('selected', true);
    $(`#dwr-${weekday}`).click();


    $('#scheduling-personalized-repetition-info').css('display', 'none');

    let future_date = new Date()
    future_date.setFullYear(date.getFullYear() + 1);

    let day = date.getDate() < 10 ? `0${future_date.getDate()}` : future_date.getDate();
    let month = (date.getMonth() + 1) < 10 ? `0${future_date.getMonth() + 1}` : future_date.getMonth() + 1;

    let parsed_date = `${day}/${month}/${future_date.getFullYear()}`;
    
    repeat_finish_date = parsed_date;
    montly_repeat_value = curr_day;

    $('#finish-date-in').val(`${future_date.getFullYear()}-${month}-${day}`);

    new_scheduling_config = {
        crawl_request: null,
        crawler_queue_behavior: 'wait_on_last_queue_position',
        scheduler_config: {
            start_date: null,
            timezone: 'America/Sao_Paulo',
            repeat_mode: 'no_repeat',
            personalized_repeat: null
        }
    };

    repeat = {
        mode: 'daily',
        interval: 1,
        data: null,
        finish: {
            mode: 'never',
            value: null
        }
    };
}

function repeat_to_text(repeat) {
    let s = '';

    switch (repeat.mode) {
        case 'daily':
            if (repeat.interval == 1)
                s = 'Repete diariamente.'

            else
                s = `Repete a cada ${repeat.interval} dias.`

            break;

        case 'weekly':

            if (repeat.data.length > 0) {
                if (repeat.interval == 1)
                    s = 'Repete semanalmente aos/às ';

                else
                    s = `Repete a cada ${repeat.interval} semanas aos/às `

                let days = [];
                let day_number;

                for (let i = 0; i < repeat.data.length; i++) {
                    day_number = repeat.data[i];
                    days.push(day_number_to_weekday[day_number]);
                }

                if (days.length == 1)
                    s += days[0] + '.';

                else {
                    for (let i = 0; i < days.length - 1; i++)
                        s += days[i] + ', '
                    s = s.substring(0, s.length - 2) + ` e ${days[days.length - 1]}.`;

                }

            } else
                s = 'Repete semanalmente.'

            break

        case 'monthly':
            if (repeat.interval == 1)
                s = 'Repete mensalmente ';

            else
                s = `Repete a cada ${repeat.interval} meses `

            switch (repeat.data.mode) {
                case 'day-x':
                    s += `no dia ${repeat.data.value}.`;
                    break;

                case 'first-weekday':

                    s += `no/na primeiro(a) ${day_number_to_weekday[repeat.data.value]}.`
                    break

                case 'last-weekday':
                    s += `no/na último(a) ${day_number_to_weekday[repeat.data.value]}.`
                    break;

                default:
                    break;
            }

            break

        case 'yearly':
            if (repeat.interval == 1)
                s = 'Repete anualmente.'

            else
                s = `Repete a cada ${repeat.interval} anos.`

            break
    }

    switch (repeat.finish.mode) {
        case 'occurrence':
            s += ` Ocorre ${repeat.finish.value} vezes.`
            break;

        case 'date':
            s += ` Ocorre até ${repeat.finish.value}.`
            break;

        default:
            break;
    }

    return s;    
}

function update_repeat_info() {
    if (task_being_edited) {
        scheduling_task = task_being_edited;
        raw_repeat = scheduling_task.scheduler_config.personalized_repeat;
    } else {
        scheduling_task = new_scheduling_config;
        raw_repeat = repeat; 
    }
    
    if (scheduling_task.scheduler_config.repeat_mode != 'personalized') 
        return;

    let parsed_repeat = repeat_to_text(raw_repeat);
    $('#repetition-info').text(parsed_repeat);

    let personalized_repeat_info = $('#scheduling-personalized-repetition-info');
    personalized_repeat_info.css('display', 'inline-block');
    personalized_repeat_info.text(parsed_repeat);

    scheduling_task.scheduler_config.personalized_repeat = repeat;
}

function close_personalized_repeat_modal() {
    $('#personalizedCrawlerRepetion').modal('hide');
    $('#setSchedulingModal').modal({ backdrop: 'static', keyboard: false }, 'show');
}

function update_calendar_mode(mode) {
    if (mode == calendar_mode)
        return;

    switch (calendar_mode) {
        case 'daily':
            calendar.daily.hide();
            break;

        case 'weekly':
            calendar.weekly.hide();
            break;

        case 'monthly':
            calendar.monthly.hide();
            break;

        case 'yearly':
            calendar.yearly.hide();
            break;

        default:
            break;
    }

    switch (mode) {
        case 'daily':
            calendar.daily.show();
            break;

        case 'weekly':
            calendar.weekly.show();
            break;

        case 'monthly':
            calendar.monthly.show();
            break;

        case 'yearly':
            calendar.yearly.show();
            break;

        default:
            break;
    }

    calendar_mode = mode;
}

function sleep(ms) {
    var now = new Date().getTime();
    while (new Date().getTime() < now + ms) { /* Do nothing */ }
}

function valid_new_scheduling() {
    if (task_being_edited)
        scheduling_task = task_being_edited;

    else
        scheduling_task = new_scheduling_config; 

    if (scheduling_task.crawl_request == null) {
        alert('Escolha um coletor válido!');
        return;
    }

    if (scheduling_task.scheduler_config.start_date == null) {
        alert('Escolha um horário válido!');
        return;
    }

    if (scheduling_task.scheduler_config.repeat_mode == 'personalized' 
        && scheduling_task.scheduler_config.personalized_repeat.mode == 'weekly'
        && scheduling_task.scheduler_config.personalized_repeat.data.length == 0) {
        alert('Você configurou uma coleta personalizada semanal, porém não escolheu o(s) dia(s) que ela deve ocorrer!');
        return;
    }

    let now = new Date();
    let start_date = new Date(scheduling_task.scheduler_config.start_date);

    if (start_date < now) {
        alert('O horário de início da coleta deve ser maior que o horário atual!');
        return;
    }

    
    if (task_being_edited) {
        services.save_updated_scheduling(task_being_edited);
        task_being_edited = null;
    }
    
    else
        services.save_new_scheduling(scheduling_task);
    
    hide_set_scheduling();
    
    let year_month_day = scheduling_task.scheduler_config.start_date.split('T')[0].split('-')
    calendar.daily.active_day = new Date(parseInt(year_month_day[0]), parseInt(year_month_day[1]) - 1, parseInt(year_month_day[2])); 

    calendar.daily.show();
}

function str_to_date(runtime) {
    // runtime follows the format <year>-<month>-<day>T<hour>:<minute>:<seconds>Z'
    let splited_runtime = runtime.split('T');
    
    let runtime_date = splited_runtime[0].split('-');
    let runtime_time = splited_runtime[1].split(':');

    return new Date(parseInt(runtime_date[0]), 
                    parseInt(runtime_date[1]) - 1, 
                    parseInt(runtime_date[2]),
                    parseInt(runtime_time[0]),
                    parseInt(runtime_time[1]));

}

function get_now(timezone) {
    let now = new Date().toLocaleString({ timeZone: timezone }) ;
    return new Date(now);
}

function show_task_detail(task_id, modal_open_callback_funct = null) {

    if (modal_open_callback_funct != null) {
        close_all_scheduling_modal();
        close_show_more_schedulings_modal();
    }
    
    modal_open_callback = modal_open_callback_funct;

    let task = TASKS[task_id];

    let now = get_now(task.scheduler_config.timezone);

    let start_date = str_to_date(task.scheduler_config.start_date);

    let next_run_text = '';
    let repeat_info = '';
    
    let since = now > start_date ? 'Desde de ' : 'A partir de ';
    since += `${start_date.getDate()} de ${MONTHS[start_date.getMonth()]} de ${start_date.getFullYear()}.`;

    switch (task.scheduler_config.repeat_mode) {
        case 'no_repeat':
            repeat_info = 'Não se repete.';    
            break;
        
        case 'daily':
            repeat_info = `Repete diariamente às ${start_date.getHours()}h${String(start_date.getMinutes()).padStart(2, '0') }.`;
            break;

        case 'weekly':
            let weedays = ['domingo', 'segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira', 'sábado'];
            repeat_info = `Repete toda(o) ${weedays[start_date.getDay()]} às ${start_date.getHours()}h${String(start_date.getMinutes()).padStart(2, '0') }.`;
            break;
        
        case 'monthly':
            repeat_info = `Repete todo dia ${start_date.getDate()} do mês às ${start_date.getHours()}h${String(start_date.getMinutes()).padStart(2, '0') }.`;
            break;
        
        case 'yearly':
            repeat_info = `Repete todo dia ${start_date.getDate()} de ${MONTHS[start_date.getMonth()]} do ano às ${start_date.getHours()}h${String(start_date.getMinutes()).padStart(2, '0') }.`;
            break;
        
        case 'personalized':
            repeat_info = repeat_to_text(task.scheduler_config.personalized_repeat);
            break;

        default:
            break;
    };

    // O único caso em que o next_run não é definido é quando a coleta é agendada para ser executada uma única vez e o horário de início já passou.
    if (task.next_run == null) 
        task.next_run = task.scheduler_config.start_date;

    let next_run_date = str_to_date(task.next_run);
    next_run_text = new Intl.DateTimeFormat('pt-BR', {
        dateStyle: 'full',
        timeStyle: 'long',
        timeZone: task.scheduler_config.timezone
    }).format(next_run_date);

    // the first letter must be capitalized
    next_run_text = next_run_text[0].toUpperCase() + next_run_text.slice(1);

    if (next_run_date.getDate() == now.getDate() && next_run_date.getMonth() == now.getMonth() && next_run_date.getFullYear() == now.getFullYear()) 
        next_run_text = next_run_text.replace(/^[^,]*/, 'Hoje');

    let next_run_html = '';

    // if next_run is in the past, it means that the task is running right now
    if (next_run_date < now) 
        next_run_html = `<div class="text-danger"
                            title="A coleta já foi executada em: ${next_run_text}">
                            <i class="fa fa-calendar-alt mr-2" aria-hidden="true"></i>
                            <small
                                style="text-decoration: line-through;" 
                                class="font-weight-bold">${next_run_text}
                            </small> 
                        </div>`
    
    else 
        next_run_html = `<div title="Aguardando execução em: ${next_run_text}">
                            <i class="fa fa-calendar-alt mr-2" aria-hidden="true"></i>   
                            <small class="font-weight-bold">${next_run_text}</small>
                        </div>`
        
    let bg_crawler_queue_info = '';
    let crawler_queue_info = '';

    switch (task.crawler_queue_behavior) {
        case 'run_immediately':
            bg_crawler_queue_info = 'bg-danger';
            crawler_queue_info = 'Executa imediatamente.';
            break;

        case 'wait_on_first_queue_position':
            bg_crawler_queue_info = 'bg-warning';
            crawler_queue_info = 'Aguarda na primeira posição da fila de coletas.';
            break;
    
        case 'wait_on_last_queue_position':
            bg_crawler_queue_info = 'bg-info';
            crawler_queue_info = 'Aguarda na última posição da fila de coletas.';
            break;

        default:
            break;
    };

    let task_detail_html = `
                <h3 class="h5 font-weight-bold">${task.crawler_name}</h3>
                
                <div class="bg-light rounded p-3 border mt-3">
                    ${next_run_html} 

                    <div class="my-2">
                        <i class="fa fa-redo mr-1 text-muted fa-sm" aria-hidden="true"></i>
                        <small class="text-muted">${repeat_info}</small>
                    </div>

                    <div class="">
                        <i class="fa fa-clock mr-1 text-muted fa-sm" aria-hidden="true"></i>
                        <small class="text-muted">${since}</small> 
                    </div>
                </div>

                <br>
                <p class="m-0 ${bg_crawler_queue_info} border rounded-pill small text-white font-weight-bold px-2" style="display: inline-block;">${crawler_queue_info}</p>
                <div class="d-flex justify-content-center mt-4 text-muted">
                    <a href="/detail/${task.crawl_request}/" 
                        target="_blank"
                        title="Visualizar coletor." class="rounded-circle bg-white border d-flex align-items-center justify-content-center scheduling-detail-options" 
                        rel="noopener noreferrer"
                        >
                        <i class="far fa-eye text-muted"></i>
                    </a>
                    <button 
                        onclick="edit_scheduling_task(${task.id})"
                        class="rounded-circle bg-white border mx-3 scheduling-detail-options">
                        <i class="fas fa-pen text-muted"></i>
                    </button>
                    <button  
                        onclick="delete_schedule_task(${task.id})"
                        class="rounded-circle border bg-white scheduling-detail-options">
                        <i class="far fa-trash-alt text-muted"></i>
                    </button>
                </div>
    `;

    $('#detailSchedulingContent').html(task_detail_html);

    $('#detailScheduling').modal({ backdrop: 'static', keyboard: false }, 'show');

}

function edit_scheduling_task(task_id) {
    $('#detailScheduling').modal('hide');

    let task = TASKS[task_id];
    if (!task) {
        console.error('Invalid task id!');
        return;
    }

    let personalized_repeat = task.scheduler_config.personalized_repeat;
    if (!personalized_repeat) {
        personalized_repeat = {
            mode: 'daily',
            interval: 1,
            data: null,
            finish: {
                mode: 'never',
                value: null
            }
        };
    }

    task_being_edited = {
        id: task.id,
        crawler_queue_behavior: task.crawler_queue_behavior,
        crawl_request: task.crawl_request,
        scheduler_config: {
            start_date: task.scheduler_config.start_date,
            timezone: task.scheduler_config.timezone,
            repeat_mode: task.scheduler_config.repeat_mode,
            personalized_repeat: personalized_repeat
        }
    };

    fill_set_scheduling(task_id);
    open_set_scheduling(false);    
}

function delete_schedule_task(task_id) {    
    close_detail_scheduling_modal()
    
    let scheduling_name = TASKS[task_id].crawler_name;
    let delete_confirmed = confirm(`Tem certeza que deseja excluir a coleta agendada "${scheduling_name}"?`);
    
    if (!delete_confirmed)
        return;
    
    delete TASKS[task_id];

    fill_task_list();

    services.delete_task(task_id);
}

function fill_set_scheduling(task_id) {
    let task = TASKS[task_id];

    if (!task)
        return;

    let start_date = task.scheduler_config.start_date.substr(0, 16);

    $(`#crawl-selector option[value='${task.crawl_request}']`).attr('selected', 'selected');
    $('#scheduling-time').val(start_date);
    $(`#repeat-crawling-select option[value='${task.scheduler_config.repeat_mode}']`).attr('selected', 'selected');
    $(`#crawler_queue_behavior option[value='${task.crawler_queue_behavior}']`).attr('selected', 'selected');
    
    if (task.scheduler_config.repeat_mode == 'personalized') {
        $('#scheduling-personalized-repetition-info').html(repeat_to_text(task.scheduler_config.personalized_repeat));
        $('#scheduling-personalized-repetition-info').css('display', 'block');
    } else
        $('#scheduling-personalized-repetition-info').css('display', 'none');

    $(`#crawl-selector`).multiselect('rebuild');
}

function attach_event_listeners() {
    $('#crawl-selector').multiselect({
        includeSelectAllOption: true,
        enableFiltering: true,
        selectAllText: 'Selecionar todas',
        nonSelectedText: 'Nada selecionado',
        filterPlaceholder: 'Procurar',
        buttonClass: 'btn btn-outline-secondary',
        buttonWidth: '100%',
        maxHeight: 380,
        maxWidth: 240,
        enableCaseInsensitiveFiltering: true,
    });

    // quando o usuário está digitando em search-task, filtra a lista de tarefas e atualiza a lista
    $('#search-task').on('keyup', function () {
        let search = $(this).val().toLowerCase();

        let task_list = $('#task-list');

        let task_items = [];

        // itera por cada objeto no objeto TASKS
        for (let task_id in TASKS) {
            let task = TASKS[task_id];

            // se o nome do crawler contém a string de busca, adiciona o item na lista
            if (task.crawler_name.toLowerCase().includes(search))
                task_items.push(create_task_item(task));
        }


        if (task_items.length == 0)
            task_items.push(`<li class="p-3">
                                <div class="d-flex justify-content-center"
                                    style="flex-direction: column;">
                                    <span style="font-size: 1.5rem;">¯\\_(ツ)_/¯</span>
                                    <p class="m-0 p-0 mt-3">Nenhum agendamento encontrado!</p>
                                </div>
                            </li>`);

        task_list.html(task_items.join(''));
    });

    $('#repeat-crawling-select').on('click', function () {
        let repeat_mode = $(this).val();

        if (task_being_edited)
            scheduling_task = task_being_edited;

        else
            scheduling_task = new_scheduling_config;

        scheduling_task.scheduler_config.repeat_mode = repeat_mode;

        if (repeat_mode == 'personalized') {
            update_repeat_info();
            open_personalized_crawler_repeat();
        } else {
            scheduling_task.scheduler_config.personalized_repeat = null;
            $('#scheduling-personalized-repetition-info').css('display', 'none');
        }

    });

    $('#repeat-mode-selector').change(function () {
        let repeat_mode = $(this).val();

        if (repeat_option_selected == repeat_mode)
            return;

        switch (repeat_option_selected) {
            case 'weekly':
                hide_days_of_week_repeat_options();
                break;

            case 'monthly':
                hide_monthly_repeat_options();
                break;
        }

        switch (repeat_mode) {
            case 'weekly':
                repeat.data = [];
                for (let i in days_selected_to_repeat)
                    if (days_selected_to_repeat[i])
                        repeat.data.push(parseInt(i));

                if (repeat.data.length == 0)
                    $(`#dwr-${date.getDay()}`).click();

                show_days_of_week_repeat_options();
                break;

            case 'monthly':
                show_monthly_repeat_options();
                repeat.data = { mode: montly_repeat_mode, value: montly_repeat_value };
                break;

            default:
                repeat.data = null;
                break;
        }

        repeat_option_selected = repeat_mode;
        repeat.mode = repeat_mode;

        update_repeat_info();
    });

    $('#interval-in').change(function () {
        repeat.interval = parseInt($(this).val());
        update_repeat_info();
    });

    $("input[name=finish-type]").change(function () {
        let input = $(this);

        let finish_mode = input.attr('finish_type');

        repeat.finish.mode = finish_mode;
        switch (finish_mode) {
            case 'never':
                repeat.finish.value = null;
                break;

            case 'occurrence':
                repeat.finish.value = repeat_finish_occurrences;
                break;

            case 'date':
                repeat.finish.value = repeat_finish_date;
                break;

            default:
                break;
        }

        update_repeat_info();
    });

    $('#finish-occurrence-in').on('click', function () {
        repeat_finish_occurrences = parseInt($(this).val());
        $('#finish-ocurrence').click();
        repeat.finish.value = repeat_finish_occurrences;
        update_repeat_info();
    });

    $('#finish-date-in').change(function () {
        repeat_finish_date = $(this).val();
        $('#finish-date').click();
        repeat.finish.value = repeat_finish_date;
        update_repeat_info();
    });

    $('input[name=montly-repeat]').change(function () {
        let input = $(this);

        montly_repeat_mode = input.attr('montly_repeat');
        montly_repeat_value = parseInt($(`#montly-${montly_repeat_mode}-sel`).find(":selected").val());

        repeat.data.mode = montly_repeat_mode;
        repeat.data.value = montly_repeat_value;
        update_repeat_info();
    });

    $('#montly-day-x-sel').on('change', function () {
        montly_repeat_value = parseInt($(this).find(":selected").val());
        montly_repeat_mode = 'day-x';

        $('#montly-every-day-x').click();

        repeat.data.mode = montly_repeat_mode;
        repeat.data.value = montly_repeat_value;
        update_repeat_info();
    });

    $('#montly-first-weekday-sel').on('change', function () {
        montly_repeat_value = parseInt($(this).find(":selected").val());
        montly_repeat_mode = 'first-weekday';

        $('#montly-first-weekday').click();

        repeat.data.mode = montly_repeat_mode;
        repeat.data.value = montly_repeat_value;
        update_repeat_info();
    });

    $('#montly-last-weekday-sel').on('change', function () {
        montly_repeat_value = parseInt($(this).find(":selected").val());
        montly_repeat_mode = 'last-weekday';

        $('#montly-last-weekday').click();

        repeat.data.mode = montly_repeat_mode;
        repeat.data.value = montly_repeat_value;
        update_repeat_info();
    });

    $('#previous').on('click', function () {
        switch (calendar_mode) {
            case 'daily':
                calendar.daily.previous();
                break;

            case 'weekly':
                calendar.weekly.previous();
                break;

            case 'monthly':
                calendar.monthly.previous();
                break;

            case 'yearly':
                calendar.yearly.previous();
                break;

            default:
                break;
        }
    });

    $('#next').on('click', function () {
        switch (calendar_mode) {
            case 'daily':
                calendar.daily.next();
                break;

            case 'weekly':
                calendar.weekly.next();
                break;

            case 'monthly':
                calendar.monthly.next();
                break;

            case 'yearly':
                calendar.yearly.next();
                break;

            default:
                break;
        }
    });

    $('#today').on('click', function () {

        switch (calendar_mode) {
            case 'daily':
                calendar.daily.today();
                break;

            case 'weekly':
                calendar.weekly.today();
                break;

            case 'monthly':
                calendar.monthly.today();
                break;

            case 'yearly':
                calendar.yearly.today();
                break;

            default:
                break;
        }
    });

    $('#calendar-mode').on('change', function () {
        update_calendar_mode($(this).val());
    });

    $('#crawler_queue_behavior').on('change', function () {
        if (task_being_edited)
            scheduling_task = task_being_edited;

        else
            scheduling_task = new_scheduling_config;

        scheduling_task.crawler_queue_behavior = $(this).val();
    });

    $('#scheduling-time').on('change', function () {
        if (task_being_edited)
            scheduling_task = task_being_edited;

        else
            scheduling_task = new_scheduling_config;

        scheduling_task.scheduler_config.start_date = $(this).val();
    });

    $('#crawl-selector').on('change', function () {
        if (task_being_edited)
            scheduling_task = task_being_edited;

        else
            scheduling_task = new_scheduling_config;

        scheduling_task.crawl_request = parseInt($(this).val());
    });

    $('#scheduling-timezone').on('change', function () {
        if (task_being_edited)
            scheduling_task = task_being_edited;

        else
            scheduling_task = new_scheduling_config;

        scheduling_task.scheduler_config.timezone = $(this).val();
    });    
}

function create_task_item(task) {
    return `<li class="rounded border p-3 mb-2">
                <div class="d-flex justify-content-between align-items-center">
                    <div class="">
                        <p class="font-weight-bold m-0 p-0">${task.crawler_name}</p>
                    </div>
                </div>
                <div class="mt-2 d-flex justify-content-between">
                    <div class="next-runtime d-flex align-items-center"
                        title="Horário da próxima execução"
                        style="cursor: pointer;">
                        <i class="fa fa-calendar-alt mr-2 text-muted" aria-hidden="true"></i>
                        <small class="">Seg., 23 de Jun., às 17h24</small>
                    </div>
                    <div class="d-flex">
                        <!-- botão com icone de editar -->
                        <button 
                            title="Visualizar agendamento"
                            style="width: 1.75rem; height: 1.75rem;"
                            class="scheduling-item text-muted rounded-circle bg-white border-0 d-flex align-items-center justify-content-center mr-2"
                            onclick="show_task_detail(${task.id}, show_all_scheduling_modal)">
                            
                            <i class="far fa-eye" aria-hidden="true"></i>
                        </button>
                        <button 
                            onclick="delete_schedule_task(${task.id})"
                            title="Remover agendamento"
                            style="width: 1.75rem; height: 1.75rem;"
                            class="scheduling-item rounded-circle border-0 bg-white text-muted">
                            <i class="far fa-trash-alt" aria-hidden="true"></i>
                        </button>
                    </div>
                </div>
            </li>`
}

function fill_task_list() {
    let task_list = $('#task-list');

    let task_items = [];
    for (let task_id in TASKS) 
        task_items.push(create_task_item(TASKS[task_id]));
    
    task_list.html(task_items.join(''));
}

function show_all_scheduling_modal() {
    $('#allScheduling').modal({ backdrop: 'static', keyboard: false }, 'show');
}

function close_all_scheduling_modal() {
    $('#allScheduling').modal('hide');
}

function close_detail_scheduling_modal() {
    $('#detailScheduling').modal('hide');

    if (modal_open_callback) {
        modal_open_callback();
        modal_open_callback = null;
    }
}

function open_show_more_schedulings_modal() {
    $('#showMoreSchedulings').modal({ backdrop: 'static', keyboard: false }, 'show');
}

function close_show_more_schedulings_modal() {
    $('#showMoreSchedulings').modal('hide');
}

function get_more_scheduling_li_html(task, curr_day) {
    let bg_color = '';

    if (task.crawler_queue_behavior == 'run_immediately')
        bg_color = 'bg-danger';
    
    else if (task.crawler_queue_behavior == 'wait_on_last_queue_position')
        bg_color = 'bg-primary';
    
    else
        bg_color = 'bg-warning';

    let [title, opacity] = get_task_title_and_opacity(task, curr_day);

    return `
        <li class="rounded border p-3 mb-2 text-white ${bg_color}"
            id="more-showing-task-${task.id}"
            onclick="show_task_detail(${task.id}, open_show_more_schedulings_modal)"
            title="${title}"
            style="cursor: pointer; ${opacity}">
            <div class="d-flex justify-content-between align-items-center"> 
                <div class="">
                    <p class="font-weight-bold m-0 p-0 small">${task.crawler_name}</p>
                </div>
            </div>
        </li>
    `;
}

function show_more_schedulings(tasks_not_shown, date, from_hour, to_hour=null) {
    let splited_day = date.split('-');

    let curr_day = new Date(parseInt(splited_day[2]),
        parseInt(splited_day[1]) - 1,
        parseInt(splited_day[0]));

    // formatar data para o formato dia da semana, dia/mês/anos, a partir das horas e minutos
    let formatted_date = curr_day.toLocaleDateString('pt-BR', {
        weekday: 'long',
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    });

    if (to_hour == null)
        to_hour = parseInt(from_hour) + 1;

    if (to_hour >= 24)
        to_hour = 0;
    
    if (from_hour != to_hour)
        formatted_date += `, ${from_hour}h - ${to_hour}h`;

    // first letter uppercase
    formatted_date = formatted_date.charAt(0).toUpperCase() + formatted_date.slice(1);

    $('#showMoreSchedulings .modal-title').html(formatted_date);

    let task_list = $('#showMoreSchedulings .modal-body ul');

    if (tasks_not_shown.length == 0) {

        task_list.html(`<li class="p-3">
                            <div class="d-flex justify-content-center"
                                style="flex-direction: column;">
                                <span style="font-size: 1.5rem;">¯\\_(ツ)_/¯</span>
                                <p class="m-0 p-0 mt-3">Sem agendamentos para a data informada!</p>
                            </div>
                        </li>`);

        open_show_more_schedulings_modal();

        return;
    }

    let task_items = [], task;
    for (let i in tasks_not_shown) {
        task_id = tasks_not_shown[i];
        
        // ckeck if task is in excluded tasks
        if (excluded_tasks.includes(task_id))
            continue;

        task = TASKS[task_id];
        task_items.push(get_more_scheduling_li_html(task, curr_day));
    }

    task_list.html(task_items.join(''));

    open_show_more_schedulings_modal();
}

function update_view() {
    switch (calendar_mode) {
        case 'daily':
            calendar.daily.show();
            break;

        case 'weekly':
            calendar.weekly.show();
            break;

        case 'monthly':
            calendar.monthly.show();
            break;

        case 'yearly':
            calendar.yearly.show();
            break;

        default:
            break;
    }
}

$(document).ready(function () {
    // transforma a lista de tarefas em um objeto onde o campo id é a chave
    TASKS = TASKS.reduce((obj, item) => {
        obj[item.id] = item;
        return obj;
    }, {});

    attach_event_listeners();
    fill_task_list();
    init_default_options();
    update_calendar_mode('daily');
});
