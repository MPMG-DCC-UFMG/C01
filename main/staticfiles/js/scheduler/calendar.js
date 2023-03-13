var WEEKDAYS = [
    'Dom.',
    'Seg.',
    'Ter.',
    'Qua.',
    'Qui.',
    'Sex.',
    'Sáb.'
];

var HOURS = [
    '0 AM',
    '1 AM',
    '2 AM',
    '3 AM',
    '4 AM',
    '5 AM',
    '6 AM',
    '7 AM',
    '8 AM',
    '9 AM',
    '10 AM',
    '11 AM',
    '12 PM',
    '13 PM',
    '14 PM',
    '15 PM',
    '16 PM',
    '17 PM',
    '18 PM',
    '19 PM',
    '20 PM',
    '21 PM',
    '22 PM',
    '23 PM',
];

var MONTHS = [
    'Jan.',
    'Fev.',
    'Mar.',
    'Abr.',
    'Mai.',
    'Jun.',
    'Jul.',
    'Ago.',
    'Set.',
    'Out.',
    'Nov.',
    'Dez.',
];

var FLEX_CENTER = 'd-flex justify-content-center align-items-center';

var JANUARY = 0;
var DECEMBER = 11;

var calendar = {};

calendar.curr_date = calendar.active_date = new Date();
calendar.date_info = $('#curr-date');

calendar.yearly = {};
calendar.monthly = {};
calendar.weekly = {};
calendar.daily = {};

calendar.weekly.container = $('#calendar-weekly');
calendar.daily.container = $('#calendar-daily');
calendar.monthly.container = $('#calendar-monthly');
calendar.yearly.container = $('#calendar-monthly');
calendar.yearly.container = $('#calendar-yearly');
calendar.yearly.month_containers = $('.calendar-yearly-month');

calendar.daily.active_day = calendar.daily.curr_day = calendar.curr_date;
calendar.weekly.active_start_day = calendar.weekly.curr_start_day = new Date(calendar.curr_date.getFullYear(), 
                                                            calendar.curr_date.getMonth(), 
                                                            calendar.curr_date.getDate() - calendar.curr_date.getDay());
calendar.monthly.active_month = calendar.monthly.curr_month = new Date(calendar.curr_date.getFullYear(), calendar.curr_date.getMonth());
calendar.yearly.active_year = calendar.yearly.curr_year = calendar.curr_date.getFullYear();


calendar.fill_month = function (container, year, month) {
    let first_day = new Date(year, month, 1);
    let last_day = new Date(year, month + 1, 0);

    let weekday_month_start = first_day.getDay();
    let num_days_previous_month = (new Date(year, month, 0)).getDate();

    let calendar_cells = [];
    let i;

    for (i = 0; i < WEEKDAYS.length; i++)
        calendar_cells.push(`<div class="calendar-cell h6 text-center text-muted">${WEEKDAYS[i]}</div>`);

    i = num_days_previous_month - weekday_month_start + 1;
    for (i; i <= num_days_previous_month; i++) {
        calendar_cells.push(`<div class="d-flex justify-content-center calendar-cell no-current-month">
                                ${i}
                            </div>`);
    }

    let is_curr_day_css = '';
    for (i = 1; i <= last_day.getDate(); i++) {
        if (this.curr_date.getFullYear() == year && this.curr_date.getMonth() == month && this.curr_date.getDate() == i) 
            is_curr_day_css = `class="bg-primary rounded-circle text-white text-center border font-weight-bold" style="width: 1.8em; height: 2.3em; padding-top: 2px;"`;

        calendar_cells.push(`<div class="${FLEX_CENTER} calendar-cell" style="flex-direction: column;">
                                <div ${is_curr_day_css}>
                                ${i}
                                </div>
                                <div class="calendar-cell-content" id="calendar-cell-${year}-${month}-${i}">
                                
                                </div>
                            </div>`);

        is_curr_day_css = '';
    }

    let diff_until_saturday = 6 - last_day.getDay();

    for (i = 1; i <= diff_until_saturday; i++)
        calendar_cells.push(`<div class="d-flex justify-content-center calendar-cell no-current-month">${i}</div>`);


    container.empty();
    container.html(calendar_cells.join('\n'))
} 

