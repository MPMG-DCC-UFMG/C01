function enableCreateButton() {
    var blocks = document.getElementsByClassName('valid-icon');
    var isValid = true;
    for (var i = 0; i < blocks.length; i++) {
        if (blocks[i].classList.contains('fa-warning')) {
            isValid = false;
            break;
        }
    }

    var button = document.getElementById('createButton');
    if (button.classList.contains('list-group-item-valid') && !isValid) {
        button.classList.remove('list-group-item-valid');
        button.classList.add('list-group-item-invalid');
    } else if (isValid) {
        button.classList.remove('list-group-item-invalid');
        button.classList.add('list-group-item-valid');
    }
}

function submit() {
    document.getElementById("myForm").submit();
}

function defineIcon(section, isValid) {
    var sectionId = '#' + section + '-valid-icon';
    if (isValid) {
        $(sectionId).removeClass('fa-warning').addClass('fa-check');
    } else {
        $(sectionId).removeClass('fa-check').addClass('fa-warning');
    }
    enableCreateButton();
}

function validateIntegerInput(input_id, can_be_empty = true, can_be_negative = false) {
    if (can_be_empty && can_be_negative) return true;

    var input = document.getElementById(input_id);
    var empty = !Boolean(input.value.trim())

    if (empty) return can_be_empty;

    var value = parseInt(input.value);
    return (value > 0 || can_be_negative);
}

function validateTextInput(input_id) {
    return document.getElementById(input_id).value.length > 0;
}

function getCheckboxState(checkbox_id) {
    return document.getElementById(checkbox_id).checked;
}

function getSelectedOptionText(select_id) {
    var select = document.getElementById(select_id);
    return select.options[select.selectedIndex].text;
}

function getSelectedOptionValue(select_id){
    var select = document.getElementById(select_id);
    return select.options[select.selectedIndex].value;
}

function setHiddenState(element_id, hidden) {
    document.getElementById(element_id).hidden = hidden;
}

function checkBasicInfo() {
    var valid = validateTextInput('id_source_name') && validateTextInput('id_base_url');
    defineIcon("basic-info", valid);
}

function checkAntiblock() {
    var valid = true;
    valid = (
        valid &&
        validateIntegerInput('id_antiblock_download_delay', can_be_empty = false, can_be_negative = false)
    );

    if (getCheckboxState('id_antiblock_autothrottle_enabled')) {
        valid = (
            valid &&
            validateIntegerInput('id_antiblock_autothrottle_start_delay', can_be_empty = false, can_be_negative = false) &&
            validateIntegerInput('id_antiblock_autothrottle_max_delay', can_be_empty = false, can_be_negative = false)
        );
    }

    var selected_option = getSelectedOptionValue("id_antiblock_mask_type");
    console.log("id_antiblock_mask_type", selected_option);
    if (selected_option == 'ip') {
        valid = (
            valid &&
            validateIntegerInput('id_antiblock_max_reqs_per_ip', can_be_empty = false, can_be_negative = false) &&
            validateIntegerInput('id_antiblock_max_reuse_rounds', can_be_empty = false, can_be_negative = false)
        );

        var selected_proxy = getSelectedOptionText("id_antiblock_mask_type");
        if (selected_proxy == "proxy")
            valid = validateTextInput('id_proxy_list');
    }
    else if (selected_option == 'user_agent') {
        valid = (
            validateIntegerInput('id_antiblock_reqs_per_user_agent', can_be_empty = false, can_be_negative = false) &&
            validateIntegerInput('id_antiblock_user_agents_file', can_be_empty = false, can_be_negative = false)
        );
    }
    else if (selected_option == 'cookies') {
        valid = validateTextInput('id_antiblock_cookies_file');
    }

    defineIcon("antiblock", valid);
}

function checkCaptcha() {
    var valid = true;

    if (getCheckboxState("id_has_webdriver"))
        valid = valid && validateTextInput("id_webdriver_path");

    var selected_option = getSelectedOptionValue("id_captcha");

    if (selected_option == 'image')
        valid = validateTextInput('id_img_xpath');
    else if (selected_option == 'sound')
        valid = validateTextInput('id_sound_xpath');

    defineIcon("captcha", valid);
}

