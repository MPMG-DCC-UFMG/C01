
var el_days_of_week_repeat_option = $('#days-week-repeat-wrapper');
var el_montly_repeat_option = $('#monthly-repeat-wrapper');

var repeat_option_selected = null;

var days_selected_to_repeat = {
    '0': false,
    '1': false,
    '2': false,
    '3': false,
    '4': false,
    '5': false,
    '6': false
};

function new_scheduling_modal() {    
}

function open_personalized_crawler_repetition() {
    console.log('ok, npe')

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
    let weekday = el.getAttribute('weekday');

    days_selected_to_repeat[weekday] = !days_selected_to_repeat[weekday];

    if (days_selected_to_repeat[weekday]) {
        el.classList.remove('text-muted', 'bg-white');
        el.classList.add('text-white', 'bg-primary');
    } else {
        el.classList.remove('text-white', 'bg-primary');
        el.classList.add('text-muted', 'bg-white');
    }
}

function init_default_options() {
    let date = new Date();

    let curr_day = date.getDate();
    let weekday = date.getDay();
    
    $(`#medx-${curr_day}`).attr('selected', 'selected');
    $(`#mfws-${weekday}`).attr('selected', 'selected');
    $(`#mlws-${weekday}`).attr('selected', 'selected');
    $(`#dwr-${weekday}`).click();

    date.setFullYear(date.getFullYear() + 1);

    let day = date.getDate() < 10 ? `0${date.getDate()}` : date.getDate();
    let month = date.getMonth() < 10 ? `0${date.getMonth()}` : date.getMonth();

    let parsed_date = `${date.getFullYear()}-${month}-${day}`;
    $('#finish-date-in').val(parsed_date);
    
    console.log(parsed_date);

    // console.log($('#finish-date-in').val(), parsed_date)
    
    // .val(parsed_date);
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

    $('#personalizedCrawlerRepetion').modal('show');

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
                show_days_of_week_repeat_options();
                break;
        
            case 'monthly':
                show_monthly_repeat_options();
                break;
        }

        repeat_option_selected = repeat_mode;
    });

    init_default_options();
});