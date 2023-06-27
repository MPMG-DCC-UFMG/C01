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
var MAX_TASKS = 3;

var calendar = {};

calendar.curr_date = calendar.active_date = new Date();
calendar.date_info = $('#curr-date');

calendar.yearly = {};
calendar.monthly = {};
calendar.weekly = {};
calendar.daily = {};

calendar.weekly.container = $('#calendar-weekly');

calendar.weekly.weekdays_container = $('#calendar-weekly-weekdays');
calendar.weekly.days_container = $('#calendar-weekly-days');

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

calendar.monthly.tasks = {};

calendar.monthly.get_tasks = function (start_date, end_date) {    
    let formatted_start_date = calendar.get_formated_date(start_date.getDate(), start_date.getMonth() + 1, start_date.getFullYear());
    let formatted_end_date = calendar.get_formated_date(end_date.getDate(), end_date.getMonth() + 1, end_date.getFullYear());

    let tasks = services.get_tasks_in_interval(formatted_start_date, formatted_end_date);

    this.tasks = tasks;
}

calendar.monthly.get_schedulings_html = function (schedulings, curr_date) {
    if (!schedulings)
        return '';

    let schedulings_html = '', task;
    
    let title = '';
    let bg_color = '';
    let opacity = '';

    let num_tasks = schedulings.length;

    if (num_tasks > MAX_TASKS) {
        for (let i = 0; i < MAX_TASKS - 1; i++) {
            task = TASKS[schedulings[i]];

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

            [title, opacity] = get_task_title_and_opacity(task, curr_date);

            schedulings_html += `<div 
                            onclick="show_task_detail(${task.id})" 
                            title="${title}"
                            class="px-2 py-0 ${bg_color} rounded-pill text-white text-container mt-1 w-100"
                            style="overflow: hidden; 
                                    white-space: nowrap; 
                                    cursor: pointer;
                                    padding: 5px 0px 5px 0px;
                                    ${opacity}">
                            <p  
                                style="font-size: .75em;"
                                class="font-weight-bold m-0 p-0 scroll-text">
                                ${task.crawler_name}
                            </p>
                        </div>`;
        }

        let tasks_not_shown = [];
        for (let i = MAX_TASKS - 1; i < num_tasks; i++)
            tasks_not_shown.push(TASKS[schedulings[i]].id);

        let formatted_date = calendar.get_formated_date(curr_date.getDate(), curr_date.getMonth() + 1, curr_date.getFullYear());

        schedulings_html += `
                    <div 
                        style="cursor: pointer;"
                        onclick="show_more_schedulings([${tasks_not_shown}], '${formatted_date}', '0', '0')"
                        class="px-2 py-0 bg-light rounded border border-dark rounded-pill mt-2 text-center">
                        <p class="font-weight-bold m-0 p-0" style="font-size: .75em;">+${num_tasks - MAX_TASKS + 1} outras</p>
                    </div>`;

    } else {
        for (let i = 0; i < schedulings.length; i++) {
            task = TASKS[schedulings[i]];
            
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
    
            [title, opacity] = get_task_title_and_opacity(task, curr_date)
    
            schedulings_html += `<div 
                                    onclick="show_task_detail(${task.id})" 
                                    title="${title}"
                                    class="px-2 py-0 ${bg_color} rounded-pill text-white text-container mt-1 w-100"
                                    style="overflow: hidden; 
                                            white-space: nowrap; 
                                            cursor: pointer;
                                            padding: 5px 0px 5px 0px;
                                            ${opacity}">
                                    <p  
                                        style="font-size: .75em;"
                                        class="font-weight-bold m-0 p-0 scroll-text">
                                        ${task.crawler_name}
                                    </p>
                                </div>`;
        }
    }

    return schedulings_html;
}

