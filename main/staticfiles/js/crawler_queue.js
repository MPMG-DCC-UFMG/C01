var SERVER_ADDRESS = window.location.origin;

// when this variable equals true, it blocks the interface update to prevent 
// the data being changed from being rewritten by the interface update
var UPDATING_SCHEDULER_CONFIG = false;

// the queue always has id = 1 as it is unique and designed that way
var CRAWLER_QUEUE_API_ADDRESS = SERVER_ADDRESS + '/api/crawler_queue/1/';

var MAX_FAST_CRAWLERS;
var MAX_MEDIUM_CRAWLERS;
var MAX_SLOW_CRAWLERS;

var FILTER_RUNNING_CRAWLERS_ACTIVE = 'fast';
var FILTER_WAITING_CRAWLERS_ACTIVE = 'fast';

var QUEUE_ITEM_TO_FORCE_EXEC;

var RUNNING_EMPTY_HTML = `<li class="border rounded p-3 mt-3">
                            <p class="text-center m-0 font-weight-bold">
                                <i class="fa fa-exclamation-triangle" aria-hidden="true" style="font-size: 2em;"></i>
                                <br>
                                Sem coletores em execução.
                            </p>
                        </li>`;

var WAITING_EMPTY_HTML = `<li class="border rounded p-3 mt-3">
                            <p class="text-center m-0 font-weight-bold">
                                <i class="fa fa-exclamation-triangle" aria-hidden="true" style="font-size: 2em;"></i>
                                <br>
                                Sem coletores aguardando execução.
                            </p>
                        </li>`;

var WAITING_LIST_FILTER_REF = $('#waiting-filter-list');
var RUNNING_LIST_FILTER_REF = $('#running-filter-list');

function countdown(seconds) {
    let days = Math.floor(seconds / (3600 * 24));
    seconds  -= days * 3600 * 24;

    let hours = Math.floor(seconds / 3600);
    seconds  -= hours * 3600;

    let minutes = Math.floor(seconds / 60);
    seconds -= minutes * 60;

    let elapsed_time = '';

    if (days > 0)
        elapsed_time += `${days}d `

    if (hours > 0)
        elapsed_time += `${hours}h `

    if (minutes > 0)
        elapsed_time += `${minutes}m `

    elapsed_time += `${seconds}s`

    return elapsed_time;
}

function pad_time(time) {
    return time >= 10 ? time : '0' + time;
}

function timestamp_converter(timestamp) {
    let date = new Date(timestamp);

    let days = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];
    let months = ['Jan', 'Fev', 'Mar', 'Abr', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];

    let cur_date = new Date();

    let year = cur_date.getFullYear() != date.getFullYear() ? date.getFullYear() : '';

    return `${days[date.getDay()]}, ${pad_time(date.getDate())} de ${months[date.getMonth()]} ${year} - ${pad_time(date.getHours())}h${pad_time(date.getMinutes())}`;
}

function get_running_li_html(item) {
    let now = Date.now();
    let elapsed_time = Math.floor((now - item.last_modified) / 1000);

    let forced_execution_badge = '';

    if (item.forced_execution)
        forced_execution_badge = '<span class="badge badge-danger">Execução forçada</span>';

    return `<li class="border rounded p-3 mt-3">
        <div class="d-flex justify-content-between p-0">
            <div>
                ${forced_execution_badge}
                <a href="${SERVER_ADDRESS + '/detail/' + item.crawler_id}"> ${ item.crawler_name } </a>
            </div>
            <small class="" title="Tempo gasto coletando"> <i class="fa fa-clock-o fa-lg" aria-hidden="true"></i> ${countdown(elapsed_time)}</small>
        </div>
        <small>Coletando desde: ${timestamp_converter(item.last_modified)} </small>
    </li>`;
}

