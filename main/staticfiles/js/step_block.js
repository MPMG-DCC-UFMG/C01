/**
 * Init a block. A block is an element that allows the user choose a step and then
 * parametrize it.
 * @param  {List} step_list A list with the steps information.
 * @param {Number} depth The depth is the level of indentention of this step.
 * @return {Node} The block initalized.
 */
function init_block(step_list, depth){
    // // Filter the steps so that only those compatible with iframe are available
    // if (curr_execution_context == 'iframe') 
    //     step_list = step_list.filter(function (step) { return step.executable_in_iframe })

    //instanciating and initializing the block element
    var block = init_block_element(step_list)

    //Adding some attributes
    block.type = "block"
    block.step_list = step_list
    block.depth = depth
    block.style.left = (block.depth*2-2) +"em"

    //setting the select step
    block.select_box = document.createElement("div")
    block.select_box.className = "step-config-select"
    block.select = document.createElement("select")
    block.select.className = "row form-control select-step"
    block.select.innerHTML = get_this_texts_inside_each_tag(Object.keys(get_step_names(step_list)), "<option>")
    block.select_box.appendChild(block.select)

    //Seting up the lines of the object
    block.lines_box = block.children[0]
    block.lines = block.lines_box.children
    block.params = []

    block.add_line = add_line
    block.add_line()

    //Setting the control
    block.controler_box = block.children[1]
    block.controler = block.controler_box.children[0]

    //Show parameter button
    block.params_visibility = true
    block.show_params_button_box = document.createElement("div")
    block.show_params_button = document.createElement("img")
    block.show_params_button_box.onclick = hide_show_params
    block.show_params_button_box.style.cursor = "pointer";
    block.show_params_button_box.style.padding = ".2em"
    block.show_params_button.src = "/static/icons/expand-down.png"
    block.show_params_button.style.display = "block";
    block.show_params_button.style.margin = "auto";
    block.appendChild(block.show_params_button_box)
    block.show_params_button_box.appendChild(block.show_params_button)
    block.show_params_button_box.onmouseover = function(){this.style.backgroundColor = "rgba(0,0,0,0.05)"}
    block.show_params_button_box.onmouseout = function(){this.style.backgroundColor = ""}
    block.hide_show_params = hide_show_params
    block.hide_show_params()

    //Setting the estrutural steps builders
    block.turn_to_for_step = turn_to_for_step
    block.turn_to_while_step = turn_to_while_step
    block.turn_to_attribution_step = turn_to_attribution_step
    block.turn_to_new_tab_step = turn_to_new_tab_step
    block.turn_to_close_tab_step = turn_to_close_tab_step
    block.turn_to_run_in_iframe_step = turn_to_run_in_iframe_step
    block.turn_to_exit_iframe_step = turn_to_exit_iframe_step
    block.turn_to_if_step = turn_to_if_step


    //Setting the border functions
    block.onmouseout = function(){
        hide(this.controler_box);
        this.style.borderColor = "";
        this.show_params_button_box.style.height = "0em";
        this.show_params_button.hidden = true
    }
    block.onmouseover = function(){
        show(this.controler_box);
        this.style.borderColor = "rgba(0,143,255,.5)";
        this.show_params_button_box.style.height = "2em";
        this.show_params_button.hidden = false
    }
    block.onmouseout()

    //seting other block methods
    block.delete_lines =  delete_lines


    //setting new parameter button
    block.init_optional_params_button = init_optional_params_button
    block.add_param = add_param    

    //--

    block.add_block_tooltip = add_block_tooltip

    block.select.onchange = refresh_step
    block.select.onchange()

    block.step = get_step_info(block.select.value)

    //Setting controler functions
    block.unindent_step = unindent_step
    block.indent_step = indent_step
    block.move_up = move_up
    block.move_down = move_down
    block.delete_step = delete_step
    block.add_block_bellow = add_block_bellow
    block.duplicate_blocks = duplicate_blocks

    block.controler.children[0].onclick = block.add_block_bellow
    block.controler.children[1].onclick = block.unindent_step
    block.controler.children[2].onclick = block.indent_step
    block.controler.children[3].onclick = block.move_up
    block.controler.children[4].onclick = block.move_down
    block.controler.children[5].onclick = block.duplicate_blocks
    block.controler.children[6].onclick = block.delete_step

    return block
}


//---------------- parameters manager methods --------------------------


/**
 * Init the optional parameters button. This button allows the user add optional parameters to the block.
 * This function is a method of the blocks.
 * @param {Dict} step A step in the json steps format
 */
