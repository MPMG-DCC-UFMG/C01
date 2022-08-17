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
    runtime: null,
    crawler_queue_behavior: 'wait_on_last_queue_position',
    repeat_mode: 'no_repeat',
    personalized_repetition_mode: null
}

var repetion = {};

var date = new Date();

var repeat_finish_occurrences = 1;
var montly_repeat_value = date.getDate();
var montly_repeat_type = 'day-x';
var repeat_finish_date; 

// calendar
var calendar_mode = null; //daily, weekly, monthly or yearly

var tasks;
var task_being_edited = null;

function open_set_scheduling(creating_task = true) {
    
    if (creating_task) {
        init_default_options();
    }

    $('#setSchedulingModal').modal('show');
}

function hide_set_scheduling() {
    $('#setSchedulingModal').modal('hide');

    if (task_being_edited)
        task_being_edited = null;
}

function open_personalized_crawler_repetition() {
    $('#setSchedulingModal').modal('hide');
    $('#personalizedCrawlerRepetion').modal('show');
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

    repetion.additional_data = [];
    for (let i in days_selected_to_repeat)
        if (days_selected_to_repeat[i])
            repetion.additional_data.push(parseInt(i));
    
    update_repetition_info();
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

    $('#finish-date-in').val(parsed_date);

    new_scheduling_config = {
        crawl_request: null,
        runtime: null,
        crawler_queue_behavior: 'wait_on_last_queue_position',
        repeat_mode: 'no_repeat',
        personalized_repetition_mode: null
    };

    repetion = {
        type: 'daily',
        interval: 1,
        additional_data: null,
        finish: {
            type: 'never',
            additional_data: null
        }
    };
}