function get_waiting_li_html(item, above_queue_item, bellow_queue_item) {

    let now = Date.now();
    let elapsed_time = Math.floor((now - item.creation_date) / 1000);

    let btn_previous = '';
    if (bellow_queue_item) {
        btn_previous = `
            <button
                title="Trocar posição com o de baixo"
                onclick="switch_position('${item.id}','${bellow_queue_item}')"
                class="border-0 rounded-left bg-white crawler-queue-switch-position p-0 mx-1">
                <i class="fa fa-chevron-down" aria-hidden="true"></i>
            </button>
        `;
    }

    let btn_next = '';
    if (above_queue_item) {
        btn_next = `
            <button
                title="Trocar posição com o de cima"
                onclick="switch_position('${item.id}','${above_queue_item}')"
                class="border-0 rounded-right bg-white crawler-queue-switch-position p-0 mx-1">
                <i class="fa fa-chevron-up" aria-hidden="true"></i>
            </button>   
        `;
    }

    let switch_position = '';
    if (above_queue_item || bellow_queue_item) {
        switch_position = `
            <div class="rounded border px-2 py-0 mr-2">
                ${btn_previous}
                ${btn_next}   
            </div>
        `
    }

    return `<li class="border rounded p-3 mt-3">
                <div class="d-flex justify-content-between p-0">
                    <a href="${SERVER_ADDRESS + '/detail/' + item.crawler_id}"> ${ item.crawler_name } </a>
                    <small class="" title="Tempo de fila"> <i class="fa fa-clock-o fa-lg" aria-hidden="true"></i> ${countdown(elapsed_time)}</small>
                </div>
                <div class="d-flex justify-content-between align-items-center">
                    <small>Aguardando desde: ${timestamp_converter(item.creation_date)} </small>
                    <div class="d-flex justify-content-end mt-2" style="flex: auto;">
                        ${switch_position}
                        <button
                            title="Remover da fila"
                            onclick="remove_item_from_queue('${item.id}')"
                            class="border py-0 rounded-circle bg-light crawler-queue-remove-item mr-2">
                            <i class="fa fa-times" aria-hidden="true"></i>
                        </button>
                        <button
                            title="Forçar execução"
                            onclick="openForceExecutionConfirmModal('${item.id}')"
                            class="px-2 py-0 border rounded-circle bg-light crawler-queue-force-execution">
                            <i class="fa fa-bolt" aria-hidden="true"></i>
                        </button>
                    </div>
                </div>
            </li>`;
}

function hide_waiting_filters() {
    WAITING_LIST_FILTER_REF.removeClass('d-flex');
    WAITING_LIST_FILTER_REF.addClass('d-none');
}

function show_waiting_filters() {
    WAITING_LIST_FILTER_REF.removeClass('d-none');
    WAITING_LIST_FILTER_REF.addClass('d-flex');
}

function hide_running_filters() {
    RUNNING_LIST_FILTER_REF.removeClass('d-flex');
    RUNNING_LIST_FILTER_REF.addClass('d-none');
}

function show_running_filters() {
    RUNNING_LIST_FILTER_REF.removeClass('d-none');
    RUNNING_LIST_FILTER_REF.addClass('d-flex');
}

