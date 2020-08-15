function init_block(step_list, depth){
    //instanciating and initializing the block element
    var block = init_block_element(step_list)

    //Adding some attributes
    block.id = genId()
    block.type = "block"
    block.step_list = step_list
    block.depth = depth
    block.style.left = (block.depth*2-2) +"em"

    //setting the select step
    block.select_box=document.createElement("div")
    block.select_box.className = "step-config-select"
    block.select = document.createElement("select")
    block.select.className = "row form-control select-step"
    block.select.innerHTML = get_this_texts_inside_each_tag(get_step_names(step_list), "<option>")
    block.select_box.appendChild(block.select)

    //Seting up the lines of the object
    block.lines_box = block.children[0]
    block.lines = block.lines_box.children
    block.add_line = add_line
    block.add_line()

    //Setting the control
    block.controler_box = block.children[1]
    block.controler = block.controler_box.children[0]

    //Setting the estrutural steps builders
    block.turn_to_for_step = turn_to_for_step

    //Setting the border functions
    block.onmouseout = function(){hide(this.controler_box); this.style.borderColor = ""}
    block.onmouseover = function(){show(this.controler_box); this.style.borderColor = "rgba(0,143,255,.5)"}
    block.onmouseout()



    
    //seting other block methods
    block.get_line = get_line
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

    block.controler.children[0].onclick = block.unindent_step
    block.controler.children[1].onclick = block.indent_step
    block.controler.children[2].onclick = block.move_up
    block.controler.children[3].onclick = block.move_down
    block.controler.children[4].onclick = block.delete_step

    return block
}


//---------------- parameters manager methods --------------------------

function init_optional_params_button(optional_params){
    
    block = find_parent_of_type(this, "block")

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
    new_parameter_button_image.style.heigth = "1em"

    dropdown_menu.className = "dropdown-menu"
    step = get_step_info(block.select.value, block.step_list)
    dropdown_menu.innerHTML = get_this_texts_inside_each_tag(optional_params, '<a class="dropdown-item" style="cursor:pointer">')

    for(child of dropdown_menu.children){
        child.onclick = function(){
            block = find_parent_of_type(this, "block")
            block.add_param(this.innerText, true)
            hide(this)
        }
    }
    block.new_parameter_button.dropdown_menu = dropdown_menu

}

function add_param(param_name, optional_param = false){
    block = find_parent_of_type(this, "block")
    last_line = block.lines.length-1
    max_params=3
    if(last_line == 0){
        max_params=2
    }
    if(block.lines[last_line].row.children.length == max_params){
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
        remove_img.src = "/static/icons/x.svg"
        remove_button.appendChild(remove_img)
        remove_button.style.position = "absolute"
        remove_button.style.top = "-.75em"
        remove_button.style.right = "1.2em"
        remove_button.style.cursor = "pointer"
        hide(remove_button)
        remove_button.onclick = function(){
            block = find_parent_of_type(this, "block")
            for(param of block.new_parameter_button.dropdown_menu.children){
                if(param.innerText == this.parentElement.children[0].placeholder){
                    show(param)
                }
            }
            line = find_parent_of_type(this, "line")
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
}

//---------------- lines manager methods ------------------------------

function add_line(){
    block = find_parent_of_type(this, "block")
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

function get_line(i){
    if(i==0){
        return block.lines_box.children[0].children[1].children[0]
    }else{
        return block.lines_box.children[i].children[0].children[0]
    }
}

function delete_lines(len){
    var n = len
    for(var i=0; i<n; i++){
        block.lines[0].remove()
    }
}

//---------------- refresh methods -----------------------------------

function refresh_iterable(){
    step_html = get_params_element_list(this.value)
    commun_parent = this.parentElement.parentElement.parentElement.parentElement.parentElement
    commun_parent.children[1].children[0].children[0].innerHTML = step_html
    
}

function refresh_step(){
    block = find_parent_of_type(this, "block")
    block.step = get_step_info(this.value, block.step_list)

    if(this.value=="para cada"){
        block.turn_to_for_step()
    }else{
        block.delete_lines(block.lines.length)
        block.add_line()

        for(param of block.step.mandatory_params){
            block.add_param(param)
        }

        optional_params = Object.keys(block.step.optional_params)
        if(optional_params.length!=0){
            block.init_optional_params_button(optional_params)
            block.lines[last_line].appendChild(block.new_parameter_button_box) 
        }
    }
    
}


//---------------- "turn to" methods ---------------------------------

function turn_to_for_step(){
    block = find_parent_of_type(this, "block")
    block.delete_lines(block.lines.length)
    block.add_line()
    alert(block.lines.length)

    inside_first_row = `<div class="col-sm"><input value="opcao" class="form-control"></div>
                        <div style="width:3em;"><p style="margin-top:10%; text-align:center;">em</p></div>
                        <div class="step-config-select">
                            <select class="form-control select-step">` + get_this_texts_inside_each_tag(get_step_names(block.step_list), "<option>")+ `<option>objeto</option>` + `</select>
                        </div>`


    block.lines[0].children[1].children[0].innerHTML = inside_first_row
    select_iterable = block.lines[0].children[1].children[0].children[2].children[0]
    for(param of get_params_element_list(select_iterable.value, block.step_list)){
        block.lines[1].children[0].children[0].appendChild = param
    }
    select_iterable.onchange = refresh_iterable
    block.iterator_input = block.lines[0].children[1].children[0].children[0].children[0]
    block.iterable_select = block.lines[0].children[1].children[0].children[2].children[0]
    block.iterable_params_div = block.lines[1].children[0].children[0]

    return step_html
}



//---------------- block menu methods ------------------------------

function unindent_step(){
    block = find_parent_of_type(this, "block")
    if(block.depth > 1){
        block.depth-=1
        block.parentElement.current_depth -= 1
    }
    block.style.left = (block.depth*2-2) +"em"
}

function indent_step(){
    block = find_parent_of_type(this, "block")
    block.depth+=1
    block.parentElement.current_depth += 1
    block.style.left = (block.depth*2-2) +"em"
}

function move_up(){
    block = find_parent_of_type(this, "block")
    index = get_index_in_parent(block)
    parent = block.parentElement
    if(index>0){
        parent.insertBefore(parent.children[index], parent.children[index-1]);
    }
}

function move_down(){
    block = find_parent_of_type(this, "block")
    index = get_index_in_parent(block)
    parent = block.parentElement
    if(index<parent.children.length-1){
        parent.insertBefore(parent.children[index+1], parent.children[index]);
    }
}

function delete_step(){
    find_parent_of_type(this, "block").remove()
}


//------------------ others ------------------------

function init_block_element(step_list){
    var step_html = `<div class="col-sm">
                    </div>
                    <div class="conteiner block-controler">
                        <div class="row block-controler-interface">
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
                                <img class="block-controler-button" src="/static/icons/x.svg">
                            </div>
                        </div>
                    <div>`
    var new_step = document.createElement("DIV")
    new_step.innerHTML = step_html
    new_step.className = "conteiner card step-block"
    return new_step
}  