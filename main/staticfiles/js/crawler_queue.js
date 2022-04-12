var SERVER_ADDRESS = window.location.origin;

// when this variable equals true, it blocks the interface update to prevent 
// the data being changed from being rewritten by the interface update
var UPDATING_MAX_CRAWLERS = false;

// the queue always has id = 1 as it is unique and designed that way
var CRAWLER_QUEUE_API_ADDRESS = SERVER_ADDRESS + '/api/crawler_queue/1/';

var MAX_FAST_CRAWLERS;
var MAX_MEDIUM_CRAWLERS;
var MAX_SLOW_CRAWLERS;

var FILTER_RUNNING_CRAWLERS_ACTIVE = 'all';
var FILTER_WAITING_CRAWLERS_ACTIVE = 'all';

var RUNNING_EMPTY_HTML = `<li class="border rounded p-3">
                            <p class="text-center m-0 font-weight-bold">
                                <i class="fa fa-exclamation-triangle" aria-hidden="true" style="font-size: 2em;"></i>
                                <br>
                                Sem coletores em execução.
                            </p>
                        </li>`;

var WAITING_EMPTY_HTML = `<li class="border rounded p-3">
                            <p class="text-center m-0 font-weight-bold">
                                <i class="fa fa-exclamation-triangle" aria-hidden="true" style="font-size: 2em;"></i>
                                <br>
                                Sem coletores aguardando execução.
                            </p>
                        </li>`;

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

    return `<li class="border rounded p-3 mt-3">
        <div class="d-flex justify-content-between p-0">
            <a href="${SERVER_ADDRESS + '/detail/' + item.crawler_id}"> ${ item.crawler_name } </a>
            <small class="" title="Tempo gasto coletando"> <i class="fa fa-clock-o fa-lg" aria-hidden="true"></i> ${countdown(elapsed_time)}</small>
        </div>
        <small>Coletando desde: ${timestamp_converter(item.last_modified)} </small>
    </li>`;
}

function get_waiting_li_html(item) {

    let now = Date.now();
    let elapsed_time = Math.floor((now - item.creation_date) / 1000);

    return `<li class="border rounded p-3 mt-3">
                <div class="d-flex justify-content-between p-0">
                    <a href="${SERVER_ADDRESS + '/detail/' + item.crawler_id}"> ${ item.crawler_name } </a>
                    <small class="" title="Tempo de fila"> <i class="fa fa-clock-o fa-lg" aria-hidden="true"></i> ${countdown(elapsed_time)}</small>
                </div>
                <small>Aguardando desde: ${timestamp_converter(item.creation_date)} </small>
            </li>`;
}

function update_ui() {
    if (UPDATING_MAX_CRAWLERS)
        return;

    $.ajax({
        url: CRAWLER_QUEUE_API_ADDRESS,
        type: 'get',
        success: function (data) {
            
            $('#in_max_fast_crawler').val(data.max_fast_runtime_crawlers_running);
            $('#in_max_fast_crawler_number').val(data.max_fast_runtime_crawlers_running);

            $('#in_max_medium_crawler').val(data.max_medium_runtime_crawlers_running)
            $('#in_max_medium_crawler_number').val(data.max_medium_runtime_crawlers_running);

            $('#in_max_slow_crawler').val(data.max_slow_runtime_crawlers_running)
            $('#in_max_slow_crawler_number').val(data.max_slow_runtime_crawlers_running);


            MAX_FAST_CRAWLERS = data.max_fast_runtime_crawlers_running;
            MAX_MEDIUM_CRAWLERS = data.max_medium_runtime_crawlers_running;
            MAX_SLOW_CRAWLERS = data.max_slow_runtime_crawlers_running;

            let items = data.items;

            let running = items.filter(function (item) {
                return item.running;
            });

            if (running.length == 0) {
                $('#running-list').html(RUNNING_EMPTY_HTML);
            } else {
                let item;
                let running_html = [];
                for (let i=0;i<running.length;i++) {
                    item = running[i];
                    running_html.push(get_running_li_html(item));
                }
                $('#running-list').html(running_html);
            }

            let waiting = items.filter(function (item) {
                return !item.running;
            }); 

            if (waiting.length == 0) {
                $('#waiting-list').html(WAITING_EMPTY_HTML);
            } else {
                let item;
                let waiting_html = [];
                for (let i=0;i<waiting.length;i++) {
                    item = waiting[i];
                    waiting_html.push(get_waiting_li_html(item));
                }
                $('#waiting-list').html(waiting_html);
            }
            
        },
        error: function () {
            console.error('Não foi possível atualizar a Interface!');
        }
    });
}

function openEditMaxCrawlersModal() {
    UPDATING_MAX_CRAWLERS = true;
    $('#editMaxCrawler').modal('show');
}

function closeMaxCrawlersModal() {
    UPDATING_MAX_CRAWLERS = false;
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
            UPDATING_MAX_CRAWLERS = false;
        },
        error: function (data) {
            alert('Houve um erro ao editar o campo!');
        }
    });
}

function deactive_filter_btn(btn_id) {
    let btn_ref = $(`#${btn_id}`);

    btn_ref.removeClass('active-tab-color');
    btn_ref.removeClass('text-white');
    btn_ref.removeClass('font-weight-bold');
    btn_ref.addClass('text-muted');
}

function active_filter_btn(btn_id) {
    let btn_ref = $(`#${btn_id}`);

    btn_ref.removeClass('text-muted');
    btn_ref.addClass('active-tab-color');
    btn_ref.addClass('text-white');
    btn_ref.addClass('font-weight-bold');
}

function filter_running_crawlers(filter) {
    if (FILTER_RUNNING_CRAWLERS_ACTIVE == filter)
        return;

    deactive_filter_btn(`btn_running_filter_${FILTER_RUNNING_CRAWLERS_ACTIVE}`);
    active_filter_btn(`btn_running_filter_${filter}`);

    FILTER_RUNNING_CRAWLERS_ACTIVE = filter;

}

function filter_waiting_crawlers(filter) {
    if (FILTER_WAITING_CRAWLERS_ACTIVE == filter)
        return;

    deactive_filter_btn(`btn_waiting_filter_${FILTER_WAITING_CRAWLERS_ACTIVE}`);
    active_filter_btn(`btn_waiting_filter_${filter}`);

    FILTER_WAITING_CRAWLERS_ACTIVE = filter;
}

$(document).ready(function() {
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