function update_waiting_queue(items) {
    let waiting_all = items.filter(function (item) {
        return !item.running;
    });

    let waiting_fast = filter_by_queue_type(waiting_all, 'fast');
    let waiting_medium = filter_by_queue_type(waiting_all, 'medium');
    let waiting_slow = filter_by_queue_type(waiting_all, 'slow');

    let item;
    let waiting_html = [];

    $('#qtd_waiting_crawler_fast').text(waiting_fast.length);
    $('#qtd_waiting_crawler_medium').text(waiting_medium.length);
    $('#qtd_waiting_crawler_slow').text(waiting_slow.length);

    if (FILTER_WAITING_CRAWLERS_ACTIVE == 'fast')
        waiting = waiting_fast;

    else if (FILTER_WAITING_CRAWLERS_ACTIVE == 'medium')
        waiting = waiting_medium;

    else 
        waiting = waiting_slow;

    if (waiting.length == 0) {
        $('#waiting-list').html(WAITING_EMPTY_HTML);

        if (waiting_fast.length == 0 && waiting_medium.length == 0 && waiting_slow.length == 0) 
            hide_waiting_filters();

    } else {
        show_waiting_filters();

        waiting.sort((a, b) => (a.position > b.position) ? 1 : -1);

        let above_queue_item = null, bellow_queue_item;
        item = waiting[0];

        if (waiting.length == 1) {
            bellow_queue_item = null;
            waiting_html.push(get_waiting_li_html(item, above_queue_item, bellow_queue_item));

        } else {
            bellow_queue_item = waiting[1].id;
            waiting_html.push(get_waiting_li_html(item, above_queue_item, bellow_queue_item));

            let i;

            for (i = 1; i < waiting.length - 1; i++) {
                above_queue_item = waiting[i - 1].id;
                bellow_queue_item = waiting[i + 1].id;

                item = waiting[i];
                waiting_html.push(get_waiting_li_html(item, above_queue_item, bellow_queue_item));
            }

            bellow_queue_item = null;
            above_queue_item = waiting[i - 1].id;

            item = waiting[i];

            waiting_html.push(get_waiting_li_html(item, above_queue_item, bellow_queue_item));
        }

        $('#waiting-list').html(waiting_html);
    }
}

function update_running_queue(items) {
    let running_all = items.filter(function (item) {
        return item.running;
    });
    
    let running_fast = filter_by_queue_type(running_all, 'fast');
    let running_medium = filter_by_queue_type(running_all, 'medium');
    let running_slow = filter_by_queue_type(running_all, 'slow');

    $('#qtd_running_crawler_fast').text(`${running_fast.length}/${MAX_FAST_CRAWLERS}`);
    $('#qtd_running_crawler_medium').text(`${running_medium.length}/${MAX_MEDIUM_CRAWLERS}`);
    $('#qtd_running_crawler_slow').text(`${running_slow.length}/${MAX_SLOW_CRAWLERS}`);

    if (FILTER_RUNNING_CRAWLERS_ACTIVE == 'fast')
        running = running_fast;

    else if (FILTER_RUNNING_CRAWLERS_ACTIVE == 'medium')
        running = running_medium;

    else
        running = running_slow;

    if (running.length == 0) {
        $('#running-list').html(RUNNING_EMPTY_HTML);

        if (running_fast.length == 0 && running_medium.length == 0 && running_slow.length == 0)
            hide_running_filters();

    } else {
        show_running_filters();

        let item;
        let running_html = [];
        for (let i = 0; i < running.length; i++) {
            item = running[i];
            running_html.push(get_running_li_html(item));
        }
        $('#running-list').html(running_html);
    }
}

function update_scheduler_config(data) {
    $('#in_max_fast_crawler').val(data.max_fast_runtime_crawlers_running);
    $('#in_max_fast_crawler_number').val(data.max_fast_runtime_crawlers_running);

    $('#in_max_medium_crawler').val(data.max_medium_runtime_crawlers_running)
    $('#in_max_medium_crawler_number').val(data.max_medium_runtime_crawlers_running);

    $('#in_max_slow_crawler').val(data.max_slow_runtime_crawlers_running)
    $('#in_max_slow_crawler_number').val(data.max_slow_runtime_crawlers_running);

    MAX_FAST_CRAWLERS = data.max_fast_runtime_crawlers_running;
    MAX_MEDIUM_CRAWLERS = data.max_medium_runtime_crawlers_running;
    MAX_SLOW_CRAWLERS = data.max_slow_runtime_crawlers_running;
}

function update_ui() {
    if (UPDATING_SCHEDULER_CONFIG)
        return;

    $.ajax({
        url: CRAWLER_QUEUE_API_ADDRESS,
        type: 'get',
        success: function (data) {
            update_scheduler_config(data);

            let items = data.items;

            update_running_queue(items);
            update_waiting_queue(items);        
        },
        error: function () {
            console.error('Não foi possível atualizar a Interface!');
        }
    });
}

