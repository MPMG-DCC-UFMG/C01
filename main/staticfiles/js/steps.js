/**
 * Loads the json with the steps information and init the steps creations interface
 * @param  {Node} interface_root_element [The element that will be the root of the entire interface]
 * @param  {Node} output_element [The element where the steps json are going to be placed]
 * @param  {String} json_path [The path of the json with the steps information]
 */
function load_steps(interface_root_element, output_element, json_path="/static/json/step_signatures.json"){
    var xmlhttp = new XMLHttpRequest();
    
<<<<<<< HEAD
    xmlhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        step_list = JSON.parse(this.response, function (key, value){
            if (typeof value == "string"){
                return value.replace(/_/g, " ")
            }
            return value;
        })
        step_list = step_list.concat(JSON.parse('{"name":"object", "mandatory_params":["ex: [1,2,3]"], "optional_params":{}}'))
        step_list = step_list.concat(JSON.parse('{"name":"for each", "mandatory_params":[], "optional_params":{}}'))
        step_list = step_list.concat(JSON.parse('{"name":"for each page in", "mandatory_params":[], "optional_params":{}}'))
        init_steps_creation_interface(interface_root_element, output_element, step_list)
      }
    };
=======
    if (iframe_element.style.display === "none"){
        iframe_element.style.display = "block";
        document.getElementById("myButton").innerText = "Esconder Website";
    }
    else{
        iframe_element.style.display = "none";
        document.getElementById("myButton").innerText = "Mostrar Website";
    }
}
>>>>>>> 8af382f4b42ca97559998a27872ae886b25e305a

    xmlhttp.open("GET", json_path, true);
    xmlhttp.send();
}



//-------------- creation_interface ------------------------------


/**
 * Init the steps creation interface, that is, the save button, the add step button and the step board.
 * @param  {Node} interface_root_element The element that will be the root of the entire interface.
 * @param  {Node} output_element The element where the steps json are going to be placed.
 * @param  {List} step_list A list with the steps information.
 */

function init_steps_creation_interface(interface_root_element, output_element, step_list){
    steps_creation_interface = document.createElement("div")
    steps_creation_interface.type= "steps_creation_interface"
    
    step_controler = document.createElement("div")
    step_controler.type = "step_controler"
    step_board = init_step_board(step_list)


    add_block_button = document.createElement("a")
    add_block_button.className="btn btn-primary step-controler-buttons"
    add_block_button.style.color = "white"
    add_block_button.onclick = function(){step_board.add_block(step_list)}
    add_block_button.innerText = "Add step"


    save_button = document.createElement("button")
    save_button.innerText = "Save steps"
    save_button.className="btn btn-primary step-controler-buttons"
    save_button.style.color = "white"
    interface_root_element.save_button = save_button
    interface_root_element.save_button.onclick = function(){build_json(step_board, output_element)}

    step_controler.appendChild(add_block_button)
    step_controler.appendChild(save_button)
    steps_creation_interface.appendChild(step_controler)
    steps_creation_interface.appendChild(step_board)
    steps_creation_interface.step_controler = step_controler
    steps_creation_interface.step_board = step_board
    steps_creation_interface.step_board.type

    interface_root_element.insertBefore(steps_creation_interface, interface_root_element.children[0])
    interface_root_element.type = "root"
    interface_root_element.steps_creation_interface = steps_creation_interface
    interface_root_element.step_json_input = output_element

}

//------------------- step board ------------------------------

/**
 * Init the step_board, the element that will store the steps created by the user.
 * @param  {List} step_list [A list with the steps information]
 * @return {Node} step_board [The step_board html element already initialized]
 */
function init_step_board(step_list){
    step_board = document.createElement('DIV')
    step_board.type = "step_board"
    step_board.current_depth = 1
    step_board.get_last_depth = get_last_depth
    step_board.style.marginTop = "1em"
    step_board.style.marginBottom = "1em"
    step_board.add_block = function(step_list, index = -1){
        steps_creation_interface = find_parent_with_attr_worth(this, "steps_creation_interface")
        step_board = steps_creation_interface.step_board
        step_block = init_block(step_list, step_board.get_last_depth())
        if(index != -1){
            step_board.insertBefore(step_block, step_board.children[index])
        }else{
            step_board.appendChild(step_block)
        }
    }    
    return step_board
}    

/**
 * Function that will be setted to be a method of the step_board
 * This function analyses the last step in the step_board to answer what 
 * should be the depth of the next step to be added.
 * @return {Number} The last depth or in case of the last step be a 
 *                  loop step, the last depth + 1
 */
