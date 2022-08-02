var weekdays = [
    'Dom.',
    'Seg.',
    'Ter.',
    'Qua.',
    'Qui.',
    'Sex.',
    'Sáb.'
];

var months = [
    'Janeiro',
    'Fevereiro',
    'Março',
    'Abril',
    'Maio',
    'Junho',
    'Julho',
    'Agosto',
    'Setembro',
    'Outubro',
    'Novembro',
    'Dezembro',
]



var JANUARY = 0;
var DECEMBER = 11;

var calendar = {};

calendar.curr_date = calendar.active_date = new Date();

calendar.show = function () {
    let active_year = this.active_date.getFullYear();
    let active_month = this.active_date.getMonth();

    let first_day = new Date(active_year, active_month, 1);
    let last_day = new Date(active_year, active_month + 1, 0);

    let weekday_month_start = first_day.getDay();
    let num_days_previous_month = (new Date(active_year, active_month, 0)).getDate();

    let calendar_cells = [];
    let i;

    for (i=0;i<weekdays.length;i++)
        calendar_cells.push(`<div class="calendar-cell">${weekdays[i]}</div>`);

    i = num_days_previous_month - weekday_month_start + 1;
    for (i;i<=num_days_previous_month;i++)
        calendar_cells.push(`<div class="calendar-cell no-current-month">${i}</div>`);

    for (i=1;i<=last_day.getDate();i++)
        calendar_cells.push(`<div class="calendar-cell">${i}</div>`);

    let diff_until_saturday = 6 - last_day.getDay();
    for (i=1;i<=diff_until_saturday;i++)
        calendar_cells.push(`<div class="calendar-cell no-current-month">${i}</div>`);

    let schedule_calendar = $('#schedule-calendar');
    
    schedule_calendar.empty();

    schedule_calendar.html(calendar_cells.join('\n'))

    $('#curr-date').text(`${months[active_month]} de ${active_year}`)
}


calendar.previous_month = function () {
    let active_year = this.active_date.getFullYear();
    let active_month = this.active_date.getMonth();

    if (active_month == JANUARY)
        active_year--, active_month = DECEMBER;

    else
        active_month--;

    calendar.active_date = new Date(active_year, active_month);

    this.show();
}

calendar.next_month = function () {
    let active_year = this.active_date.getFullYear();
    let active_month = this.active_date.getMonth(); 

    if (active_month == DECEMBER) 
        active_year++, active_month = JANUARY;

    else 
        active_month++;

    calendar.active_date = new Date(active_year, active_month);

    this.show();
}

calendar.today = function () {
    this.active_date = this.curr_date;
    this.show();
}

$(document).ready(function () {
    calendar.show();
});