function init_optional_params_button(step){

    block = find_parent_with_attr_worth(this, "block")

    block.new_parameter_button_box = document.createElement("DIV")
    block.new_parameter_button = document.createElement("BUTTON")
    new_parameter_button_image = document.createElement("IMG")
    dropdown_menu =  document.createElement("DIV")

    block.new_parameter_button_box.appendChild(block.new_parameter_button)
    block.new_parameter_button_box.appendChild(dropdown_menu)
    block.new_parameter_button.appendChild(new_parameter_button_image)

    block.new_parameter_button_box.style.borderRadius = "1em"

    block.new_parameter_button.type="button"
    block.new_parameter_button.className="btn btn-primary"
    block.new_parameter_button.setAttribute("data-toggle", "dropdown" )
    block.new_parameter_button.setAttribute("aria-haspopup", "true" )
    block.new_parameter_button.setAttribute("aria-expanded", "false")

    new_parameter_button_image.src = "/static/icons/white-plus-icon.svg"
    new_parameter_button_image.style.width = "1em"
    new_parameter_button_image.style.height = "1em"

    dropdown_menu.className = "dropdown-menu"

    if(!step){
        step = block.step
    }

    optional_params = Object.keys(step.optional_params)
    dropdown_menu.innerHTML = optional_params.map(
        function(param){
            text = param_to_placeholder(param)
            return `<a class="dropdown-item" style="cursor:pointer" data-param="${param}">${text}<\a>`
        }
    ).join('\n')
    for(child of dropdown_menu.children){
        child.onclick = function(){
            block = find_parent_with_attr_worth(this, "block")
            param = this.dataset.param
            field_options = step.field_options[param]
            block.add_param(param, field_options, true)
            hide(this)
        }
    }

    block.new_parameter_button.dropdown_menu = dropdown_menu
    block.lines[last_line].appendChild(block.new_parameter_button_box)
}

function generate_input_html(param_name, param_display, field_options){
    if (field_options == undefined){
        return `<input type="text" placeholder="${param_display}" class="row form-control" data-param="${param_name}" data-type="text" />`
    }

    field_type = field_options['field_type']
    innerHTML = ''

    switch(field_type){
        case 'text':
        case 'number':
            placeholder = field_options['input_placeholder'] == undefined ?  param_display : field_options['input_placeholder']
            innerHTML = `<input type="${field_type}" placeholder="${placeholder}" class="row form-control" data-param="${param_name}" data-type="text" />`
            break;
        case 'checkbox':
            label = field_options['checkbox_label']
            innerHTML = `<input type="${field_type}" id="${param_name}" class="form-check-input" data-param="${param_name}" data-type="bool"/>`
            innerHTML += `<label for="${param_name}" class="form-check-label">${label}</label>`
            break;
        case 'select':
            options = field_options['select_options']
            innerHTML += `<select class="row form-control" id="${param_name}" data-param="${param_name}" data-type="text">`
            innerHTML += `<option value="" disabled selected>${param_display}</option>`
            for(option of options){
                innerHTML += `<option value="${option}">${option}</option>`
            }
            innerHTML += `</select>`
            break;
    }

    return innerHTML
}

/**
 * This function adds a parameter to a block, that is,
 * an input element to obtain the value to be setted
 * for this parameter. This function is a method of block.
 * @param {String} param_name The name of the param to be added.
 * @param {Dict} field_options A dictionary containing options 
 * regarding the field which will be created for the parameter
 * @param {Bool} optional_param A boolean that says whether or
 *               not the parameter is optional
 */
function add_param(param_name, field_options, optional_param = false){
    block = find_parent_with_attr_worth(this, "block")
    last_line = block.lines.length-1
    if(block.lines[last_line].row.full){
        block.add_line()
        last_line++
        if(optional_param){
            block.new_parameter_button_box.remove()
            block.lines[last_line].appendChild(block.new_parameter_button_box)
        }
    }

    param_element = document.createElement("DIV")
    param_element.className = "col-sm"
    param_display = param_to_placeholder(param_name)

    param_element.innerHTML = generate_input_html(param_name, param_display, field_options)

    if(optional_param){
        remove_button = document.createElement("A")
        remove_img = document.createElement("IMG")
        remove_img.src = "/static/icons/black-x.svg"
        remove_button.appendChild(remove_img)
        remove_button.style.position = "absolute"
        remove_button.style.top = "-.75em"
        remove_button.style.right = "1.2em"
        remove_button.style.cursor = "pointer"
        hide(remove_button)
        remove_button.onclick = function(){
            block = find_parent_with_attr_worth(this, "block")
            line = find_parent_with_attr_worth(this, "line")
            line.row.full = false
            for(param of block.new_parameter_button.dropdown_menu.children){
                if(param.innerText == this.parentElement.children[0].placeholder){
                    show(param)
                }
            }
            line = find_parent_with_attr_worth(this, "line")

            this.parentElement.remove()

            if(block.lines[block.lines.length-1].row.children.length == 0){
                block.new_parameter_button_box.remove()
                block.lines[block.lines.length-2].append(block.new_parameter_button_box)
            }
            if(line.row.children.length==0){
                line.remove()
            }
        }
        param_element.remove_button = remove_button
        param_element.appendChild(remove_button)
        param_element.onmouseover = function(){show(this.remove_button)}
        param_element.onmouseout = function(){hide(this.remove_button)}
    }
    block.lines[last_line].row.appendChild(param_element)
    block.params.push(param_element)

    number_max_of_params=1
    if(last_line == 0){
        number_max_of_params=1
    }
    if(block.lines[last_line].row.children.length == number_max_of_params){
        block.lines[last_line].row.full = true
    }
}

//---------------- lines manager methods ------------------------------

/**
 * This function is method of block. It adds a line to this block.
 * A line is a conteiner that stores the parameters input and sometime,
 * other things.
 * @param {String} param_name The name of the param to be added.
 * @param {Bool} optional_param A boolean that says whether or
 *               not the parameter is optional
 */