calendar.monthly.show = function () {
    calendar.fill_month(this.container, this.active_month.getFullYear(), this.active_month.getMonth());
    this.container.css('display', 'grid');
    calendar.date_info.text(`${MONTHS[this.active_month.getMonth()]} de ${this.active_month.getFullYear()}`);
}

calendar.monthly.previous = function () {
    this.active_month = new Date(this.active_month.getFullYear(), this.active_month.getMonth() - 1);
    this.show();
}

calendar.monthly.next = function () {
    this.active_month = new Date(this.active_month.getFullYear(), this.active_month.getMonth() + 1);
    this.show();
}

calendar.monthly.today = function () {
    this.active_month = this.curr_month;
    this.show();
}

calendar.monthly.hide = function () {
    this.container.css('display', 'none');
}

calendar.yearly.show = function () {
    let i, month_el, month;
    for (i=0;i<this.month_containers.length;i++) {
        month_el = $(this.month_containers[i]);
        month = parseInt(month_el.attr('month'));
        calendar.fill_month(month_el, this.active_year, month);
        month_el.css('display', 'grid');
    }
    this.container.css('display', 'grid');

    calendar.date_info.text(`${this.active_year}`);
} 

calendar.yearly.next = function () {
    this.active_year++;
    this.show();
}

calendar.yearly.previous = function () {
    this.active_year--;
    this.show();
}

calendar.yearly.today = function() {
    this.active_year = this.curr_year;
    this.show();
}

calendar.yearly.hide = function () {
    for (let i = 0; i < this.month_containers.length; i++) 
        $(this.month_containers[i]).css('display', 'none');
    this.container.css('display', 'none');
}

calendar.weekly.show = function () {
    // mostra os dias da semana
    let calendar_cells = ['<div></div>'];

    let i;
    
    let active_year = this.active_start_day.getFullYear();
    let active_month = this.active_start_day.getMonth();
    let week_start_day = this.active_start_day.getDate();
    
    let day, day_repr, days = [];


    for (i=0;i<7;i++) {
        day = new Date(active_year, active_month, week_start_day + i);

        let diff_month_css_class = day.getMonth() != calendar.curr_date.getMonth() ? 'no-current-month' : '';

        if (day.toDateString() == calendar.curr_date.toDateString()) 
            day_repr = `<div class="${FLEX_CENTER} h4 rounded-circle border  bg-primary text-white p-0" style="width: 1.9em;height: 1.9em;">
                            ${day.getDate()}
                        </div>`;
        else 
            day_repr = `<div class="${FLEX_CENTER} h4 rounded-circle border ${diff_month_css_class} p-0" style="width: 1.9em;height: 1.9em;">
                            ${day.getDate()}
                        </div>`;

        calendar_cells.push(`<div>
                    <h2 class="${FLEX_CENTER} mb-3">
                        <div class="d-flex align-items-center" style="flex-direction: column;">
                            <div class="h6 text-muted">
                                ${WEEKDAYS[i]}
                            </div>
                            ${day_repr}
                        </div>
                    </h2>
                </div>`);
        
        days.push(day);
    }

    let hour_idx = 0;
    for (i=0;i<8 * 24;i++) {
        if (i % 8 == 0) 
            calendar_cells.push(`<div id="calendar-weekly-hour-${hour_idx}" class="${FLEX_CENTER} text-muted small">${HOURS[hour_idx++]}</div>`)
        
        else 
            calendar_cells.push(`<div id="calendar-weekly-cell-${hour_idx}-${i % 8 - 1}" class=""></div>`);
    }

    this.container.empty();
    this.container.html(calendar_cells.join('\n'));
    this.container.css('display', 'grid');

    let first_day_of_week = days[0];
    let last_day_of_week = days[6];

    let first_day_month = '';
    let first_day_year = '';
    
    let last_day_month = ` de ${MONTHS[last_day_of_week.getMonth()]}`;
    let last_day_year = ` de ${last_day_of_week.getFullYear()}`;

    if (first_day_of_week.getMonth() != last_day_of_week.getMonth()) 
        first_day_month = ` de ${MONTHS[first_day_of_week.getMonth()]}`;

    if (first_day_of_week.getFullYear() != last_day_of_week.getFullYear())
        first_day_year = ` de ${first_day_of_week.getFullYear()}`;

    calendar.date_info.text(`${first_day_of_week.getDate()}${first_day_month}${first_day_year} - ${last_day_of_week.getDate()}${last_day_month}${last_day_year}`);
}