function get_last_depth(){
    if(find_parent_with_attr_worth(this, "step_board")){
        step_board = find_parent_with_attr_worth(this, "step_board")
        if(step_board.children.length>0){
            last_step = step_board.children[step_board.children.length-1]
            if(last_step.step.name == "for each" || last_step.step.name == "for each page in"){
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

/**
 * This function gets the steps added by user in the step_board and builds the
 * steps json, that describes the steps to be performed on the page to be crawled. 
 * @param {Node} step_board The html element with all the steps setted by user.
 * @param {Node} output_element The html element that is going to receive the steps json in its value.
 */
function build_json(step_board, output_element){
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
    output_element.value = JSON.stringify(root_step)
    
}

/**
 * This function gets a block and extract its information to build the json step represtation with this.
 * @param {Node} block The html element that represents a step and was parameterized by the user.
 * @return {Dict} the step that was parameterized in the block, but now in the json steps represtation.
 */
function get_step_json_format(block){
    param_name = block.step.name.replace(/ /g, "_")
    step_dict={
        step : param_name,
        depth : block.depth,
    }
    if(param_name == "for each"){
        step_dict.iterator = block.iterator_input.value
        step_dict.children = []
        step_dict.iterable = {call:{}}
        step_dict.iterable.call = {
            step: block.iterable_select.value,
            arguments:{}
        }
        for(param of block.params){
            step_dict.iterable.call.arguments[param.children[0].placeholder.replace(/ /g, "_")] = param.children[0].value
        }
    }else if(param_name == "for each page in"){
        step_dict.children = []
        for(param of block.params){
            step_dict[param.children[0].placeholder.replace(/ /g, "_")] = param.children[0].value
        }
    }else {
        step_dict.arguments = {}
        for(param of block.params){
            step_dict.arguments[param.children[0].placeholder.replace(/ /g, "_")] = param.children[0].value
        }
    }
    return step_dict
}

//-------------- util -------------------------------

/**
 * This function get all the mandatory parameters of a step, and return them but in input format in a list.
 * @param {String} step_name The name of the step to get the inputs representing the parameters.
 * @param {List} step_list The list of steps that conteing the step named with the step_name value.
 * @retuns {List} A list with the inputs represting the mandatory parameters of the step.
 */
function get_params_element_list(step_name, step_list){
    if(step_name == "objeto"){
        object_div = document.createElement("DIV")
        object_div.className = "col-sm"
        object_div.innerHTML = `<input placeholder="objeto, ex: [1,2,3]" class="row form-control">`
        return [object_div.children[0]]
    }else{
        var step = get_step_info(step_name, step_list)
        var param_element_list = []

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


/**
 * This function puts one by one the strings of a list inside a tag.
 * @param {List} string_list A list of strings
 * @param {String} tag A tag
 * @retuns {String} All the tags with the string inside concatenated.
 */
function get_this_texts_inside_each_tag(string_list, tag){
    html_tags=""
    for (var i = 0; i < string_list.length; i++) {
        html_tags = html_tags + tag + string_list[i] + tag.split(" ")[0].replace('<', '</')+">\n"
    }
    return html_tags
}

/**
 * This function get the steps name inside a list of steps.
 * @param {List} step_list The list of steps on json steps format.
 * @retuns {List} A list with the names of all the steps inside the step_list.
 */
function get_step_names(step_list){
    step_names = []
    for(step of step_list){
        step_names.push(step.name)
    }
    return step_names
}


/**
 * This function gets the index of an element in its parent childrens.
 * @param {Node} element The element by which the index will be found.
 * @retuns {Number} The index of the elemente in its parent children.
 */
function get_index_in_parent(element){
    parent = element.parentElement
    for(var i=0; i<parent.children.length; i++){
        if(parent.children[i] == element){
            return i
        }
    }
}

/**
 * This function gets the information of an step inside a step_list by its name.
 * @param {String} step_name The name of the step.
 * @param {List} step_list The list of steps that conteing the step named with the step_name value.
 * @retuns {Dict} A dictionary with the information of the step.
 */
function get_step_info(step_name, step_list){
    for(step of step_list){
        if(step.name == step_name){
            return step
        }
    }
    console.log(step_name + " não está entre os passos do json passado no init.")
}

/**
 * This function hides an element.
 * @param {Node} element Element to be hided.
 */
function hide(element){
    element.style.display = "none";
}

/**
 * This function shows an hided element.
 * @param {Node} element Element to be showed.
 */
function show(element){
    element.style.display = "block";
}

/**
 * This function is very important, it finds in the ancestors of an element,
 * that with an attribute setted with an value.
 * @param {Node} element Starting element.
 * @param {Any} value The value to be verificated in the attr of each ancestor.
 * @param {String} attr The attribute that should be with the value.
 * @retuns {Node} The ancestor element that have the value property with the value passed by parameter.
 */
function find_parent_with_attr_worth(element, value, attr = "type"){
    if(element[attr] && element[attr] == value){
        return element
    }else {
        if(!element.parentElement){
            console.log("This element isn't inside an element with attribute \""+ attr + "\" storing the value " + value)
            return false
        }else{
            return find_parent_with_attr_worth(element.parentElement, value)
        }
    }
}