function add_line(){
    block = find_parent_with_attr_worth(this, "block")
    new_line = document.createElement("DIV")
    new_line.className = "card-body row step-config"
    new_line.col = document.createElement("DIV")
    new_line.row = document.createElement("DIV")
    new_line.col.className = "col-sm"
    new_line.row.className = "row"
    new_line.appendChild(new_line.col)
    new_line.col.appendChild(new_line.row)
    new_line.type = "line"
    if(block.lines.length==0){
        new_line.insertBefore(block.select_box ,new_line.children[0])
    }else{
        new_line.style.paddingLeft = "2.25em";
    }
    block.lines_box.appendChild(new_line)
}

/**
 * This function is method of block. It deletes a range of lines.
 * @param {Number} m If n wasn't passed, so m is the top limit
 *                 of the range and 0 is the bottom limit. Else
 *                 m is the bottom limit
 * @param {Number} n The superior limit of the range.
 *
 */
function delete_lines(m, n=null){
    if(n===null){
        n=m
        m=0
    }
    for(var i=m; i<n; i++){
        block.lines[m].remove()
    }
}

//---------------- refresh methods -----------------------------------

/**
 * Refreshes the parameter inputs of an iterable when it is changed.
 * This function is a method of the iterable select element.
 */
function refresh_iterable(){
    block = find_parent_with_attr_worth(this, "block")
    block.iterable_step = get_step_info(this.value)
    block.params = []
    
    block.delete_lines(1, block.lines.length)
    block.add_line()

    for(param of block.iterable_step.mandatory_params){
        field_options = block.iterable_step.field_options[param]
        block.add_param(param, field_options)
    }

    optional_params = Object.keys(block.iterable_step.optional_params)
    if(optional_params.length!=0){
        block.init_optional_params_button(block.iterable_step)
    }
}

/**
 * Refreshes the parameter inputs of an condition when it is changed.
 * This function is a method of the condition select element.
 */
 function refresh_condition(){
    block = find_parent_with_attr_worth(this, "block")
    block.condition_step = get_step_info(this.value)
    block.params = []

    block.delete_lines(1, block.lines.length)
    block.add_line()

    for(param of block.condition_step.mandatory_params){
        field_options = block.condition_step.field_options[param]
        block.add_param(param, field_options)
    }

    optional_params = Object.keys(block.condition_step.optional_params)
    if(optional_params.length!=0){
        block.init_optional_params_button(block.condition_step)
    }
}

/**
 * Refreshes the parameter inputs of an source when it is changed.
 * This function is a method of the atributtion step.
 */
function refresh_source(){

    block = find_parent_with_attr_worth(this, "block")
    block.source_step = get_step_info(this.value)
    block.params = []

    block.delete_lines(1, block.lines.length)
    block.add_line()

    for(param of block.source_step.mandatory_params){
        field_options = block.source_step.field_options[param]
        block.add_param(param, field_options)
    }

    optional_params = Object.keys(block.source_step.optional_params)
    if(optional_params.length!=0){
        block.init_optional_params_button(block.source_step)
    }
}

/**
 * Colorize the context of the steps execution
 */

function colorize_contexts() {
    let contexts = [];
    let curr_context = 'page';
    
    let step_blocks = $('.step-block');

    for (let i=0; i < step_blocks.length;i++) {
        curr_step = step_blocks[i];
        
        // reseta cores
        curr_step.classList.remove("bg-tab-execution-context");
        curr_step.classList.remove("bg-iframe-execution-context");

        if (curr_step.classList.contains('new-tab-context-start')) {
            curr_step.classList.add("bg-tab-execution-context");

            contexts.push(curr_context)
            curr_context = 'tab';
        } else if (curr_step.classList.contains('iframe-context-start')) {
            curr_step.classList.add('bg-iframe-execution-context');

            contexts.push(curr_context)
            curr_context = 'iframe';
        } else if (curr_step.classList.contains('new-tab-context-end')) {
            curr_step.classList.add("bg-tab-execution-context");
            curr_context = contexts.pop();
        } else if (curr_step.classList.contains('iframe-context-end')) {
            curr_step.classList.add('bg-iframe-execution-context');
            curr_context = contexts.pop();
        } else {
            if (curr_context == 'iframe')
                curr_step.classList.add('bg-iframe-execution-context');
    
            else if (curr_context == 'tab')
                curr_step.classList.add("bg-tab-execution-context");
        }
    }

}

/**
 * Gets the context that a block to be inserted will have at the passed index, 
 * depending on whether the block will be inserted below or on top of another block
 * @param {Number} Index where the block will be inserted in the step block set.
 * @param {String} direction Indicates whether the block will be inserted below or above another
 * @return {String} The execution context of the inserted step (page, tab, or iframe)
 */