calendar.weekly.next = function () {
    this.active_start_day = new Date(this.active_start_day.getFullYear(), this.active_start_day.getMonth(), this.active_start_day.getDate() + 7);
    this.show();
}

calendar.weekly.previous = function () {
    this.active_start_day = new Date(this.active_start_day.getFullYear(), this.active_start_day.getMonth(), this.active_start_day.getDate() - 7);
    this.show();
}

calendar.weekly.today = function () {
    this.active_start_day = this.curr_start_day;
    this.show();
}

calendar.weekly.hide = function () {
    this.container.css('display', 'none');
}

calendar.get_formated_date = function (day, month, year) {
    return `${String(day).padStart(2, '0')}-${String(month).padStart(2, '0') }-${year}`;
}

calendar.get_hour_from_str_datetime = function (str_datetime) {
    // expected format of str_datetime is like 2022-08-10T14:47:00Z
    return str_datetime.split('T')[1].split(':')[0];
}

calendar.daily.tasks = {};
calendar.daily.get_daily_tasks = function () {
    let day = this.active_day;
    let key = start_date = end_date = calendar.get_formated_date(day.getDate(), day.getMonth() + 1, day.getFullYear());

    let tasks_of_day = services.get_tasks_in_interval(start_date, end_date);
    // junta todos as listas de tasks do dia em uma única lista de tasks, garantindo que não haverá tasks repetidas
    
    let all_tasks_of_day = new Set();
    for (let hour in tasks_of_day) {
        for (let task of tasks_of_day[hour]) {
            all_tasks_of_day.add(task);
        }
    }
    
    this.tasks = {};
    for (let hour = 0;hour<24;hour++)
        this.tasks[String(hour).padStart(2, '0')] = [];
    
    let task_runtime, task;

    // iterates over all tasks of the day
    for (let task_id of all_tasks_of_day) {
        task = services.get_task(task_id);
        task_runtime = task.scheduler_config.start_date;
        key = calendar.get_hour_from_str_datetime(task_runtime);
        this.tasks[key].push(task);
    }
}

function get_task_next_run_text(now, next_run_date, timezone) {    
    next_run_text = new Intl.DateTimeFormat('pt-BR', {
        dateStyle: 'full',
        timeStyle: 'long',
        timeZone: timezone
    }).format(next_run_date);

    // the first letter must be capitalized
    next_run_text = next_run_text[0].toUpperCase() + next_run_text.slice(1);

    if (next_run_date.getDate() == now.getDate() && next_run_date.getMonth() == now.getMonth() && next_run_date.getFullYear() == now.getFullYear())
        next_run_text = next_run_text.replace(/^[^,]*/, 'Hoje');

    return next_run_text;
}

