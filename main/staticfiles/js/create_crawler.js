// 
var selected_proxy = "tor";

function setIpRotationType() {
    $('#id_antiblock_ip_rotation_type').val(selected_proxy);
}

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
        $(sectionId).removeClass('fa-exclamation-triangle text-warning').addClass('fa-check');
    } else {
        $(sectionId).removeClass('fa-check').addClass('fa-exclamation-triangle text-warning');
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

function validateTextInputsByName(input_name) {
    let elements = document.getElementsByName(input_name);
    let valid = true;
    for(let i=0; i<elements.length; i++) {
        if(elements[i].value.length == 0) {
            valid = false;
            break
        }
    }
    return valid
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
      validateTextInputsByName("source_name") &&
      validateTextInputsByName("base_url") &&
      validateTextInputsByName("data_path");
    defineIcon("basic-info", valid);
}

function checkAntiblock() {
    var valid = true;

    valid = validateIntegerInput('id_antiblock_download_delay', can_be_empty = false, can_be_negative = false);

    if (getCheckboxState('id_antiblock_autothrottle_enabled')) {
        valid = (
            validateIntegerInput('id_antiblock_autothrottle_start_delay', can_be_empty = false, can_be_negative = false) &&
            validateIntegerInput('id_antiblock_autothrottle_max_delay', can_be_empty = false, can_be_negative = false)
        );
    }

    if (getCheckboxState("id_antiblock_ip_rotation_enabled")) {
        if (selected_proxy === "tor") {
            valid = (
                validateIntegerInput('id_antiblock_max_reqs_per_ip', can_be_empty = false, can_be_negative = false) &&
                validateIntegerInput('id_antiblock_max_reuse_rounds', can_be_empty = false, can_be_negative = false)
            );

        } else
            valid = validateTextInput('id_antiblock_proxy_list');
    }

    if (getCheckboxState("id_antiblock_user_agent_rotation_enabled")) {
        valid = (
            validateIntegerInput('id_antiblock_reqs_per_user_agent', can_be_empty = false, can_be_negative = false) &&
            validateTextInput('id_antiblock_user_agents_list')
        );
    }

    if (getCheckboxState("id_antiblock_insert_cookies_enabled")) {
        valid = validateTextInput('id_antiblock_cookies_list');
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
    console.log(input_name)

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

function initIpRotationTabs() {
    if ($('#id_antiblock_ip_rotation_type').val() === 'proxies') {
        selected_proxy = 'proxies';
        
        $('#tor').removeClass('active');
        $('#ip-nav').removeClass('show active');

        $('#proxies').addClass('active');
        $('#proxies-nav').addClass('show active');

    } else
        setIpRotationType();
}

$(document).ready(function () {
    setNavigation();
    initIpRotationTabs();

    // Responsible for identifying which IP rotation mechanism to use: Tor or proxy list.
    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        selected_proxy = $(e.target).attr('id');
        
        setIpRotationType();
        checkAntiblock();
    });

    // $('input, textarea').on('blur keyup change', checkRelatedFields);
    $(document.body).on('blur keyup change', 'input, textarea', checkRelatedFields);
    $('#collapse-adv-links').on("click", function () { mycollapse("#adv-links");})
    $('#collapse-adv-download').on("click", function () { mycollapse("#adv-download"); })
    updateInjectionFields('static_form');

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


    //Editar aqui futuramete. É necessário uma estrutura
    //mais geral para as funções do tipo detail já que ao
    //editar um coletor e navegar pelas abas, o showblock
    //é chamado mostrando apenas as suas paginas iniciais.
    if (clicked_id == "crawler-type-item"){
        detailCrawlerType();
    }
}

function detailBaseUrl() {
    const base_url = $("[name=base_url]").val();

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
    const base_url = $("[name=base_url]").val();
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

    // Display the form selection modal
    $("#form_detection_modal").modal('show');
    $("#form_detection_modal .modal-body .spinner-border").parent().show();
    $("#form_detection_modal .modal-body .form_list").hide();

    // Use the field detection module to load the fields
    $.ajax('/info/form_fields', {
        data: {
            'base_url': base_url,
            'req_type': req_type,
            'url_param_data': JSON.stringify(url_params),
            'url_response_data': JSON.stringify(url_responses)
        },
        success: (data) => {
            displayDetectedForms(data['forms']);
        },
        error: (xhr) => {
            displayFormsError(xhr.responseJSON['error']);
        },
        complete: () => {
            updateInjectionFields('static_form');

            checkStaticForm();
        }
    });
}

function fillFormFields(form_data) {
    // Set the request method
    $('#id_form_request_type').val(form_data['method'])

    $('#static_form_param').formset('setNumForms',
        parseInt(form_data['length']));

    for (i in form_data['names']) {
        let form = $(`#static_form_param ` +
            `.param-step:not(.subform-deleted):nth(${i})`);

        let key_input = form.find('input[id$="parameter_key"]');
        let label_input = form.find('input[id$="parameter_label"]');
        let type_input = form.find('select[id$="parameter_type"]');

        key_input.val(form_data['names'][i]);
        if (form_data['types'][i] != 'hidden') {
            label_input.val(form_data['labels'][i]);
        }
        switch (form_data['types'][i]) {
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
}

function displayFormsError(error) {
    let modal_body = $("#form_detection_modal .modal-body");

    // Hide confirmation button
    $('#form_detection_modal .include_fields').hide();

    // Hide spinner
    modal_body.find(".spinner-border").parent().hide();

    // Display error
    let form_list_el = modal_body.find(".form_list");
    form_list_el.empty();
    modal_body.find(".form_list").append(
        $(`<div class="text-center col"><p>${error}</p></div>`)
    );
    form_list_el.show();
}

function displayDetectedForms(forms_list) {

    let modal_body = $("#form_detection_modal .modal-body");
    modal_body.find(".spinner-border").parent().hide();

    let form_list_el = modal_body.find(".form_list");
    form_list_el.empty();
    form_list_el.show();

    // Display confirmation button
    $('#form_detection_modal .include_fields').show();

    for (let i in forms_list) {
        let form = forms_list[i];

        let form_element = $("<div class='form_detection_el'></div>");

        form_element.append($(`<input type='radio' id='form${i}' value='${i}'
            name='form_choice'>
            </input>`));
        form_element.append($(`<label for='form${i}'>
            Formulário ${parseInt(i) + 1} <i>(método: `+
            `${form['method'].toUpperCase()})</i>
        </label>`));

        // Add radio button change event
        form_element.find(`#form${i}`).change(function (e) {
            let form_index = parseInt(e.target.value);

            // Uncheck and disable fields from other forms
            $(`#form_detection_modal input[type="checkbox"]`+
            `:not([data-form-index="${form_index}"])`)
                .prop('checked', false)
                .prop( "disabled", true);

            // Check and enable fields from this form
            $(`#form_detection_modal input[type="checkbox"]`+
            `[data-form-index="${form_index}"]`)
                .prop('checked', true)
                .prop( "disabled", false);
        });

        for (let j = 0; j < parseInt(form['length']); j++) {
            let field_element = $(`<div class='form_input_el
                form_indented row'></div>`);
            let field = {
                'name': form['names'][j],
                'type': form['types'][j],
                'label': form['labels'][j]
            };

            let field_description = `${field['name']} <i>(`;
            field_description += `tipo: ${field['type']}`;
            if (field['label'] && field['label'].length > 0) {
                field_description += `, descrição: ${field['label']}`;
            }
            field_description += ')</i>'

            field_element.append($(`<input type='checkbox'
                id='form${i}_field${j}' data-form-index='${i}'
                data-field-index='${j}'>
                </input>`));
            field_element.append($(`<label for='form${i}_field${j}'
                class='form_field_label'>
                ${field_description}
            </label>`));

            form_element.append(field_element)
        }

        form_list_el.append(form_element);
    }

    // Select the first radio button to avoid an undefined state
    $('#form_detection_modal input#form0').prop('checked', true).change();

    // Enable the button to include the fields
    $('#form_detection_modal .include_fields').click(function() {
        let el = $('#form_detection_modal input[name="form_choice"]:checked');
        let form_index = 0;
        if (el) form_index = parseInt(el.val());

        let selected_form = forms_list[form_index];

        let field_indices = $(`#form_detection_modal input[type="checkbox"]`+
            `[data-form-index="${form_index}"]:checked`)
        .map((_, el) =>
            parseInt(el.getAttribute('data-field-index'))
        ).toArray();

        // Filter selected fields only
        selected_form['length'] = field_indices.length;
        selected_form['names'] = selected_form['names'].filter((_, i) =>
            field_indices.includes(i)
        );
        selected_form['types'] = selected_form['types'].filter((_, i) =>
            field_indices.includes(i)
        );
        selected_form['labels'] = selected_form['labels'].filter((_, i) =>
            field_indices.includes(i)
        );

        fillFormFields(selected_form);

        $('#form_detection_modal').modal('hide');
    });
}

function detailWebdriverType() {
    setHiddenState("webdriver_path_div", !getCheckboxState("id_has_webdriver"));
}

function detailDynamicProcessing() {
    dynamic_processing_check = document.getElementById("dynamic-processing-valid-icon")
    dynamic_processing_block = document.getElementById("dynamic-processing-item-wrap")
    dynamic_processing_skip_errors = document.getElementById("dynamic-processing-skip-errors")
    if(getCheckboxState("id_dynamic_processing")){
        dynamic_processing_check.classList.remove("disabled")
        dynamic_processing_block.classList.remove("disabled")
        dynamic_processing_skip_errors.classList.remove("disabled")
    }else{
        dynamic_processing_check.classList.add("disabled")
        dynamic_processing_block.classList.add("disabled")
        dynamic_processing_skip_errors.classList.add("disabled")
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

function detailAntiblock() {
    var mainSelect = document.getElementById("id_antiblock_mask_type");
    const antiblock_type = mainSelect.options[mainSelect.selectedIndex].value;

    var contents = document.getElementsByClassName("antiblock-mask-div");
    for (const i in contents)
        contents[i].hidden = true;
    setHiddenState(antiblock_type, false);

    checkAntiblock();
}

function autothrottleEnabled() {
    setHiddenState("autothrottle-options-div", !getCheckboxState("id_antiblock_autothrottle_enabled"));
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

function ipRotationEnabled() {
    setHiddenState("ip-rotation-options-div", !getCheckboxState("id_antiblock_ip_rotation_enabled"));
}

function userAgentRotationEnabled() {
    setHiddenState("user-agent-rotation-options-div", !getCheckboxState("id_antiblock_user_agent_rotation_enabled"));
}

function insertCookiesEnabled() {
    setHiddenState("insert-cookies-options-div", !getCheckboxState("id_antiblock_insert_cookies_enabled"));
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