function get_insertion_index_context(index, direction) {
    let curr_context = 'page';
    
    let step_blocks = $('.step-block');
    if (index < 0)
        index = step_blocks.length
    
    let contexts = [];

    for (let i = 0; i < step_blocks.length; i++) {
        curr_step = step_blocks[i];
        if (curr_step.classList.contains('new-tab-context-start')) {
            if (i == index) {
                // we are leaving the tab context
                if (direction == 'up')
                    return curr_context;
                // we are entering the tab context
                return 'tab';
            }

            contexts.push(curr_context)
            curr_context = 'tab';

        } else if (curr_step.classList.contains('iframe-context-start')) {
            if (i == index) {
                // we are leaving the iframe context
                if (direction == 'up')
                    return curr_context;
                // we are entering the iframe context
                return 'iframe';
            }

            contexts.push(curr_context)
            curr_context = 'iframe';
        } else if (curr_step.classList.contains('new-tab-context-end') || curr_step.classList.contains('iframe-context-end')) {
            if (i == index) {
                if (direction == 'up')
                    return curr_context;
                return contexts.pop();
            }

            curr_context = contexts.pop(); 
        } else {
            if (i == index)
                return curr_context
        }
    }

    return curr_context;
}


/**
 * Updates the available step options according to an execution context
 * @param {Node} block The block that will have the updated step options
 * @param {String} context The new context that the block will execute
 */
function refresh_step_options(block, context) {
    let value = block.select.value
    let context_step_list = step_list.filter(function (step) { return step_executable_in_context(step, context) })
    block.select.innerHTML = get_this_texts_inside_each_tag(Object.keys(get_step_names(context_step_list)), "<option>")
    block.select.value = value
}

/**
 * Updates the options available for all step blocks below an index in the block set
 * @param {Number} index Indicates from which index the available step options will be updated
 */

function refresh_steps_option_below_index(index) {
    let step_blocks = $('.step-block')
    let start_index = index + 1;
    if (start_index >= step_blocks.length)
        return;

    for (let i=start_index;i<step_blocks.length;i++) {
        let context = get_insertion_index_context(index, 'down')
        refresh_step_options(step_blocks[i], context)
    }
}

/**
 * Adds the button and the functionality to open the iframe in a new tab
 * @param {Node} block Block containing the "Executar em iframe" step
 */
function add_open_iframe_button(block) {
    block.open_iframe_block = document.createElement("DIV")
    block.open_iframe_button = document.createElement("BUTTON")
    open_iframe_img = document.createElement("IMG")

    block.open_iframe_block.appendChild(block.open_iframe_button)
    block.open_iframe_button.appendChild(open_iframe_img)

    block.open_iframe_block.style.borderRadius = "1em"

    block.open_iframe_button.type = "button"
    block.open_iframe_button.title = "Abrir iframe em nova aba"
    block.open_iframe_button.className = "btn btn-primary"

    open_iframe_img.src = "/static/icons/external-link-alt-solid.svg"
    open_iframe_img.style.width = "1.25em"
    open_iframe_img.style.height = "1.25em"

    block.open_iframe_button.onclick = function () {
        let xpath = block.xpath_input.value;

        if (xpath.length == 0) {
            alert('É necessário especificar o XPATH do iframe antes!')
            return
        }

        let base_url = document.getElementById('id_base_url').value
        if (base_url.length == 0) {
            alert('Insira a "URL BASE" primeiro na seção "Infos básicas"!')
            return
        }

        let host = location.protocol + '//' + location.host;

        let enc_base_url = encodeURIComponent(base_url)
        let enc_xpath = encodeURIComponent(xpath)

        let url_of_iframe_loader = `${host}/iframe/load?url=${enc_base_url}&xpath=${enc_xpath}`

        window.open(url_of_iframe_loader, '_blank').focus();
    }

    block.lines[last_line].appendChild(block.open_iframe_block)
}

/**
 * Refreshes the parameter inputs of an iterable when it is changed.
 * This function is a method of the select element of the block.
 */
function refresh_step(){
    let execution_context_changed = false;
    
    
    
    block = find_parent_with_attr_worth(this, "block")
    block.step = get_step_info(this.value)
    block.params = []

    // reseta o contexto do block
    block.classList.remove("new-tab-context-start")
    block.classList.remove("new-tab-context-end")
    block.classList.remove("iframe-context-start")
    block.classList.remove("iframe-context-end")

    if(this.value=="Para cada") {
        block.turn_to_for_step()
    } else if(this.value=="Enquanto") {
        block.turn_to_while_step()
    } else if(this.value=="Se") {
        block.turn_to_if_step()
    } else if(this.value=="Atribuição") {
        block.turn_to_attribution_step()
    } else if(this.value=="Abrir em nova aba") {
        block.turn_to_new_tab_step()
        block.className += " new-tab-context-start"
        execution_context_changed = true
    } else if(this.value=="Fechar aba") {
        block.turn_to_close_tab_step()
        block.className += " new-tab-context-end"
        execution_context_changed = true
    } else if (this.value == "Executar em iframe") {
        block.turn_to_run_in_iframe_step()
        block.className += " iframe-context-start"
        execution_context_changed = true;
    } else if (this.value == "Sair de iframe") {
        block.turn_to_exit_iframe_step()
        block.className += " iframe-context-end"
        execution_context_changed = true;
    } else {
        block.delete_lines(block.lines.length)
        block.add_line()

        for(param of block.step.mandatory_params){
            field_options = block.step.field_options[param]
            block.add_param(param, field_options)
        }

        optional_params = Object.keys(block.step.optional_params)
        if(optional_params.length!=0){
            block.init_optional_params_button(block.step)
        }
    }

    //add block tooltip depending on type selection
    block.add_block_tooltip();

    if (execution_context_changed) {
        let index = get_index_in_parent(block)
        refresh_steps_option_below_index(index)
    }

    colorize_contexts()
}