calendar.monthly.fill_cells = function (container, year, month) {
    let first_day = new Date(year, month, 1);
    let last_day = new Date(year, month + 1, 0);
    
    let weekday_month_start = first_day.getDay();
    let num_days_previous_month = (new Date(year, month, 0)).getDate();
    
    let previous_month = num_days_previous_month - weekday_month_start + 1 > 0 ? month - 1 : month;

    let start_date = new Date(year, previous_month, num_days_previous_month - weekday_month_start + 1);
    let end_date;

    if (6 - last_day.getDay() == 0)
        end_date = last_day;

    else 
        end_date = new Date(year, month + 1, 6 - last_day.getDay());

    this.get_tasks(start_date, end_date);

    let calendar_cells = [];
    for (i = 0; i < WEEKDAYS.length; i++) {
        calendar_cells.push(`<div class="calendar-cell">
                                <h2 class="h6 text-center text-muted">
                                ${WEEKDAYS[i]}
                                </h2>
                            </div>`);
    }

    i = num_days_previous_month - weekday_month_start + 1;
    let date, formatted_date, schedulings_html;
    
    let bg_color = '';
    for (i; i <= num_days_previous_month; i++) {
        date = new Date(year, previous_month, i);
        formatted_date = calendar.get_formated_date(date.getDate(), date.getMonth() + 1, date.getFullYear());
        schedulings_html = this.get_schedulings_html(this.tasks[formatted_date], date);
        
        bg_color = date.getDay() % 2 ? 'bg-light' : 'bg-white';

        calendar_cells.push(`<div class="${bg_color} calendar-cell no-current-month rounded p-2 border">
                                <div class="w-100">
                                    <div class="d-flex justify-content-center"> 
                                        <p class="m-0 p-0 font-weight-bold">${i}</p>
                                    </div>
                                    <div>
                                        ${schedulings_html}
                                    </div>    
                                </div>
                            </div>`);
    }

    let custom_style = '';
    for (i = 1; i <= last_day.getDate(); i++) {
        if (calendar.curr_date.getFullYear() == year 
            && calendar.curr_date.getMonth() == month 
            && calendar.curr_date.getDate() == i) 
                custom_style = `class="bg-primary rounded-circle text-white text-center border font-weight-bold" style="width: 1.8em; height: 1.9em; padding-top: 2px;"`;
        else 
            custom_style = 'class="m-0 p-0 font-weight-bold"';
        

        date = new Date(year, month, i);

        bg_color = date.getDay() % 2 ? 'bg-light' : 'bg-white';

        formatted_date = calendar.get_formated_date(date.getDate(), date.getMonth() + 1, date.getFullYear());
        schedulings_html = this.get_schedulings_html(this.tasks[formatted_date], date);

        calendar_cells.push(`<div class="calendar-cell calendar-cell-monthly rounded p-2 border ${bg_color}">
                                <div class="w-100">
                                    <div class="d-flex justify-content-center">
                                        <p ${custom_style}>${i}</p>
                                    </div>
                                    <div 
                                        id="calendar-cell-${year}-${month}-${i}">
                                        ${schedulings_html}
                                    </div>
                                </div>
                            </div>`);

    }

    let diff_until_saturday = 6 - last_day.getDay();

    for (i = 1; i <= diff_until_saturday; i++) {
        date = new Date(year, month + 1, i);

        formatted_date = calendar.get_formated_date(date.getDate(), date.getMonth() + 1, date.getFullYear());
        schedulings_html = this.get_schedulings_html(this.tasks[formatted_date], date);

        bg_color = date.getDay() % 2 ? 'bg-light' : 'bg-white';

        calendar_cells.push(`<div class="${bg_color} calendar-cell no-current-month rounded p-2 border">
                                <div class="w-100">
                                    <div class="d-flex justify-content-center"> 
                                        <p class="m-0 p-0 font-weight-bold">${i}</p>
                                    </div>
                                    <div>
                                        ${schedulings_html}
                                    </div>    
                                </div>
                            </div>`);
    }

    container.empty();
    container.html(calendar_cells.join('\n'))
} 

