// TODO replace this
export function load_step_list(callback) {
    const json_path = "/static/json/steps_signature.json"
    let step_list_complete = []
    let xmlhttp = new XMLHttpRequest()
    xmlhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        let step_list = JSON.parse(this.response, function (key, value){
            return value
        })

        step_list = step_list.concat(JSON.parse('{"name": "para_cada", "name_display" : "Para cada", "executable_contexts": ["page", "tab", "iframe"], "mandatory_params":["iterator"], "optional_params":[], "field_options": {"iterator": { "field_type": "text", "input_placeholder": "opção" }}, "inner_step":  "iterable" }'))
        step_list = step_list.concat(JSON.parse('{"name": "enquanto", "name_display" : "Enquanto", "executable_contexts": ["page", "tab", "iframe"], "mandatory_params":["invert"], "optional_params":[], "field_options": {"invert": { "field_type": "checkbox", "checkbox_label": "Inverter" }}, "inner_step":  "condition" }'))
        step_list = step_list.concat(JSON.parse('{"name": "se", "name_display" : "Se", "executable_contexts": ["page", "tab", "iframe"], "mandatory_params":["invert"], "optional_params":[], "field_options": {"invert": { "field_type": "checkbox", "checkbox_label": "Inverter" }}, "inner_step": "condition" }'))
        step_list = step_list.concat(JSON.parse('{"name": "atribuicao", "name_display" : "Atribuição", "executable_contexts": ["page", "tab", "iframe"], "mandatory_params":["target"], "optional_params":[], "field_options": {"target": { "field_type": "text", "input_placeholder": "opção" }}, "inner_step":  "source" }'))
        step_list = step_list.concat(JSON.parse('{"name": "abrir_em_nova_aba", "name_display" : "Abrir em nova aba", "executable_contexts": ["page", "tab"], "mandatory_params":["link_xpath"], "optional_params":[], "field_options": {"link_xpath": { "field_type": "text", "input_placeholder": "xpath do link" }}}'))
        step_list = step_list.concat(JSON.parse('{"name": "fechar_aba", "name_display" : "Fechar aba", "executable_contexts": ["tab"], "mandatory_params":[], "optional_params":[]}'))
        step_list = step_list.concat(JSON.parse('{"name": "executar_em_iframe", "name_display" : "Executar em iframe", "executable_contexts": ["page", "tab", "iframe"], "mandatory_params":["xpath"], "optional_params":[], "field_options": {"xpath": { "field_type": "text", "input_placeholder": "xpath do iframe" }}}'))
        step_list = step_list.concat(JSON.parse('{"name": "sair_de_iframe", "name_display" : "Sair de iframe", "executable_contexts": ["iframe"], "mandatory_params":[], "optional_params":[]}'))
        step_list = step_list.concat(JSON.parse('{"name": "screenshot", "name_display" : "Screenshot", "executable_contexts": ["page", "tab", "iframe"], "mandatory_params":[], "optional_params":[]}'))

        step_list_complete = step_list
        callback(step_list_complete)
      }
    };

    xmlhttp.open("GET", json_path, true)
    xmlhttp.send()
}

/**
 * This function gets a function's parameter name and returns its corresponding
 * display name.
 * @param {String} the parameter's name.
 * @retuns {String} the parameter's placeholder name.
 */
export function param_to_placeholder(param){
    let param_display;

    switch(param){
        case "opcao":
            param_display = "opção"
            break;
        case "xpath_dos_botoes":
            param_display = "xpath dos botões"
            break;
        case "numero_xpaths":
            param_display = "número de xpaths"
            break;
        case "funcao_preprocessamento":
            param_display = "função de pré-processamento"
            break;
        case "objeto":
            param_display = "ex: [1,2,3]"
            break;
        case "link_xpath":
            param_display = "xpath do link"
            break;
        default:
            param_display = String(param).replaceAll("_", " ")
            break;
    }

    return param_display
}