//---------------- "turn to" methods ---------------------------------

/**
 * Sets the block to the for each step.
 * This function is a method of the block.
 */
function turn_to_for_step(){
    block = find_parent_with_attr_worth(this, "block")
    block.delete_lines(block.lines.length)
    block.add_line()

    // defines iterator
    iterator_input_box = document.createElement("DIV")
    iterator_input_box.className = "col-sm"
    iterator_input = document.createElement("INPUT")
    iterator_input.placeholder = "opção"
    iterator_input.className = "form-control row"
    iterator_input_box.appendChild(iterator_input)
    block.iterator_input = iterator_input

    in_label_box = document.createElement("DIV")
    in_label_box.style.width = "3em"
    in_label = document.createElement("P")
    in_label.style.marginTop = "10%"
    in_label.style.textAlign = "center"
    in_label.innerText = " em"
    in_label_box.appendChild(in_label)

    // defines iterable step
    iterable_select_box = document.createElement("DIV")
    iterable_select_box.className = "step-config-select"
    iterable_select = document.createElement("select")
    iterable_select.className = "form-control select-step"
    iterable_select.innerHTML = get_this_texts_inside_each_tag(Object.keys(get_step_names(block.step_list)), "<option>")
    iterable_select_box.appendChild(iterable_select)
    block.iterable_select = iterable_select

    block.lines[0].row.appendChild(iterator_input_box)
    block.lines[0].row.appendChild(in_label_box)
    block.lines[0].row.appendChild(iterable_select_box)
    block.lines[0].row.full = true

    iterable_select.onchange = refresh_iterable
    iterable_select.onchange()
}

/**
 * Sets the block to the while step.
 * This function is a method of the block.
 */
 function turn_to_while_step(){
    block = find_parent_with_attr_worth(this, "block")
    block.delete_lines(block.lines.length)
    block.add_line()

    // defines "invert" checkbox
    invert_input_box = document.createElement("DIV")
    invert_input = document.createElement("input")
    invert_input.setAttribute("type", "checkbox");
    invert_input_box.appendChild(invert_input)
    invert_input_label = document.createElement("label")
    invert_input_label.innerHTML = "Inverter"
    invert_input_label.style.paddingLeft = "0.5em"
    invert_input_box.appendChild(invert_input_label)
    block.invert_input = invert_input

    // defines condition step
    condition_select_box = document.createElement("DIV")
    condition_select_box.className = "step-config-select"
    condition_select = document.createElement("select")
    condition_select.className = "form-control select-step"
    condition_select.innerHTML = get_this_texts_inside_each_tag(Object.keys(get_step_names(block.step_list)), "<option>")
    condition_select_box.appendChild(condition_select)
    block.condition_select = condition_select

    block.lines[0].row.appendChild(invert_input_box)
    block.lines[0].row.appendChild(condition_select_box)
    block.lines[0].row.full = true

    condition_select.onchange = refresh_condition
    condition_select.onchange()
}

/**
 * Sets the block to the if step.
 * This function is a method of the block.
 */
 function turn_to_if_step(){
    block = find_parent_with_attr_worth(this, "block")
    block.delete_lines(block.lines.length)
    block.add_line()

    // defines "invert" checkbox
    invert_input_box = document.createElement("DIV")
    invert_input = document.createElement("input")
    invert_input.setAttribute("type", "checkbox");
    invert_input_box.appendChild(invert_input)
    invert_input_label = document.createElement("label")
    invert_input_label.innerHTML = "Inverter"
    invert_input_label.style.paddingLeft = "0.5em"
    invert_input_box.appendChild(invert_input_label)
    block.invert_input = invert_input

    // defines condition step
    condition_select_box = document.createElement("DIV")
    condition_select_box.className = "step-config-select"
    condition_select = document.createElement("select")
    condition_select.className = "form-control select-step"
    condition_select.innerHTML = get_this_texts_inside_each_tag(Object.keys(get_step_names(block.step_list)), "<option>")
    condition_select_box.appendChild(condition_select)
    block.condition_select = condition_select

    block.lines[0].row.appendChild(invert_input_box)
    block.lines[0].row.appendChild(condition_select_box)
    block.lines[0].row.full = true

    condition_select.onchange = refresh_condition
    condition_select.onchange()
}

/**
 * Sets the block to the attribution step.
 * This function is a method of the attribution step.
 */
 function turn_to_attribution_step(){
    block = find_parent_with_attr_worth(this, "block")
    block.delete_lines(block.lines.length)
    block.add_line()

    // defines target
    target_input_box = document.createElement("DIV")
    target_input_box.className = "col-sm"
    target_input = document.createElement("INPUT")
    target_input.value = "opção"
    target_input.className = "form-control row"
    target_input_box.appendChild(target_input)
    block.target_input = target_input

    in_label_box = document.createElement("DIV")
    in_label_box.style.width = "3em"
    in_label = document.createElement("P")
    in_label.style.marginTop = "10%"
    in_label.style.textAlign = "center"
    in_label.innerText = " ="
    in_label_box.appendChild(in_label)

    // defines source step
    source_select_box = document.createElement("DIV")
    source_select_box.className = "step-config-select"
    source_select = document.createElement("select")
    source_select.className = "form-control select-step"
    source_select.innerHTML = get_this_texts_inside_each_tag(Object.keys(get_step_names(block.step_list)), "<option>")
    source_select_box.appendChild(source_select)
    block.source_select = source_select

    block.lines[0].row.appendChild(target_input_box)
    block.lines[0].row.appendChild(in_label_box)
    block.lines[0].row.appendChild(source_select_box)
    block.lines[0].row.full = true

    source_select.onchange = refresh_source
    source_select.onchange()
}