calendar.monthly.show = function () {
    this.fill_cells(this.container, this.active_month.getFullYear(), this.active_month.getMonth());
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

calendar.show_tasks_of_day = function (date) {
    let start_date = end_date = calendar.get_formated_date(date.getDate(), date.getMonth() + 1, date.getFullYear());
    
    let tasks = services.get_tasks_in_interval(start_date, end_date);
    let tasks_of_day = [];

    //checks if tasks has a key equals to start_date
    if (tasks.hasOwnProperty(start_date)) 
        tasks_of_day = tasks[start_date];
    
    show_more_schedulings(tasks_of_day, start_date, 0, 0);
}

calendar.yearly.fill_month = function (container, year, month) {
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
        calendar_cells.push(`<div
                                onclick="calendar.show_tasks_of_day(new Date(${year}, ${month - 1}, ${i}))" 
                                class="d-flex justify-content-center calendar-cell no-current-month" style="cursor: pointer;">
                                ${i}
                            </div>`);
    }



    let is_curr_day_css = '';
    for (i = 1; i <= last_day.getDate(); i++) {
        if (calendar.curr_date.getFullYear() == year && calendar.curr_date.getMonth() == month && calendar.curr_date.getDate() == i)
            is_curr_day_css = `class="bg-primary rounded-circle text-white text-center border font-weight-bold" style="width: 1.75em; height: 1.9m; padding-top: 2px;"`;

        calendar_cells.push(`<div 
                                onclick="calendar.show_tasks_of_day(new Date(${year}, ${month}, ${i}))"
                                class="${FLEX_CENTER} calendar-cell" style="cursor: pointer;">
                                <div ${is_curr_day_css} >
                                ${i}
                                </div>
                            </div>`);

        is_curr_day_css = '';
    }

    let diff_until_saturday = 6 - last_day.getDay();

    for (i = 1; i <= diff_until_saturday; i++)
        calendar_cells.push(`<div 
                                onclick="calendar.show_tasks_of_day(new Date(${year}, ${month + 1}, ${i}))"
                                class="d-flex justify-content-center calendar-cell no-current-month" style="cursor: pointer;">
                                    ${i}
                            </div>`);


    container.empty();
    container.html(calendar_cells.join('\n'))
}

