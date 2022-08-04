
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

var repetion = {
    type: 'daily',
    interval: 1,
    additional_data: null,
    finish: {
        type: 'never',
        additional_data: null
    }
};

var date = new Date();

var repeat_finish_occurrences = 1;
var montly_repeat_value = date.getDate();
var montly_repeat_type = 'day-x';
var repeat_finish_date; 

// calendar
var calendar_mode = null; //daily, weekly, monthly or yearly

function open_new_scheduling() {    
    $('#newScheduling').modal('show');
}

function open_personalized_crawler_repetition() {
    $('#newScheduling').modal('hide');
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
            repetion.additional_data.push(i)
    
    update_repetition_info();
}

function init_default_options() {
    let curr_day = date.getDate();
    let weekday = date.getDay();
    
    $(`#medx-${curr_day}`).attr('selected', 'selected');
    $(`#mfws-${weekday}`).attr('selected', 'selected');
    $(`#mlws-${weekday}`).attr('selected', 'selected');
    $(`#dwr-${weekday}`).click();

    let future_date = new Date()
    future_date.setFullYear(date.getFullYear() + 1);

    let day = date.getDate() < 10 ? `0${future_date.getDate()}` : future_date.getDate();
    let month = (date.getMonth() + 1) < 10 ? `0${future_date.getMonth() + 1}` : future_date.getMonth() + 1;

    let parsed_date = `${day}/${month}/${future_date.getFullYear()}`;
    
    repeat_finish_date = parsed_date;
    montly_repeat_value = curr_day;

    $('#finish-date-in').val(parsed_date);
}

function update_repetition_info() {
    let s = '';
    
    switch (repetion.type) {
        case 'daily':
            if (repetion.interval == 1)
                s = 'Repete diariamente.'
            
            else
                s = `Repete a cada ${repetion.interval} dias.`

            break;
        
        case 'weekly':
            
            if (repetion.additional_data.length > 0) {
                if (repetion.interval == 1)
                    s = 'Repete semanalmente aos/às ';
    
                else 
                    s = `Repete a cada ${repetion.interval} semanas aos/às `

                    let days = [];
                let day_number;
                
                for (let i = 0;i < repetion.additional_data.length;i++) {
                    day_number = repetion.additional_data[i];
                    days.push(day_number_to_weekday[day_number]);
                }
                
                if (days.length == 1)
                    s += days[0] + '.';

                else {
                    for (let i=0;i<days.length-1;i++)
                        s += days[i] + ', '
                    s = s.substring(0, s.length - 2) + ` e ${days[days.length - 1]}.`;

                }

            } else 
                s = 'Repete semanalmente.'

            break
        
        case 'monthly':
            if (repetion.interval == 1)
                s = 'Repete mensalmente ';
            
            else 
                s = `Repete a cada ${repetion.interval} meses `

            switch (repetion.additional_data.type) {
                case 'day-x':
                    s += `no dia ${repetion.additional_data.value}.`;
                    break;
                
                case 'first-weekday':

                    s += `no/na primeiro(a) ${day_number_to_weekday[repetion.additional_data.value]}.`
                    break

                case 'last-weekday':
                    s += `no/na último(a) ${day_number_to_weekday[repetion.additional_data.value]}.`
                    break;

                default:
                    break;
            }

            break

        case 'yearly':
            if (repetion.interval == 1)
                s = 'Repete anualmente.'

            else
                s = `Repete a cada ${repetion.interval} anos.`

            break 
    }

    switch (repetion.finish.type) {
        case 'occurrence':
            s += ` Ocorre ${repetion.finish.additional_data} vezes.`
            break;
        
        case 'date':
            s += ` Ocorre até ${repetion.finish.additional_data}.`
            break;

        default:
            break;
    }

    $('#repetition-info').text(s);
}

function close_personalized_repetition_modal() {
    $('#personalizedCrawlerRepetion').modal('hide');
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

    // $('#newScheduling').modal('show');

    $('#repeat-crawling-select').change(function () {
        let repeat_mode = $(this).val();

        if (repeat_mode == 'custom-repeat') {
            open_personalized_crawler_repetition()
        }
        // console.log($(this).val());
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
                        repetion.additional_data.push(i)                    

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

    $('#finish-date-in').datepicker({
        format: 'dd/mm/yyyy',
        language: 'pt-BR'
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

    update_calendar_mode('daily');
});
