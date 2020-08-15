

function load_steps(outside_element, json_path="/static/json/step_signatures.json"){
    var xmlhttp = new XMLHttpRequest();
    
    xmlhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        step_list = JSON.parse(this.responseText)
        step_list = step_list.concat(JSON.parse('{"name":"para cada"}'))
        init_steps_creation_interface(outside_element, step_list)
      }
    };

    xmlhttp.open("GET", json_path, true);
    xmlhttp.send();
}



//-------------- creation_interface ------------------------------

function init_steps_creation_interface(outside_element, step_list){
    outside_element.innerHTML = `<div class="row" style="margin-top: 1em">
                            <a class="btn btn-primary" style="color:white; width: 10em; margin-right: 2em" id="add_step_button" onclick=build_json()>
                                    generate json
                            </a>
                            <input class="form-control col-sm" id="json_output" placeholder="steps json">
                        </div>
                        `
    steps_creation_interface = document.createElement("div")
    steps_creation_interface.type= "steps_creation_interface"
    
    step_controler = document.createElement("div")
    step_controler.type = "step_controler"
    step_board = init_step_board(step_list)

    a = document.createElement("a")
    a.className="btn btn-primary"
    a.style.color = "white"
    a.onclick = function(){step_board.add_block(step_list)}
    a.innerText = "Adicionar Bloco"

    step_controler.appendChild(a)
    steps_creation_interface.appendChild(step_controler)
    steps_creation_interface.appendChild(step_board)
    steps_creation_interface.step_controler = step_controler
    steps_creation_interface.step_board = step_board

    outside_element.insertBefore(steps_creation_interface, outside_element.children[0])
}

//------------------- step board ------------------------------

function init_step_board(step_list){
    step_board = document.createElement('DIV')
    step_board.type = "step_board"
    step_board.current_depth = 1
    step_board.get_last_depth = get_last_depth
    step_board.style.marginTop = "1em"
    step_board.add_block = function(step_list){
        steps_creation_interface = find_parent_of_type(this, "steps_creation_interface")
        step_board = steps_creation_interface.step_board
        step_block = init_block(step_list, step_board.get_last_depth())
        step_board.appendChild(step_block)
    }    
    return step_board
}    


function get_last_depth(){
    if(find_parent_of_type(this, "step_board")){
        step_board = find_parent_of_type(this, "step_board")
        if(step_board.children.length>0){
            last_step = step_board.children[step_board.children.length-1]
            if(last_step.step === "para cada"){
                return last_step.depth + 1
            }else{
                return last_step.depth
            }
        }else{
            return 1
        }
    }
}


//--------------------- json build functions ---------------------------------

function build_json(){
    step_board = document.getElementById("step_board")
    var root_step = {
        step: "root",
        depth: 0,
        children: []
    }

    stack = [root_step]

    for(step_element of step_board.children){
        indent = step_element.depth - stack[stack.length-1].depth

        step_dict = get_step_json_format(step_element)

        if(indent == 1){
            stack[stack.length-1].children.push(step_dict)
            stack.push(step_dict)
        }else if(indent == 0){
            stack.pop()
            stack[stack.length-1].children.push(step_dict)
            stack.push(step_dict)
        }else if(indent < 0){
            for(var i = 0; i < -indent; i++){
                stack.pop()
            }
        }else if(indent>1){
            console.log("Indentation ERROR")
        }

    }
    document.getElementById("json_output").value = JSON.stringify(root_step)
    
}

function get_step_json_format(step_element){
    step_dict={
        step : step_element.step,
        depth : step_element.depth,
    }
    if(step_element.step == "para cada"){
        step_dict.step = "para_cada"
        step_dict.iterator = step_element.iterator_input.value
        step_dict.children = []
        if(step_element.iterable_select.value == "objeto"){
            step_dict.iterable = {objeto:{}}
            step_dict.iterable.objeto = step_element.iterable_params_div.children[0].children[0].value
        }else{
            step_dict.iterable = {call:{}}
            step_dict.iterable.call = {
                step: step_element.iterable_select.value,
                arguments:{}
            }
            for(param of step_element.iterable_params_div.children){
                step_dict.iterable.call.arguments[param.children[0].placeholder] = param.children[0].value
            }
        }
    }
    else {
        step_dict.arguments = {}
        for(child of step_element.children[0].children[0].children[1].children[0].children){
            step_dict.arguments[child.children[0].placeholder] = child.children[0].value
        }
    }
    return step_dict
}

//-------------- util -------------------------------

function get_this_texts_inside_each_tag(string_list, tag){
    html_step_options=""
    for (var i = 0; i < string_list.length; i++) {
        html_step_options = html_step_options + tag + string_list[i] + tag.split(" ")[0].replace('<', '</')+">\n"
    }
    return html_step_options
}

function get_step_names(step_list){
    step_names = []
    for(step of step_list){
        step_names.push(step.name)
    }
    return step_names
}

function get_params_element_list(step_name, step_list){
    if(step_name == "objeto"){
        object_div = document.createElement("DIV")
        object_div.className = "col-sm"
        object_div.innerHTML = `<input placeholder="objeto, ex: [1,2,3]" class="row form-control">`
        return object_div
    }else{
        'use strict'
        var step = get_step_info(step_name, step_list)
        var param_element_list = []
        //alert(step.mandatory_params)

        for(param of step.mandatory_params){
            var parameter = document.createElement("DIV")
            parameter.className = "col-sm"
            parameter.innerHTML = `<input placeholder="` + String(param) + `" class="row form-control">`
            parameter.children[0].placeholder = param
            param_element_list.push(parameter)
        }
        return param_element_list
    }
}

function get_index_in_parent(element){
    parent = element.parentElement
    for(var i=0; i<parent.children.length; i++){
        if(parent.children[i].id == element.id){
            return i
        }
    }
}

function get_step_info(step_name, step_list){
    for(step of step_list){
        if(step.name == step_name){
            return step
        }
    }
    console.log(step_name + " não está entre os passos do json passado no init.")
}

function hide(element){
    element.style.display = "none";
}

function show(element){
    element.style.display = "block";
}

function find_parent_of_type(element, type){
    if(element.type && element.type == type){
        return element
    }else {
        if(!element.parentElement){
            console.log("This element isn't inside an element of type " + type)
            return false
        }else{
            return find_parent_of_type(element.parentElement, type)
        }
    }
}


function genId(length=8) {
    var result = '';
    var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
    var charactersLength = characters.length;
    for (var i = 0; i < length; i++) {
        result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    return result;
}