calendar.yearly.show = function () {
    let i, month_el, month;

    for (i=0;i<this.month_containers.length;i++) {
        month_el = $(this.month_containers[i]);
        month = parseInt(month_el.attr('month'));
        this.fill_month(month_el, this.active_year, month);
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

calendar.weekly.tasks = {};

calendar.weekly.get_tasks = function () {
    let last_day_of_week = new Date(this.active_start_day.getFullYear(), 
                                    this.active_start_day.getMonth(), 
                                    this.active_start_day.getDate() + 6);
    
    let start_date = calendar.get_formated_date(this.active_start_day.getDate(), this.active_start_day.getMonth() + 1, this.active_start_day.getFullYear());
    let end_date = calendar.get_formated_date(last_day_of_week.getDate(), last_day_of_week.getMonth() + 1, last_day_of_week.getFullYear());

    
    let tasks_of_week = services.get_tasks_in_interval(start_date, end_date);
    let task, task_runtime, key;
    
    for (let day in tasks_of_week) {
        this.tasks[day] = {};

        for (let hour = 0; hour < 24; hour++)
            this.tasks[day][String(hour).padStart(2, '0')] = [];

        for (let i = 0; i < tasks_of_week[day].length; i++) {
            task = TASKS[tasks_of_week[day][i]];

            task_runtime = task.scheduler_config.start_date;
            key = calendar.get_hour_from_str_datetime(task_runtime);
            
            this.tasks[day][key].push(task);
        }
    }

}

function get_task_title_and_opacity(task, curr_date) {
    let now = get_now(task.scheduler_config.timezone);

    // O único caso em que o next_run não é definido é quando a coleta é agendada para ser executada uma única vez e o horário de início já passou.
    if (task.next_run == null)
        task.next_run = task.scheduler_config.start_date;

    let next_run_date = str_to_date(task.next_run);
    let_next_run_text = get_task_next_run_text(now, next_run_date, task.scheduler_config.timezone);

    let title = '';
    let opacity = 'opacity: 0.5;';

    let past_day = curr_date.getDate() < now.getDate()
        && curr_date.getMonth() == now.getMonth()
        && curr_date.getFullYear() == now.getFullYear();

    if (past_day || next_run_date < now)
        title = 'Coleta executada em: ' + next_run_text + '. \n\nClique para opções.';

    else
        title = 'Coleta agendada para: ' + next_run_text + '. \n\nClique para opções.', opacity = '';

    return [title, opacity];
}

calendar.weekly.get_datetime_tasks = function (week_day, hour) {
    let curr_day = new Date(this.active_start_day.getFullYear(), this.active_start_day.getMonth(), this.active_start_day.getDate() + week_day);
    day = calendar.get_formated_date(curr_day.getDate(), curr_day.getMonth() + 1, curr_day.getFullYear());

    // check if day is in this.tasks
    if (!(day in this.tasks)) 
        return '';  

    let tasks = this.tasks[day][hour];
    let task, task_repr, task_reprs = [], bg_color;
    let num_tasks = tasks.length;

    if (num_tasks > MAX_TASKS) {
        for (let i = 0; i < MAX_TASKS - 1; i++) {
            task = tasks[i];

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

            let [title, opacity] = get_task_title_and_opacity(task, curr_day);

            task_repr = `
                        <div 
                            onclick="show_task_detail(${task.id})" 
                            title="${title}"
                            class="px-2 py-1 ${bg_color} rounded-pill text-white text-container mt-2"
                            style="overflow: hidden; 
                                    white-space: nowrap; 
                                    cursor: pointer;
                                    ${opacity}">
                            <p class="font-weight-bold small m-0 p-0 scroll-text">${task.crawler_name}</p>
                        </div>`;

            task_reprs.push(task_repr);
        }

        let tasks_not_shown = [];
        for (let i = MAX_TASKS - 1; i < num_tasks; i++)
            tasks_not_shown.push(tasks[i].id);
        
        // transforma a data no formato dia/mês/ano
        

        task_repr = `
                    <div 
                        style="cursor: pointer;"
                        onclick="show_more_schedulings([${tasks_not_shown}], '${day}', '${hour}')"
                        class="px-2 py-1 bg-light rounded border border-dark rounded-pill mt-2 text-center">
                        <p class="font-weight-bold small m-0 p-0">+${num_tasks - MAX_TASKS + 1} outras</p>
                    </div>`;

        task_reprs.push(task_repr);
    } else {
        for (let i = 0; i < num_tasks; i++) {
            task = tasks[i];
    
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
            
            let [title, opacity] = get_task_title_and_opacity(task, curr_day);
            
            task_repr = `<div 
                            onclick="show_task_detail(${task.id})" 
                            title="${title}"
                            class="px-2 py-1 ${bg_color} rounded-pill text-white text-container mt-2"
                            style="overflow: hidden; 
                                    white-space: nowrap; 
                                    cursor: pointer;
                                    ${opacity}">
                            <p class="font-weight-bold small m-0 p-0 scroll-text">${task.crawler_name}</p>
                        </div>`;
            task_reprs.push(task_repr);
        }
    }

    return task_reprs.join('\n');
}

calendar.weekly.show = function () {
    this.get_tasks();
    
    // mostra os dias da semana
    let weekdays_cells = ['<div class=""></div>'];

    let i;
    
    let active_year = this.active_start_day.getFullYear();
    let active_month = this.active_start_day.getMonth();
    
    let day, day_repr, days = [], bg_light = '';

    for (i=0;i<7;i++) {
        day = new Date(active_year, active_month, this.active_start_day.getDate() + i);

        let diff_month_css_class = day.getMonth() != calendar.curr_date.getMonth() ? 'no-current-month' : '';

        if (day.toDateString() == calendar.curr_date.toDateString()) 
            day_repr = `<div class="${FLEX_CENTER} h4 rounded-circle border  bg-primary text-white p-0" style="width: 1.9em;height: 1.9em;">
                            ${day.getDate()}
                        </div>`;
        else 
            day_repr = `<div class="${FLEX_CENTER} h4 rounded-circle border ${diff_month_css_class} p-0" style="width: 1.9em;height: 1.9em;">
                            ${day.getDate()}
                        </div>`;

        weekdays_cells.push(`<div class="d-flex justify-content-center">
                                <div class="bg-white">
                                    <h2 class="${FLEX_CENTER} mb-3">
                                        <div class="d-flex align-items-center" style="flex-direction: column;">
                                            <div class="h6 text-muted">
                                                ${WEEKDAYS[i]}
                                            </div>
                                            ${day_repr}
                                        </div>
                                    </h2>
                                </div>
                            </div>`);
                    
        days.push(day);
    }

    this.weekdays_container.empty();
    this.weekdays_container.html(weekdays_cells.join('\n'));
    this.weekdays_container.css('display', 'grid');

    let hour_idx = 0, week_day, hour, tasks_of_hour_html, crawler_queue_behavior;

    let calendar_cells = [];

    for (i=0;i<8 * 24;i++) {
        if (i % 8 == 0) {
            if (bg_light == 'bg-light')
                bg_light = '';

            else
                bg_light = 'bg-light';

            calendar_cells.push(`<div 
                                    id="calendar-weekly-hour-${hour_idx}" 
                                    class="${FLEX_CENTER} text-muted small">
                                    ${HOURS[hour_idx++]}
                                </div>`);
        } else {

            week_day = i % 8 - 1;
            hour = hour_idx - 1;
            
            tasks_of_hour_html = this.get_datetime_tasks(week_day, String(hour).padStart(2, '0'));

            calendar_cells.push(`<div 
                                    id="calendar-weekly-cell-${hour}-${week_day}" 
                                    style="min-height: 8em;"
                                    class="border rounded px-2 pb-2 ${bg_light}">
                                    ${tasks_of_hour_html}
                                </div>`);
        }
    }

    this.days_container.empty();
    this.days_container.html(calendar_cells.join('\n'));
    this.days_container.css('display', 'grid');
    
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

    $(".text-container").hover(
        function () {
            const $this = $(this);
            const $textParagraph = $this.find("p");
            const maxWidth = parseFloat($textParagraph.css("max-width"));
            const fontSize = parseFloat($textParagraph.css("font-size"));
            const realWidth = $textParagraph.width();
            const proportion = realWidth / maxWidth;
            const textLength = $textParagraph.text().length * fontSize;
            const realLength = Math.round(textLength * proportion);

            const animation_time = realLength * 5;

            $this.animate({ scrollLeft: realLength }, animation_time);
        },
        function () {
            const $this = $(this);
            const $textParagraph = $this.find("p");
            const maxWidth = parseFloat($textParagraph.css("max-width"));
            const fontSize = parseFloat($textParagraph.css("font-size"));
            const realWidth = $textParagraph.width();
            const proportion = realWidth / maxWidth;
            const textLength = $textParagraph.text().length * fontSize;
            const realLength = Math.round(textLength * proportion);

            const animation_time = realLength;

            $this.animate({ scrollLeft: 0 }, animation_time);
        }
    );

    this.container.css('display', 'block');
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
calendar.daily.get_tasks = function () {
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
        task = TASKS[task_id];
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
    this.get_tasks();

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
            
            // get_task_title_and_opacity
            const [title, opacity] = get_task_title_and_opacity(task, this.active_day);
            
            tasks_in_hour.push(`
                <div
                    style="cursor: pointer; ${opacity}" 
                    onclick="show_task_detail(${task.id})" 
                    title="${title}"
                    class="${bg_color} text-white rounded-pill px-2 ml-2 mt-2">
                    <p class="m-0 p-0 small font-weight-bold"> ${task.crawler_name} </p>
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