function openEditMaxCrawlersModal() {
    UPDATING_SCHEDULER_CONFIG = true;
    $('#editMaxCrawler').modal('show');
}

function closeMaxCrawlersModal() {
    UPDATING_SCHEDULER_CONFIG = false;
    $('#editMaxCrawler').modal('hide');
}

function updateMaxCrawlers() {
    $('#editMaxCrawler').modal('hide');

    let num_max_fast_crawlers = $('#in_max_fast_crawler_number').val();
    let num_max_medium_crawlers = $('#in_max_medium_crawler_number').val();
    let num_max_slow_crawlers = $('#in_max_slow_crawler_number').val();

    data = {}

    if (num_max_fast_crawlers != MAX_FAST_CRAWLERS)
        data.max_fast_runtime_crawlers_running = num_max_fast_crawlers;

    if (num_max_medium_crawlers)
        data.max_medium_runtime_crawlers_running = num_max_medium_crawlers;

    if (num_max_slow_crawlers)
        data.max_slow_runtime_crawlers_running = num_max_slow_crawlers;

    $.ajax({
        url: CRAWLER_QUEUE_API_ADDRESS,
        type: 'put',
        dataType: 'json',
        async: false,
        data: data,
        success: function (data) {
            UPDATING_SCHEDULER_CONFIG = false;
        },
        error: function (data) {
            alert('Houve um erro ao editar o campo!');
        }
    });
}

function deactive_filter_btn(btn_id) {
    let btn_ref = $(`#${btn_id}`);

    btn_ref.removeClass('crawler-queue-active-tab-color');
    btn_ref.removeClass('text-white');
    btn_ref.removeClass('font-weight-bold');
    btn_ref.addClass('text-muted');
}

function active_filter_btn(btn_id) {
    let btn_ref = $(`#${btn_id}`);

    btn_ref.removeClass('text-muted');
    btn_ref.addClass('crawler-queue-active-tab-color');
    btn_ref.addClass('text-white');
    btn_ref.addClass('font-weight-bold');
}

function filter_running_crawlers(filter) {
    if (FILTER_RUNNING_CRAWLERS_ACTIVE == filter)
        return;

    deactive_filter_btn(`btn_running_filter_${FILTER_RUNNING_CRAWLERS_ACTIVE}`);
    active_filter_btn(`btn_running_filter_${filter}`);

    FILTER_RUNNING_CRAWLERS_ACTIVE = filter;

    update_ui();
}

function filter_waiting_crawlers(filter) {
    if (FILTER_WAITING_CRAWLERS_ACTIVE == filter)
        return;

    deactive_filter_btn(`btn_waiting_filter_${FILTER_WAITING_CRAWLERS_ACTIVE}`);
    active_filter_btn(`btn_waiting_filter_${filter}`);

    FILTER_WAITING_CRAWLERS_ACTIVE = filter;

    update_ui();
}

function switch_position(a, b) {
    UPDATING_SCHEDULER_CONFIG = true;
    let switch_position_address = CRAWLER_QUEUE_API_ADDRESS + `switch_position/?a=${a}&b=${b}`;
    
    $.ajax({
        url: switch_position_address,
        type: 'get',
        dataType: 'json',
        async: false,
        success: function (data) {
            UPDATING_SCHEDULER_CONFIG = false;
            update_ui();
        },
        error: function (data) {
            alert('Houve um erro ao trocar posições na fila!');
        }
    });
}

function forceExecution() {
    let force_exec_address = CRAWLER_QUEUE_API_ADDRESS + `force_execution?queue_item_id=${QUEUE_ITEM_TO_FORCE_EXEC}`;

    $.ajax({
        url: force_exec_address,
        type: 'get',
        dataType: 'json',
        async: false,
        success: function (data) {
            UPDATING_SCHEDULER_CONFIG = false;
            update_ui();
        },
        error: function (data) {
            alert('Houve um erro ao forçar execução do coletor!');
        }
    });
    $('#force-execution-modal').modal('hide');
}