/**
 * Sets the block to the open in new page step.
 * This function is a method of the block.
 */
function turn_to_new_tab_step(){
    block = find_parent_with_attr_worth(this, "block")
    block.delete_lines(block.lines.length)
    block.add_line()

    // defines link xpath
    xpath_input_box = document.createElement("DIV")
    xpath_input_box.className = "col-sm"
    xpath_input = document.createElement("INPUT")
    xpath_input.placeholder = "xpath do link"
    xpath_input.className = "form-control row"
    xpath_input_box.appendChild(xpath_input)
    block.xpath_input = xpath_input

    block.lines[0].row.appendChild(xpath_input_box)
    block.lines[0].row.full = true
}

function turn_to_close_tab_step(){
    block = find_parent_with_attr_worth(this, "block")
    block.delete_lines(block.lines.length)
    block.add_line()
    block.lines[0].row.full = true
}

/**
 * Sets the block to the run in iframe step.
 * This function is a method of the block.
 */
function turn_to_run_in_iframe_step(){
    block = find_parent_with_attr_worth(this, "block")
    block.delete_lines(block.lines.length)
    block.add_line()

    // defines iframe xpath
    xpath_input_box = document.createElement("DIV")
    xpath_input_box.className = "col-sm"
    xpath_input = document.createElement("INPUT")
    xpath_input.placeholder = "xpath do iframe"
    xpath_input.className = "form-control row"
    xpath_input_box.appendChild(xpath_input)
    block.xpath_input = xpath_input

    block.lines[0].row.appendChild(xpath_input_box)
    block.lines[0].row.full = true

    add_open_iframe_button(block);
}

function turn_to_exit_iframe_step(){
    block = find_parent_with_attr_worth(this, "block")
    block.delete_lines(block.lines.length)
    block.add_line()
    block.lines[0].row.full = true
}


//---------------- block menu methods ------------------------------

/**
 * Hides the parameters inputs of a block.
 * This function is a method of the block
 */
function hide_show_params(){
    block = find_parent_with_attr_worth(this, "block")
    if (block.params_visibility){
        block.params_visibility = false
        for(var i = 1; i < block.lines.length; i++){
            block.lines[i].hidden = false
        }
        block.show_params_button.style.transform = 'rotate(180deg)';
    }else{
        block.params_visibility = true
        for(var i = 1; i < block.lines.length; i++){
            block.lines[i].hidden = true
        }
        block.show_params_button.style.transform = 'rotate(0deg)';
    }
}

/**
 * Adds a block bellow the block that called this method.
 * This function is a method of the block
 */
function add_block_bellow(){
    step_board = find_parent_with_attr_worth(this, "step_board")
    block = find_parent_with_attr_worth(this, "block")
    i=0
    while(block != step_board.children[i]){i++}
    step_board.add_block(step_list, i+1)
}

/**
 * Decrease the indent of the block that called this method.
 * This function is a method of the block
 */
function unindent_step(){
    block = find_parent_with_attr_worth(this, "block")
    if(block.depth > 1){
        block.depth-=1
        block.parentElement.current_depth -= 1
    }
    block.style.left = (block.depth*2-2) +"em"
}

/**
 * Increase the indent of the block that called this method.
 * This function is a method of the block
 */
function indent_step(){
    block = find_parent_with_attr_worth(this, "block")
    block.depth+=1
    block.parentElement.current_depth += 1
    block.style.left = (block.depth*2-2) +"em"
}

function step_executable_in_context(step, context) {
    return step.executable_contexts.indexOf(context) >= 0
}

/**
 * Moves the block that called this method up.
 * This function is a method of the block
 */
function move_up(){
    block = find_parent_with_attr_worth(this, "block")

    
    index = get_index_in_parent(block)
    parent = block.parentElement
    if(index>0){ 
        if (get_insertion_index_context(index-1, 'up') == 'iframe') {
            let step = get_step_info(block.select.value);
            if (!step_executable_in_context(step, 'iframe')) {
                alert(`⚠️ Não é possível mover o passo "${step.name_display}" para o contexto de execução de iframe, pois ele não é compatível!`)
                return;
            }
        } 
        
        if (get_block_value_by_index(index) == 'Executar em iframe') {
            let previous_step_value = get_block_value_by_index(index - 1)
            let step = get_step_info(previous_step_value)
            if (!step_executable_in_context(step, 'iframe')) {
                alert(`⚠️ Não é possível mover o passo "${step.name_display}" para o contexto de execução de iframe, pois ele não é compatível!`)
                return;
            }
        }
        
        let last_block_context = get_insertion_index_context(index, 'up');
        parent.insertBefore(parent.children[index], parent.children[index-1]);
        let curr_block_context = get_insertion_index_context(index-1,'up');
        
        
        // o contexto do bloco mudou
        if (last_block_context != curr_block_context) {
            refresh_step_options(block, curr_block_context)
        }
        colorize_contexts()
    }
}