function repetition_to_text(repetition) {
    let s = '';

    switch (repetition.type) {
        case 'daily':
            if (repetition.interval == 1)
                s = 'Repete diariamente.'

            else
                s = `Repete a cada ${repetition.interval} dias.`

            break;

        case 'weekly':

            if (repetition.additional_data.length > 0) {
                if (repetition.interval == 1)
                    s = 'Repete semanalmente aos/às ';

                else
                    s = `Repete a cada ${repetition.interval} semanas aos/às `

                let days = [];
                let day_number;

                for (let i = 0; i < repetition.additional_data.length; i++) {
                    day_number = repetition.additional_data[i];
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
            if (repetition.interval == 1)
                s = 'Repete mensalmente ';

            else
                s = `Repete a cada ${repetition.interval} meses `

            switch (repetition.additional_data.type) {
                case 'day-x':
                    s += `no dia ${repetition.additional_data.value}.`;
                    break;

                case 'first-weekday':

                    s += `no/na primeiro(a) ${day_number_to_weekday[repetition.additional_data.value]}.`
                    break

                case 'last-weekday':
                    s += `no/na último(a) ${day_number_to_weekday[repetition.additional_data.value]}.`
                    break;

                default:
                    break;
            }

            break

        case 'yearly':
            if (repetition.interval == 1)
                s = 'Repete anualmente.'

            else
                s = `Repete a cada ${repetition.interval} anos.`

            break
    }

    switch (repetition.finish.type) {
        case 'occurrence':
            s += ` Ocorre ${repetition.finish.additional_data} vezes.`
            break;

        case 'date':
            s += ` Ocorre até ${repetition.finish.additional_data}.`
            break;

        default:
            break;
    }

    return s;    
}

function update_repetition_info() {
    if (task_being_edited) {
        scheduling_task = task_being_edited;
        raw_repetition = scheduling_task.personalized_repetition_mode;
    } else {
        scheduling_task = new_scheduling_config;
        raw_repetition = repetion; 
    }
    
    if (scheduling_task.repeat_mode != 'personalized') 
        return;

    let parsed_repetition = repetition_to_text(raw_repetition);
    $('#repetition-info').text(parsed_repetition);

    let personalized_repetition_info = $('#scheduling-personalized-repetition-info');
    personalized_repetition_info.css('display', 'inline-block');
    personalized_repetition_info.text(parsed_repetition);

    scheduling_task.personalized_repetition_mode = repetion;
}

function close_personalized_repetition_modal() {
    $('#personalizedCrawlerRepetion').modal('hide');
    $('#setSchedulingModal').modal('show');
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

    if (scheduling_task.runtime == null) {
        alert('Escolha um horário válido!');
        return;
    }

    if (scheduling_task.repeat_mode == 'personalized' 
        && scheduling_task.personalized_repetition_mode.type == 'weekly'
        && scheduling_task.personalized_repetition_mode.additional_data.length == 0) {
        alert('Você configurou uma coleta personalizada semanal, porém não escolheu o(s) dia(s) que ela deve ocorrer!');
        return;
    }

    
    if (task_being_edited) {
        services.save_updated_scheduling(task_being_edited);
        task_being_edited = null;
    }
    
    else
    services.save_new_scheduling(scheduling_task);
    
    hide_set_scheduling();
    
    let year_month_day = scheduling_task.runtime.split('T')[0].split('-')
    calendar.daily.active_day = new Date(parseInt(year_month_day[0]), parseInt(year_month_day[1]) - 1, parseInt(year_month_day[2])); 

    calendar.daily.show();
}


function task_runtime_to_date(runtime) {
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

function show_task_detail(task_id) {
    let task = tasks[task_id];

    let cur_date = new Date()
 
    let runtime = task_runtime_to_date(task.runtime);

    let repetition_info = '';
    
    
    let since = cur_date > runtime ? 'Desde de ' : 'A partir de ';
    since += `${runtime.getDate()} de ${MONTHS[runtime.getMonth()]} de ${runtime.getFullYear()}.`;

    switch (task.repeat_mode) {
        case 'no_repeat':
            repetition_info = `${runtime.getDate()} de ${MONTHS[runtime.getMonth()]} de ${runtime.getFullYear()} às ${runtime.getHours()}h${String(runtime.getMinutes()).padStart(2, '0')}.`;
            since = 'Não se repete.';    
            break;
        
        case 'daily':
            repetition_info = `Repete diariamente às ${runtime.getHours()}h${String(runtime.getMinutes()).padStart(2, '0') }.`;
            break;

        case 'weekly':
            let weedays = ['domingo', 'segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira', 'sábado'];
            repetition_info = `Repete toda(o) ${weedays[runtime.getDay()]} às ${runtime.getHours()}h${String(runtime.getMinutes()).padStart(2, '0') }.`;

        default:
            break;
    };

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
                <p class="m-0 mt-3">${repetition_info}</p>
                <small class="text-muted">${since}</small>
                <br>
                <p class="m-0 mt-3 ${bg_crawler_queue_info} border rounded-pill small text-white font-weight-bold px-2" style="display: inline-block;">${crawler_queue_info}</p>
                <div class="d-flex justify-content-center mt-4 text-muted">
                    <a href="/detail/${task.crawl_request}/" 
                        target="_blank"
                        title="Visualizar coletor." class="rounded-circle bg-white border d-flex align-items-center justify-content-center scheduling-detail-options" 
                        rel="noopener noreferrer"
                        >
                        <i class="far fa-eye text-muted"></i>
                    </a>
                    <button title="Editar agendamento." 
                        onclick="edit_scheduling_task(${task.id})"
                        class="rounded-circle bg-white border mx-3 scheduling-detail-options">
                        <i class="fas fa-pen text-muted"></i>
                    </button>
                    <button title="Excluir agendamento." 
                        onclick="delete_schedule_task(${task.id})"
                        class="rounded-circle border bg-white scheduling-detail-options">
                        <i class="far fa-trash-alt text-muted"></i>
                    </button>
                </div>
    `;

    $('#detailSchedulingContent').html(task_detail_html);

    $('#detailScheduling').modal('show');

}

function edit_scheduling_task(task_id) {
    $('#detailScheduling').modal('hide');

    if (!tasks[task_id]) {
        console.error('Invalid task id!');
        return;
    }

    task_being_edited = {
        id: tasks[task_id].id,
        crawl_request: tasks[task_id].crawl_request,
        runtime: tasks[task_id].runtime,
        crawler_queue_behavior: tasks[task_id].crawler_queue_behavior,
        repeat_mode: tasks[task_id].repeat_mode,
        personalized_repetition_mode: tasks[task_id].personalized_repetition_mode
    };

    fill_set_scheduling(task_id);
    open_set_scheduling(false);    
}

function delete_schedule_task(task_id) {
    $('#detailScheduling').modal('hide');

    let delete_confirmed = confirm('Tem certeza que deseja deletar o agendamento?');

    if (!delete_confirmed)
        return;

    services.delete_task(task_id);
}

function fill_set_scheduling(task_id) {
    let task = tasks[task_id];

    if (!task)
        return;

    let runtime = task.runtime.substr(0, 16);

    $(`#crawl-selector option[value='${task.crawl_request}']`).attr('selected', 'selected');
    $('#scheduling-time').val(runtime);
    $(`#repeat-crawling-select option[value='${task.repeat_mode}']`).attr('selected', 'selected');
    $(`#crawler_queue_behavior option[value='${task.crawler_queue_behavior}']`).attr('selected', 'selected');
    

    $('#scheduling-personalized-repetition-info').css('display', 'none');

    $(`#crawl-selector`).multiselect('rebuild');
}

$(document).ready(function () {
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

    // $('#personalizedCrawlerRepetion').modal('show');

    // $('#setSchedulingModal').modal('show');

    $('#repeat-crawling-select').on('click', function () {
        let repeat_mode = $(this).val();

        if (task_being_edited)
            scheduling_task = task_being_edited;

        else
            scheduling_task = new_scheduling_config; 

        scheduling_task.repeat_mode = repeat_mode;

        if (repeat_mode == 'personalized') {
            update_repetition_info();
            open_personalized_crawler_repetition();
        } else {
            scheduling_task.personalized_repetition_mode = null;
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
                repetion.additional_data = [];
                for (let i in days_selected_to_repeat)
                    if (days_selected_to_repeat[i])
                        repetion.additional_data.push(parseInt(i));                    

                if (repetion.additional_data.length == 0)
                    $(`#dwr-${date.getDay()}`).click();

                show_days_of_week_repeat_options();
                break;
        
            case 'monthly':
                show_monthly_repeat_options();
                repetion.additional_data = { type: montly_repeat_type, value: montly_repeat_value};
                break;
                
            default:
                repetion.additional_data = null;
                break;
        }

        repeat_option_selected = repeat_mode;
        repetion.type = repeat_mode;

        update_repetition_info();
    });

    $('#interval-in').change(function () {
        repetion.interval = parseInt($(this).val());
        update_repetition_info();
    });

    $("input[name=finish-type]").change(function() {
        let input = $(this);

        let finish_type = input.attr('finish_type');
        
        repetion.finish.type = finish_type;
        switch (finish_type) {
            case 'never':
                repetion.finish.additional_data = null;
                break;
        
            case 'occurrence':
                repetion.finish.additional_data = repeat_finish_occurrences;                
                break;

            case 'date':
                repetion.finish.additional_data = repeat_finish_date;
                break;

            default:
                break;
        }

        update_repetition_info();
    });

    $('#finish-occurrence-in').on('click', function(){
        repeat_finish_occurrences = parseInt($(this).val());
        $('#finish-ocurrence').click();
        repetion.finish.additional_data = repeat_finish_occurrences;   
        update_repetition_info();             
    });

    $('#finish-date-in').change(function () {
        repeat_finish_date = $(this).val(); 
        $('#finish-date').click();
        repetion.finish.additional_data = repeat_finish_date;
        update_repetition_info();
    });

    $('input[name=montly-repeat]').change(function() {
        let input = $(this);

        montly_repeat_type = input.attr('montly_repeat');
        montly_repeat_value = parseInt($(`#montly-${montly_repeat_type}-sel`).find(":selected").val());

        repetion.additional_data.type = montly_repeat_type;
        repetion.additional_data.value = montly_repeat_value;
        update_repetition_info();
    });

    $('#montly-day-x-sel').on('change',function() {
        montly_repeat_value = parseInt($(this).find(":selected").val());
        montly_repeat_type = 'day-x';

        $('#montly-every-day-x').click();
        
        repetion.additional_data.type = montly_repeat_type;
        repetion.additional_data.value = montly_repeat_value;
        update_repetition_info();
    });

    $('#montly-first-weekday-sel').on('change', function () {
        montly_repeat_value = parseInt($(this).find(":selected").val());
        montly_repeat_type = 'first-weekday';

        $('#montly-first-weekday').click();

        repetion.additional_data.type = montly_repeat_type;
        repetion.additional_data.value = montly_repeat_value;
        update_repetition_info();
    });

    $('#montly-last-weekday-sel').on('change', function () {
        montly_repeat_value = parseInt($(this).find(":selected").val());
        montly_repeat_type = 'last-weekday';

        $('#montly-last-weekday').click();

        repetion.additional_data.type = montly_repeat_type;
        repetion.additional_data.value = montly_repeat_value;
        update_repetition_info();
    });

    init_default_options();

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

        scheduling_task.runtime = $(this).val(); 
    });

    $('#crawl-selector').on('change', function() {
        if (task_being_edited)
            scheduling_task = task_being_edited;

        else
            scheduling_task = new_scheduling_config; 

        scheduling_task.crawl_request = parseInt($(this).val());
    });

    update_calendar_mode('daily');
});
