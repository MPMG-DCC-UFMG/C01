/* Collapse div */

function mycollapse(target){
    var el = $(target);
    
    if(el.hasClass("myshow"))
        el.removeClass("myshow");
    else
        el.addClass("myshow");
}

/* End collapse div */

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
    var valid =
      validateTextInput("id_source_name") &&
      validateTextInput("id_base_url") &&
      validateTextInput("id_data_path");
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
    // console.log("id_antiblock_mask_type", selected_option);
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

function checkInjectionForms(prefix) {
    var valid = true;

    // Parameter configurations
    $('#' + prefix + '_param .param-step:not(.subform-deleted) input')
        .each((index, entry) => {
        valid = valid && entry.checkValidity();
    });

    // Validate ordering constraints between fields
    $('#' + prefix + '_param .param-step:not(.subform-deleted)')
        .each((index, entry) => {
        entry = $(entry);

        let param_type = entry.find('select[name$="parameter_type"]').val();

        let error_msg = ""
        if (param_type == 'process_code') {
            let first_year = entry.find('input[name$="first_year_proc_param"]');
            let last_year = entry.find('input[name$="last_year_proc_param"]');

            let first_value = parseInt(first_year.val());
            let last_value = parseInt(last_year.val());

            if (first_year.val() != "" && last_year.val() != "" &&
                first_value > last_value) {
                valid = false;
                error_msg = 'O primeiro ano deve ser menor que o último.'
            }
            first_year[0].setCustomValidity(error_msg);
            last_year[0].setCustomValidity(error_msg);
        } else if (param_type == 'number_seq'){
            let first_num = entry.find('input[name$="first_num_param"]');
            let last_num = entry.find('input[name$="last_num_param"]');

            let first_value = parseInt(first_num.val());
            let last_value = parseInt(last_num.val());

            if (first_num.val() != "" && last_num.val() != "" &&
                first_value > last_value) {
                valid = false;
                error_msg = 'O primeiro número deve ser menor que o último.'
            }
            first_num[0].setCustomValidity(error_msg);
            last_num[0].setCustomValidity(error_msg);
        } else if (param_type == 'date_seq'){
            let first_date = entry.find('input[name$="start_date_date_param"]');
            let last_date = entry.find('input[name$="end_date_date_param"]');

            let first_value = new Date(first_date.val());
            let last_value = new Date(last_date.val());

            if (first_date.val() != "" && last_date.val() != "" &&
                first_value > last_value) {
                valid = false;
                error_msg = 'A primeira data deve ser menor que a última.'
            }
            first_date[0].setCustomValidity(error_msg);
            last_date[0].setCustomValidity(error_msg);
        }
    });

    return valid;
}

function checkResponseValidationForms(prefix) {
    var valid = true;

    // Response validation configurations
    $('#' + prefix + '_response .resp-step:not(.subform-deleted) input')
        .each((index, entry) => {
        valid = valid && entry.checkValidity();
    });

    return valid;
}

function checkTemplatedURL() {
    var valid = true;

    valid = checkInjectionForms('templated_url');

    valid = valid && checkResponseValidationForms('templated_url')

    defineIcon("templated_url", valid);
}

function checkStaticForm() {
    var valid = true;

    valid = checkInjectionForms('static_form');

    valid = valid && checkResponseValidationForms('static_form')

    defineIcon("static_form", valid);
}

function updateInjectionFields(prefix) {
    // Update information for selected parameters/response handlers
    $('#' + prefix + '_param .param-step > .form-group select').each(
        (index, entry) => detailParamType({ 'target': entry})
    );

    $('#' + prefix + '_response .resp-step > .form-group select').each(
        (index, entry) => detailResponseType({ 'target': entry})
    );

    // Update range-filtering sub-parameters
    $('#' + prefix + '_param .filter-config > .form-group input').each(
        (index, entry) => detailParamFilter({'target': entry})
    );
}

function checkRelatedFields() {
    var input_name = $(this).attr('name');

    if (input_name == "import_settings")
        return;

    if (input_name.length >= 11 && input_name.substring(0, 10) == "antiblock_") {
        checkAntiblock();
    }

    if (input_name.length >= 13 && input_name.substring(0, 13) == "templated_url") {
        checkTemplatedURL();
    }

    if (input_name.length >= 11 && input_name.substring(0, 11) == "static_form") {
        checkStaticForm();
    }

    // TODO: make all variables from same section have the same prefix and check like antiblock
    switch (input_name) {
        case 'source_name':
        case 'base_url':
        case 'data_path':
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
        case 'link_extractor_max_depth':
        case 'link_extractor_allow':
        case 'link_extractor_allow_extensions':
            checkCrawlerType();
            break;
    }
}

