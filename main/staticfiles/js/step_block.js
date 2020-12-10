
/**
 * Init a block. A block is an element that allows the user choose a step and then
 * parametrize it.
 * @param  {List} step_list A list with the steps information.
 * @param {Number} depth The depth is the level of indentention of this step.
 * @return {Node} The block initalized.
 */
function init_block(step_list, depth){
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
    block.select.innerHTML = get_this_texts_inside_each_tag(get_step_names(step_list), "<option>")
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
    block.turn_to_pagination_step = turn_to_pagination_step

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

    block.select.onchange = refresh_step
    block.select.onchange()

    block.step = get_step_info(block.select.value, step_list)


    //Setting controler functions
    block.unindent_step = unindent_step   
    block.indent_step = indent_step    
    block.move_up = move_up
    block.move_down = move_down
    block.delete_step = delete_step
    block.add_block_bellow = add_block_bellow

    block.controler.children[0].onclick = block.add_block_bellow
    block.controler.children[1].onclick = block.unindent_step
    block.controler.children[2].onclick = block.indent_step
    block.controler.children[3].onclick = block.move_up
    block.controler.children[4].onclick = block.move_down
    block.controler.children[5].onclick = block.delete_step

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
    dropdown_menu.innerHTML = get_this_texts_inside_each_tag(optional_params, '<a class="dropdown-item" style="cursor:pointer">')
    for(child of dropdown_menu.children){
        child.onclick = function(){
            block = find_parent_with_attr_worth(this, "block")
            block.add_param(this.innerText, true)
            hide(this)
        }
    }

    block.new_parameter_button.dropdown_menu = dropdown_menu
    block.lines[last_line].appendChild(block.new_parameter_button_box) 
}


/**
 * This function adds a parameter to a block, that is, 
 * an input element to obtain the value to be setted 
 * for this parameter. This function is a method of block.
 * @param {String} param_name The name of the param to be added.
 * @param {Bool} optional_param A boolean that says whether or 
 *               not the parameter is optional
 */
function add_param(param_name, optional_param = false){
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
    param_element.innerHTML = `<input placeholder="` + String(param_name) + `" class="row form-control">`
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
    block.iterable_step = get_step_info(this.value, block.step_list)
    block.params = []

    block.delete_lines(1, block.lines.length)
    block.add_line()

    for(param of block.iterable_step.mandatory_params){
        block.add_param(param)
    }

    optional_params = Object.keys(block.iterable_step.optional_params)
    if(optional_params.length!=0){
        block.init_optional_params_button(block.iterable_step)
    }
}

/**
 * Refreshes the parameter inputs of an iterable when it is changed.
 * This function is a method of the select element of the block.
 */
function refresh_step(){
    block = find_parent_with_attr_worth(this, "block")
    block.step = get_step_info(this.value, block.step_list)
    block.params = []

    if(this.value=="for each"){
        block.turn_to_for_step()
    }else if(this.value=="for each page in"){
        block.turn_to_pagination_step()
    }else{
        block.delete_lines(block.lines.length)
        block.add_line()

        for(param of block.step.mandatory_params){
            block.add_param(param)
        }

        optional_params = Object.keys(block.step.optional_params)
        if(optional_params.length!=0){
            block.init_optional_params_button(block.step)
        }
    }
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

    iterator_input_box = document.createElement("DIV")
    iterator_input_box.className = "col-sm"    
    iterator_input = document.createElement("INPUT")
    iterator_input.value = "option"
    iterator_input.className = "form-control row"
    iterator_input_box.appendChild(iterator_input)
    block.iterator_input = iterator_input

    in_label_box = document.createElement("DIV")
    in_label_box.style.width = "3em"
    in_label = document.createElement("P")
    in_label.style.marginTop = "10%"
    in_label.style.textAlign = "center"
    in_label.innerText = " in"
    in_label_box.appendChild(in_label)    

    iterable_select_box = document.createElement("DIV")
    iterable_select_box.className = "step-config-select"
    iterable_select = document.createElement("select")
    iterable_select.className = "form-control select-step"
    iterable_select.innerHTML = get_this_texts_inside_each_tag(get_step_names(block.step_list), "<option>")
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
 * Sets the block to the pagination step.
 * This function is a method of the block.
 */
function turn_to_pagination_step(){
    block = find_parent_with_attr_worth(this, "block")
    block.delete_lines(block.lines.length)
    block.add_line()
    block.add_param("buttons ambiguous xpath")
    block.step.optional_params = {"next button index":-1}
    block.init_optional_params_button()
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

/**
 * Moves the block that called this method up.
 * This function is a method of the block
 */
function move_up(){
    block = find_parent_with_attr_worth(this, "block")
    index = get_index_in_parent(block)
    parent = block.parentElement
    if(index>0){
        parent.insertBefore(parent.children[index], parent.children[index-1]);
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
        parent.insertBefore(parent.children[index+1], parent.children[index]);
    }
}

/**
 * Delete the block that called this method.
 * This function is a method of the block
 */
function delete_step(){
    find_parent_with_attr_worth(this, "block").remove()
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
                                <img class="block-controler-button" src="/static/icons/black-x.svg">
                            </div>
                        </div>
                    <div>`
    var new_block = document.createElement("DIV")
    new_block.innerHTML = block_html_base
    new_block.className = "conteiner card step-block"
    return new_block
}