/**
 * Moves the block that called this method down.
 * This function is a method of the block
 */
function move_down(){
    block = find_parent_with_attr_worth(this, "block")
    index = get_index_in_parent(block)
    parent = block.parentElement
    
    if(index<parent.children.length-1){
        if (get_insertion_index_context(index + 1, 'down') == 'iframe') {
            let step = get_step_info(block.select.value);
            if (!step_executable_in_context(step, 'iframe')) {
                alert(`⚠️ Não é possível mover o passo "${step.name_display}" para o contexto de execução de iframe, pois ele não é compatível!`)
                return;
            }
        }

        if (get_block_value_by_index(index) == 'Sair de iframe') {
            let next_step_value = get_block_value_by_index(index + 1)
            let step = get_step_info(next_step_value)
            if (!step_executable_in_context(step, 'iframe')) {
                alert(`⚠️ Não é possível mover o passo "${step.name_display}" para o contexto de execução de iframe, pois ele não é compatível!`)
                return;
            }
        }

        let last_block_context = get_insertion_index_context(index, 'up');
        parent.insertBefore(parent.children[index+1], parent.children[index]);
        let curr_block_context = get_insertion_index_context(index + 1, 'up');

        // o contexto do bloco mudou
        if (last_block_context != curr_block_context) {
            refresh_step_options(block, curr_block_context)
        }
        colorize_contexts()
    }
}

/**
 * Duplicates the block that called this method and its children.
 * This function is a method of the block
 */
 function duplicate_blocks(){
    block = find_parent_with_attr_worth(this, "block") //var block is the triggered one
    trigged_depth = block.depth
    i=0
    //finds block to duplicate
    while(block != step_board.children[i]){i++} 
    trigged_index = i
    //finds how many children blocks
    while(step_board.children[i+1] && trigged_depth < step_board.children[i+1].depth){i++} 
    last_child_index = i
    //creates the new blocks
    copy = 0
    while(copy != (last_child_index-trigged_index+1)) {        
        step_board.add_block(step_list, last_child_index+copy+1) //var block is now the added block
        //fix the depth of the new block
        block.depth = step_board.children[trigged_index+copy].depth
        block.parentElement.current_depth = block.depth
        block.style.left = (block.depth*2-2) +"em"
        //copies the block type
        block.select.value = step_board.children[trigged_index+copy].select.value
        block.select.onchange()
        //gets all selects
        let new_selects = Array.prototype.slice.apply(block.querySelectorAll("select"))
        let old_selects = Array.prototype.slice.apply(step_board.children[trigged_index+copy].querySelectorAll("select"))
        //copies all select values
        new_selects.forEach((select,index) => {
            if (index !== 0) {
                select.value = old_selects[index].value
                select.onchange()
            }
        })
        //checks if it has extra field
        extra_option =  step_board.children[trigged_index+copy].querySelector('.dropdown-menu')
        if (extra_option && (step_board.children[trigged_index+copy].querySelector('input[data-param="numero_xpaths"]') || step_board.children[trigged_index+copy].querySelector('input[data-param="xpath_do_campo_a_preencher"]'))) {
            block.querySelector('.dropdown-menu a').click()
        }
        //get all inputs
        let new_inputs = Array.prototype.slice.apply(block.querySelectorAll("input"))
        let old_inputs = Array.prototype.slice.apply(step_board.children[trigged_index+copy].querySelectorAll("input"))
        //copies all input values
        new_inputs.forEach((input,index) => {
            input.value = old_inputs[index].value
        })
        copy++
    }
}

/**
 * Delete the block that called this method.
 * This function is a method of the block
 */
function delete_step(){
    block = find_parent_with_attr_worth(this, "block")
    let index = get_index_in_parent(block)

    block.remove()

    refresh_steps_option_below_index(index-1)
    colorize_contexts();
}


//------------------ others ------------------------

/**
 * Init a block element. This function is called by the function init_block.
 * It just initialize the base of the block element.
 * @param  {List} step_list A list with the steps information.
 * @return {Node} The block initalized.
 */
function init_block_element(step_list){
    var block_html_base = `<div class="col-sm">
                    </div>
                    <div class="conteiner block-controler">
                        <div class="row block-controler-interface">
                            <div class="col-sm">
                                <img class="block-controler-button" src="/static/icons/black-plus.svg">
                            </div>
                            <div class="col-sm">
                                <img class="block-controler-button" src="/static/icons/arrow-left-black.svg">
                            </div>
                            <div class="col-sm">
                                <img class="block-controler-button" src="/static/icons/arrow-right-black.svg">
                            </div>
                            <div class="col-sm">
                                <img class="block-controler-button" src="/static/icons/arrow-up-black.svg">
                            </div>
                            <div class="col-sm">
                                <img class="block-controler-button" src="/static/icons/arrow-down-black.svg">
                            </div>
                            <div class="col-sm">
                                <img class="block-controler-button" src="/static/icons/duplicate-black.svg">
                            </div>
                            <div class="col-sm">
                                <img class="block-controler-button" src="/static/icons/black-x.svg">
                            </div>
                        </div>
                    <div>`
    var new_block = document.createElement("DIV")
    new_block.innerHTML = block_html_base

    new_block.className = "conteiner card step-block"

    return new_block
}