$(document).ready(function () {
    setNavigation();
    $('input').on('blur keyup', checkRelatedFields);
    $('#collapse-adv-links').on("click", function () { mycollapse("#adv-links");})
    $('#collapse-adv-download').on("click", function () { mycollapse("#adv-download"); })
    updateInjectionFields('static_form');

});

function showBlock(clicked_id) {
    console.log(clicked_id);
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

function detailBaseUrl() {
    const base_url = $("#id_base_url").val();

    // Check if a Templated URL is being used (if there is at least one
    // occurrence of the substring "{}")
    if (base_url.includes("{}")){
        $("#templated_url-item").removeClass("disabled");
        // count number of placeholders
        let num_placeholders = (base_url.match(/\{\}/g) || []).length;
        $('#templated_url_param').formset('setNumForms', num_placeholders);
    } else {
        $("#templated_url-item").addClass("disabled");

        // remove all parameter and response forms
        $('#templated_url_param').formset('setNumForms', 0);
        $('#templated_url_response').formset('setNumForms', 0);
    }

    updateInjectionFields('templated_url');

    checkTemplatedURL();
}

function loadStaticForm() {
    const base_url = $("#id_base_url").val();
    const req_type = $("#id_request_type").val();

    // Clear form before updating
    $('#static_form_param').formset('setNumForms', 0);

    // Load Templated URL info
    let url_params = $("#templated_url_param .param-step:not(.subform-deleted)")
        .map((_, el) => {
        let inputs = $(el).find(":input");
        let data = {};

        inputs.each((_, input) => {
            let input_name = $(input).attr('name')
                .replace(/templated_url-params-\d+-/, "");
            data[input_name] = $(input).val();

            if ($(input).is(':checkbox')) {
                data[input_name] = input.checked
            }
        });

        return data;
    }).toArray();

    let url_responses = $("#templated_url_response .resp-step:not(.subform-deleted)")
        .map((_, el) => {
        let inputs = $(el).find(":input");
        let data = {};

        inputs.each((_, input) => {
            let input_name = $(input).attr('name')
                .replace(/templated_url-responses-\d+-/, "");
            data[input_name] = $(input).val();

            if ($(input).is(':checkbox')) {
                data[input_name] = input.checked
            }
        });

        return data;
    }).toArray();

    // Use the field detection module to load the fields
    $.ajax('/info/form_fields', {
        data: {
            'base_url': base_url,
            'req_type': req_type,
            'url_param_data': JSON.stringify(url_params),
            'url_response_data': JSON.stringify(url_responses)
        },
        success: (data) => {
            $('#static_form_param').formset('setNumForms', parseInt(data['length']));
            let currLabel = 0;

            for (i in data['names']) {
                let form = $('#static_form_param .param-step:not(.subform-deleted):nth(' + i + ')');

                let key_input = form.find('input[id$="parameter_key"]');
                let label_input = form.find('input[id$="parameter_label"]');
                let type_input = form.find('select[id$="parameter_type"]');

                key_input.val(data['names'][i]);
                if (data['types'][i] != 'hidden') {
                    label_input.val(data['labels'][currLabel]);
                    currLabel++;
                }
                switch (data['types'][i]) {
                    case "number":
                        type_input.val('number_seq').change();
                        break;
                    case "text":
                        type_input.val('alpha_seq').change();
                        break;
                    case "number":
                        type_input.val('date_seq').change();
                        break;
                }
            }
        },
        complete: () => {
            updateInjectionFields('static_form');

            checkStaticForm();
        }
    });
}

function detailWebdriverType() {
    setHiddenState("webdriver_path_div", !getCheckboxState("id_has_webdriver"));
}

function detailDynamicProcessing() {
    dynamic_processing_block = document.getElementById("dynamic-processing-item")
    if(getCheckboxState("id_dynamic_processing")){
        dynamic_processing_block.classList.remove("disabled")
    }else{
        dynamic_processing_block.classList.add("disabled")
    }
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

function hideUnselectedSiblings(input, parentPath, siblingPath) {
    const parentDiv = $(input).closest(parentPath);
    const selectedVal = input.options[input.selectedIndex].value;

    parentDiv.find(siblingPath).each(function() {
        this.hidden = true;
    });

    if (selectedVal != "") {
        parentDiv.find("[data-option-type=" + selectedVal + "]")
                 .attr('hidden', false);
    }

    // Remove 'required' constraint from all inputs for this parameter
    $(input).closest(parentPath)
            .find(siblingPath + ' input:not([type="checkbox"])')
            .removeAttr('required');

    const paramType = input.options[input.selectedIndex].value

    if (paramType != "") {
        // Add 'required' constraint to inputs for this parameter type
        $(input).closest(parentPath)
                .find(siblingPath + '[data-option-type=' + paramType + '] ' +
                                    'input:not([type="checkbox"])')
                .attr('required', '');
    }
}

function detailResponseType(e) {
    hideUnselectedSiblings(e.target, '.resp-step:not(.subform-deleted)',
        '.response-params');

    // Update form validations
    checkStaticForm(); checkTemplatedURL();
}

function detailParamType(e) {
    const input = e.target;
    hideUnselectedSiblings(e.target, '.param-step:not(.subform-deleted)',
        '.param-config');

    const filterDiv = $(input).closest('.param-step')
                              .find('.filter-config')[0];

    switch (input.options[input.selectedIndex].value) {
        case 'process_code':
        case 'number_seq':
        case 'date_seq':
            // Display filtering options
            filterDiv.hidden = false
            break;
        default:
            // Hide filtering options
            filterDiv.hidden = true
    }

    // Update cons_misses parameter
    const filterCheckbox = $(filterDiv).find('> .form-group input')[0]
    detailParamFilter({ 'target':  filterCheckbox })

    // Update form validations
    checkStaticForm(); checkTemplatedURL();
}

function detailParamFilter(e) {
    const input = e.target;
    const consMissesInput = $(input).closest(".param-step")
         .find('.cons-misses')[0]
    consMissesInput.hidden = !input.checked
    $(consMissesInput).find('input').prop('required', input.checked)

    // Update form validations
    checkStaticForm(); checkTemplatedURL();
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

// function detailCrawlerType() {
//     var mainSelect = document.getElementById("id_crawler_type");
//     const crawler_type = mainSelect.options[mainSelect.selectedIndex].value;

//     var contents = document.getElementsByClassName("crawler-type-content-div");
//     for (const i in contents)
//         contents[i].hidden = true;
//     setHiddenState(crawler_type, false);
    

//     if(crawler_type == "form_page"){
//         interface_root_element = document.getElementById("form_page");
//         if(interface_root_element.type != "root" ){
            
//             steps_output_element = interface_root_element.children[0].children[1].children[0]
//             load_steps_interface(interface_root_element, steps_output_element);
//         }
//     }

//     checkCrawlerType();
// }


function autothrottleEnabled() {
    setHiddenState("autothrottle-options-div", !getCheckboxState("id_antiblock_autothrottle_enabled"));
}

const table_input = document.querySelectorAll(".dynamic_input_table")

table_input.forEach(input => input.addEventListener('change', getExtraParsingConfig));

function getExtraParsingConfig(e) {
  var table_match = document.getElementsByName("table_match")[0].value;
  var table_flavor = document.getElementsByName("table_flavor")[0].value;
  var table_header = document.getElementsByName("table_header")[0].value;
  var table_index_col = document.getElementsByName("table_index_col")[0].value;
  var table_skiprows = document.getElementsByName("table_skiprows")[0].value;
  var table_attributes = document.getElementsByName("table_attributes")[0].value;
  var table_parse_dates = document.getElementsByName("table_parse_dates")[0].value;
  var table_thousands = document.getElementsByName("table_thousands")[0].value;
  var table_enconding = document.getElementsByName("table_enconding")[0].value;
  var table_decimal = document.getElementsByName("table_decimal")[0].value;
  var table_na_values = document.getElementsByName("table_na_values")[0].value;
  var table_keep_default_na = document.getElementsByName("table_keep_default_na")[0].value;
  var table_displayed_only = document.getElementsByName("table_displayed_only")[0].value;

  var dict = {
              'table_match': table_match,
              'table_flavor':table_flavor,
              'table_header':table_header,
              'table_index_col':table_index_col,
              'table_skiprows':table_skiprows,
              'table_attributes':table_attributes,
              'table_parse_dates':table_parse_dates,
              'table_thousands':table_thousands,
              'table_enconding':table_enconding,
              'table_decimal':table_decimal,
              'table_na_values':table_na_values,
              'table_keep_default_na':table_keep_default_na,
              'table_displayed_only':table_displayed_only
            };

  var table_attrs_hidden = document.getElementById("table_attrs_hidden");
  var dict_string = JSON.stringify(dict);
  table_attrs_hidden.value = dict_string;
}

// Import colector

function processCheckBoxInput(data) {
    // Converts checkbox entries in the json file to the html form

    let checkbox_input, checkbox_input_id;
    $('input[type=checkbox]').each(function () {
        checkbox_input = $(this);
        checkbox_input_id = checkbox_input.attr('id');
        if (checkbox_input_id) {
            checkbox_input_id = checkbox_input_id.replace('id_', '');
            if (checkbox_input_id in data)
                // Use the .click() method instead of directly changing the
                // checked value so that the correct events are triggered
                if (data[checkbox_input_id] != checkbox_input.prop('checked'))
                    checkbox_input.click();
        }
    });
}

function processInput(input_selector, data) {
    let input, input_id;
    $(input_selector).each(function () {
        input = $(this);
        input_id = input.attr('id');
        if (input_id) {
            input_id = input_id.replace('id_', '');
            if (input_id in data)
                input.val(data[input_id]);
        }
    });
}

function processInjectionForms(data, prefix, updateNumParams=false) {
    // Loads the specified injector data from the configuration

    let num_params = data[prefix + "_parameter_handlers"].length;
    let num_validators = data[prefix + "_response_handlers"].length;

    if (updateNumParams) {
        // Updates the number of parameters in the form
        $('#' + prefix + '_param').formset('setNumForms', num_params);
    }
    // Updates the number of validators in the form
    $('#' + prefix + '_response').formset('setNumForms', num_validators);

    // Create a new data object to match with the injector parameter ids
    let new_data = {};
    for (let i = 0; i < num_params; i++) {
        let param = data[prefix + "_parameter_handlers"][i];
        for (let key in param) {
            new_data[prefix + "-params-" + i + "-" + key] = param[key];
        }
    }
    for (let i = 0; i < num_validators; i++) {
        let param = data[prefix + "_response_handlers"][i];
        for (let key in param) {
            new_data[prefix + "-responses-" + i + "-" + key] = param[key];
        }
    }

    // Re-run the processing with only the injector config data
    processSettings(new_data);
}

function processParameterizedURL(data) {
    // Loads the parameterized URL data from the configuration

    // Updates the parameterized URL section based on the URL
    detailBaseUrl();

    // Process the forms
    processInjectionForms(data, 'templated_url');

    // Re-updates the parameterized URL section (used to refresh sub-options
    // based on select values and remove/add the "required" attribute)
    detailBaseUrl();
}

function processStaticForms(data) {
    // Loads the form injector data from the configuration

    // Process the forms
    processInjectionForms(data, 'static_form', true);

    // Re-updates the static form section (used to refresh sub-options
    // based on select values and remove/add the "required" attribute)
    updateInjectionFields('static_form');
    checkStaticForm();
}

function processParsing(data) {
    // When the configuration is to not save csv, the field checked below is null
    if (!data["table_attrs"])
        return;

    let parsing_data = JSON.parse(data["table_attrs"]);

    let parsing_input, parsing_input_name;
    $('#parsing-item-block input').each(function () {
        parsing_input = $(this);
        parsing_input_name = parsing_input.attr('name');
        if (parsing_input_name) {
            if (parsing_input_name in parsing_data) {
                if(this.type == "checkbox") {
                    let bool_value = String(parsing_data[parsing_input_name])
                                        .toLowerCase() == "true";

                    // Use the .click() method instead of directly changing the
                    // checked value so that the correct events are triggered
                    if (bool_value != parsing_input.prop('checked'))
                        parsing_input.click();
                } else {
                    parsing_input.val(parsing_data[parsing_input_name]);
                }
            }
        }
    });

    getExtraParsingConfig();
}

function processSettings(data) {
    // Converts the settings of the json file into
    // parameters of the creation form
    processCheckBoxInput(data);

    processInput('select', data);
    processInput('input[type=text]', data);
    processInput('input[type=number]', data);
    processInput('input[type=date]', data);
    processInput('textarea', data);
}

function parseSettings(e) {
    const file = e.files[0];

    const reader = new FileReader();
    reader.addEventListener('load', (event) => {
        // configuratiion file parsing
        const result = event.target.result;
        const data = JSON.parse(result);

        processSettings(data);
        processParameterizedURL(data);
        processStaticForms(data);
        processParsing(data);

        // checks if the settings are valid
        checkBasicInfo();
        checkAntiblock();
        checkCaptcha();
        checkCrawlerType();
        checkTemplatedURL();
        checkStaticForm();

        // go to the option that allows the user to change the location
        // saving downloaded files
        showBlock('basic-info-item');
        $('#id_data_path').focus();
    });

    reader.readAsText(file);
}