function remove_item_from_queue(queue_item_id) {
    let remove_queue_item_address = CRAWLER_QUEUE_API_ADDRESS + `remove_item?queue_item_id=${queue_item_id}`;
    UPDATING_SCHEDULER_CONFIG = true;

    $.ajax({
        url: remove_queue_item_address,
        type: 'get',
        dataType: 'json',
        async: false,
        success: function (data) {
            UPDATING_SCHEDULER_CONFIG = false;
            update_ui();
        },
        error: function (data) {
            alert('Houve um erro ao remover o item da fila!');
        }
    });
}

function closeForceExecutionModal() {
    UPDATING_SCHEDULER_CONFIG = false;
    $('#force-execution-modal').modal('hide');
}

function openForceExecutionConfirmModal(queue_item_to_force_exec) {
    QUEUE_ITEM_TO_FORCE_EXEC = queue_item_to_force_exec;

    UPDATING_SCHEDULER_CONFIG = true;
    $('#force-execution-modal').modal('show');
}

function filter_by_queue_type(list, queue_type) {
    return list.filter(function (item) {
        return item.queue_type == queue_type;
    });
} 

function get_default_active_tab() {
    $.ajax({
        url: CRAWLER_QUEUE_API_ADDRESS,
        type: 'get',
        async: false,
        success: function (data) {
            let items = data.items;

            let waiting_all = items.filter(function (item) {
                return !item.running;
            });

            let waiting_fast = filter_by_queue_type(waiting_all, 'fast');
            let waiting_medium = filter_by_queue_type(waiting_all, 'medium');
            let waiting_slow = filter_by_queue_type(waiting_all, 'slow');

            deactive_filter_btn(`btn_waiting_filter_${FILTER_WAITING_CRAWLERS_ACTIVE}`);

            if (waiting_fast.length > 0)
                FILTER_WAITING_CRAWLERS_ACTIVE = 'fast';
            
            else if (waiting_medium.length > 0) {
                FILTER_WAITING_CRAWLERS_ACTIVE = 'medium';
            }

            else if (waiting_slow.length > 0)
                FILTER_WAITING_CRAWLERS_ACTIVE = 'slow';

            active_filter_btn(`btn_waiting_filter_${FILTER_WAITING_CRAWLERS_ACTIVE}`);

            let running_all = items.filter(function (item) {
                return item.running;
            });

            let running_fast = filter_by_queue_type(running_all, 'fast');
            let running_medium = filter_by_queue_type(running_all, 'medium');
            let running_slow = filter_by_queue_type(running_all, 'slow');

            deactive_filter_btn(`btn_running_filter_${FILTER_RUNNING_CRAWLERS_ACTIVE}`);

            if (running_fast.length > 0)
                FILTER_RUNNING_CRAWLERS_ACTIVE = 'fast';

            else if (running_medium.length > 0)
                FILTER_RUNNING_CRAWLERS_ACTIVE = 'medium';

            else if (running_slow.length > 0)
                FILTER_RUNNING_CRAWLERS_ACTIVE = 'slow';

            active_filter_btn(`btn_running_filter_${FILTER_RUNNING_CRAWLERS_ACTIVE}`);

        },
        error: function () {
            console.error('Não foi possível obter a fila de coletas!');
        }
    });
}

$(document).ready(function() {
    get_default_active_tab();

    update_ui();

    setInterval(function(){update_ui()},5000);

    $('#in_max_fast_crawler').on('input', function() {
        $('#in_max_fast_crawler_number').val(this.value);
    });

    $('#in_max_medium_crawler').on('input', function () {
        $('#in_max_medium_crawler_number').val(this.value);
    }); 
    
    $('#in_max_slow_crawler').on('input', function () {
        $('#in_max_slow_crawler_number').val(this.value);
    });

    $('#in_max_crawler_number').on('input', function () {
        if (this.value > 1000)
            this.value = 1000;

        $('#in_max_crawler').val(this.value);
    });

});