/**
 * Adds block tooltip depending on type selection
 * This function is called on the function refresh_step.
 */
function add_block_tooltip() {
    block = find_parent_with_attr_worth(this, "block")
    
    switch(block.step.name){
        case "clique":
            tooltip = "Recebe um XPath, entre aspas, ou uma váriavel (por exemplo, dentro de um Para cada) para identificar o elemento correspondente na página e clicar sobre ele."
            break;
        case "comparacao":
            tooltip = ""
            break;
        case "digite":
            tooltip = "Permite que o usuário preencha as entradas HTML do tipo input para entradas textuais."
            break;
        case "elemento_existe_na_pagina":
            tooltip = ""
            break;
        case "espere":
            tooltip = "Congela a execução durante o tempo informado em segundos"
            break;
        case "extrai_propriedade":
            tooltip = ""
            break;
        case "extrai_texto":
            tooltip = "Extrai e retorna o texto do elemento apontado pelo xpath fornecido. Pode ser mais útil se utilizado com o passo de Atribuição. Nota: é necessário converter esse valor para um valor inteiro, utilizando a int([variável_atribuida]) para que ele possa ser utilizado no Para Cada."
            break;
        case "for_clicavel":
            tooltip = ""
            break;
        case "imprime":
            tooltip = "Essa ação se assemelha ao 'print' do Python, e permite imprimir nos logs dos coletores qualquer valor desejado, por exemplo, XPath armazenado em uma variável."
            break;
        case "localiza_elementos":
            tooltip = "Utilizado junto com o Para Cada recebe um XPath genérico (que apresenta um, e apenas um, asterisco) e retorna uma lista com todos os elementos na página que casam com esse elemento genérico"
            break;
        case "nesse_elemento_esta_escrito":
            tooltip = ""
            break;
        case "objeto":
            tooltip = "Utilizado em conjunto com outro passo para retornar um objeto estático. Exemplo: pode ser utilizado na função de Para Cada para retornar uma lista de valores pré-definidos."
            break;
        case "opcoes":
            tooltip = "Utilizado junto com o Para Cada recebe um XPath de um select e retorna uma lista com todas as suas opções. Com isso, podemos iterar nessas opções e possivelmente, selecionar cada uma delas, usando o 'Selecione'"
            break;
        case "quebrar_captcha_imagem":
            tooltip = ""
            break;
        case "repete":
            tooltip = "Utilizado junto com o Para Cada recebe um valor inteiro N e é responsável por retornar a lista de valores partindo de 0 até N-1"
            break;
        case "retorna_pagina":
            tooltip = "Simula a opção de voltar dos navegadores."
            break;
        case "salva_pagina":
            tooltip = "O conteúdo será armazenado em memória e ao final da execução de ações, tais páginas serão armazenadas em disco. Além disso, essas páginas podem ser exploradas com as outras ferramentas presentes na plataforma, por exemplo, a exploração de links. A partir desse ponto, novas requisições serão executadas fora de um webdriver, portanto, podem não carregar mais o conteúdo JavaScript da página."
            break;
        case "selecione":
            tooltip = "Essa ação recebe como entrada o XPath do select e o texto da opção a ser selecionada."
            break;
        case "para_cada":
            tooltip = "Define um conjunto de ações que será repetido. O primeiro input será a variável criada para uso no conjunto de ações, que corresponde ao valor da vez no loop. Essa ação deve ser combinada com outra que retorne uma lista."
            break;
        case "atribuicao":
            tooltip = "Atribui o valor de retorno de um dos passos ao nome fornecido."
            break;
        case "abrir_em_nova_aba":
            tooltip = "Funciona de forma parecida a função de clique, com a diferença de que aqui, caso o link apontado pelo xpath fornecido leva a uma página de destino, ela é aberta em uma nova aba, e o contexto de navegação é alterado para esta nova aba."
            break;
        case "fechar_aba":
            tooltip = "Deve ser usada em conjunto com a função Abrir em Nova Aba. Este passo fecha a última aba aberta pelo passo anterior, e retorna o contexto para a página que a abriu."
            break;
        case "executar_em_iframe":
            tooltip = ""
            break;
        case "sair_de_iframe":
            tooltip = ""
            break;
        case "screenshot":
            tooltip = ""
            break;
        case "enquanto":
            tooltip = ""
            break;
        default:
            tooltip = ""
            break;
    }

    old_tooltip = this.querySelector('.block_tooltip');
    if (old_tooltip) {
        $(old_tooltip).remove();
    }

    if (tooltip != "") {
        tooltip_element = document.createElement("DIV")
        tooltip_element.className = "block_tooltip"
        tooltip_element.innerHTML = '<button type="button" class="popover-icon btn btn-link start_tooltip" data-toggle="popover" data-trigger="hover" data-content="'+tooltip+'"><i class="fa fa-info-circle" aria-hidden="true"></i></button>';
        block.firstChild.childNodes[1].appendChild(tooltip_element);
        setTimeout(() => {$('.start_tooltip').popover();$('.start_tooltip').removeClass('start_tooltip');}, 800);
        
    } 
}