function checkCrawlerType() {
}

$(document).ready(function () {
    setNavigation();

    $('input').on('blur keyup', function () {
        var input_name = $(this).attr('name');

        if (input_name.length >= 11 && input_name.substring(0, 10) == "antiblock_") {
            checkAntiblock();
        }
        // TODO: make all variables from same section have the same prefix and check like antiblock
        switch (input_name) {
            case 'source_name':
            case 'base_url':
                checkBasicInfo();
                break;
            case 'has_webdriver':
            case 'webdriver_path':
            case 'img_xpath':
            case 'sound_xpath':
                checkCaptcha();
                break;
            case 'crawler_type':
            case 'explore_links':
            case 'link_extractor_max_depht':
            case 'link_extractor_allow':
            case 'link_extractor_allow_extensions':
                checkCrawlerType();
                break;
        }
    });
});

function showBlock(clicked_id) {

    var blocks = document.getElementsByClassName('block');
    for (var i = 0; i < blocks.length; i++)
        blocks[i].setAttribute('hidden', true);

    var blockId = clicked_id + "-block";
    var block = document.getElementById(blockId);
    block.removeAttribute('hidden');


    var buttons = document.getElementsByClassName('button-block');
    for (var i = 0; i < buttons.length; i++)
        buttons[i].classList.remove('active');
    document.getElementById(clicked_id).classList.add('active');
}

function detailWebdriverType() {
    setHiddenState("webdriver_path_div", !getCheckboxState("id_has_webdriver"));
}

function detailCaptcha() {
    var mainSelect = document.getElementById("id_captcha");
    const captcha_type = mainSelect.options[mainSelect.selectedIndex].value;

    setHiddenState('webdriver', captcha_type == 'none' ? true : false);

    var contents = document.getElementsByClassName("captcha-content-div");
    for (const i in contents)
        contents[i].hidden = true;
    setHiddenState(captcha_type, false);

    checkCaptcha();
}

function detailTemplatedUrlRequestType() {
    var mainSelect = document.getElementById("id_templated_url_type");
    const request_type = mainSelect.options[mainSelect.selectedIndex].value;

    var contents = document.getElementsByClassName("templated-url-content-div");
    for (const i in contents)
        contents[i].hidden = true;
    setHiddenState(request_type, false);
}

function detailIpRotationType() {
    var ipSelect = document.getElementById("id_ip_type");

    const ip_rotation_type = ipSelect.options[ipSelect.selectedIndex].value;

    setHiddenState("tor_div", true);
    setHiddenState("proxy_div", true);

    var id = ip_rotation_type + "_div";
    setHiddenState(id, false);
}

function detailAntiblock() {
    var mainSelect = document.getElementById("id_antiblock_mask_type");
    const antiblock_type = mainSelect.options[mainSelect.selectedIndex].value;

    var contents = document.getElementsByClassName("antiblock-mask-div");
    for (const i in contents)
        contents[i].hidden = true;
    setHiddenState(antiblock_type, false);

    checkAntiblock();
}

function detailCrawlerType() {
    var mainSelect = document.getElementById("id_crawler_type");
    const crawler_type = mainSelect.options[mainSelect.selectedIndex].value;

    var contents = document.getElementsByClassName("crawler-type-content-div");
    for (const i in contents)
        contents[i].hidden = true;
    setHiddenState(crawler_type, false);
    


    var outside_element = document.getElementById("form_page");
    if(outside_element.type != "steps_creation_interface" ){
        //outside_element.children[0].hidden = true
        steps_output_element = outside_element.children[0].children[1].children[0]
        load_steps(outside_element, steps_output_element);
        outside_element.type = "steps_creation_interface" 
    }

    checkCrawlerType();
}

function autothrottleEnabled() {
    setHiddenState("autothrottle-options-div", !getCheckboxState("id_antiblock_autothrottle_enabled"));
}

// Create steps
// TODO add new fields to validation 