calendar.daily.show = function () {
    this.get_daily_tasks();

    let active_day_classes = this.curr_day.toDateString() == this.active_day.toDateString() ? 'bg-primary text-white' : ''; 

    let header = `<h2 class="h4 d-flex mb-3">
                        <div class="d-flex align-items-center" style="flex-direction: column;">
                            <div class="h6 text-muted">
                                ${WEEKDAYS[this.active_day.getDay()]}
                            </div>
                            <div class="${FLEX_CENTER} rounded-circle border ${active_day_classes}" style="width: 1.9em;height: 1.9em;">
                                ${this.active_day.getDate()}
                            </div>
                        </div>
                    </h2>`;

    let calendar_cells = [header, '<ul class="text-muted p-0" style="list-style: none;">'];

    let tasks_in_hour, task, key, bg_color, mb_size, i;
    for (let hour=0;hour<24;hour++){
        tasks_in_hour = [];

        key = String(hour).padStart(2, '0');

        for (i=0;i<this.tasks[key].length;i++) {
            task = this.tasks[key][i];
            
            switch (task.crawler_queue_behavior) {
                case 'wait_on_first_queue_position':
                    bg_color = 'bg-warning';
                    break;
            
                case 'run_immediately':
                    bg_color = 'bg-danger';
                    break;

                default:
                    bg_color = 'bg-primary';
                    break;
            }
            
            let now = get_now(task.scheduler_config.timezone);

            // O único caso em que o next_run não é definido é quando a coleta é agendada para ser executada uma única vez e o horário de início já passou.
            if (task.next_run == null)
                task.next_run = task.scheduler_config.start_date;

            let next_run_date = str_to_date(task.next_run);
            let_next_run_text = get_task_next_run_text(now, next_run_date, task.scheduler_config.timezone);

            let title = '';
            let opacity = 'opacity: 0.5;';
            
            let past_day = this.active_day.getDate() < now.getDate() 
                            && this.active_day.getMonth() == now.getMonth() 
                            && this.active_day.getFullYear() == now.getFullYear();

            if (past_day || next_run_date < now) 
                title = 'Coleta executada em: ' + next_run_text + '. \n\nClique para opções.';
            
            else 
                title = 'Coleta agendada para: ' + next_run_text + '. \n\nClique para opções.', opacity = '';
            
            tasks_in_hour.push(`
                <div
                    style="cursor: pointer; ${opacity}" 
                    onclick="show_task_detail(${task.id})" 
                    title="${title}"
                    class="${bg_color} text-white rounded-pill px-2 ml-2 mt-2">
                    ${task.crawler_name}
                </div>
            `);

        }

        mb_size = tasks_in_hour.length? 'mb-2' : 'mb-4';

        calendar_cells.push(`
            <li class="${mb_size}">
                <div class="d-flex align-items-center">
                    <span class="mr-3">
                        ${HOURS[hour]}
                    </span>
                    <div class="border-bottom" style="display: inline-block;flex: auto;">
                    </div>
                </div>
                <div class="d-flex justify-content-start align-items-center" style="padding-left: 3.3em; flex-wrap: wrap;">
                    ${tasks_in_hour.join('\n')}
                </div>
            </li>
        `);
    }

    calendar_cells.push('</ul>');

    this.container.empty();
    this.container.html(calendar_cells.join('\n'));

    this.container.css('display', 'block');

    calendar.date_info.text(`${WEEKDAYS[this.active_day.getDay()]}, ${this.active_day.getDate()} de ${MONTHS[this.active_day.getMonth()]} de ${this.active_day.getFullYear()}`);

}

calendar.daily.hide = function() {
    this.container.css('display', 'none');
}

calendar.daily.next = function () {
    this.active_day = new Date(this.active_day.getFullYear(), this.active_day.getMonth(), this.active_day.getDate() + 1);
    this.show();
}

calendar.daily.previous = function () {
    this.active_day = new Date(this.active_day.getFullYear(), this.active_day.getMonth(), this.active_day.getDate() - 1);
    this.show();
}

calendar.daily.today = function () {
    this.active_day = this.curr_day;
    this.show();
}
