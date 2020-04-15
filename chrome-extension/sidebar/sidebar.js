let errors = {
    InvalidArgumentException: "Ivalid value passed as arguments."
}

function toggleElement(id){
    console.log("toggleElement: id=" + id);
    var el = document.getElementById(id);
    console.log("toggleElement: style=" + el.style.display);
    if(el.style.display == "none")
        el.style.display = "block";
    else
        el.style.display = "none"; 
}

function enableAddStep(){
    var select = document.getElementById("stepMenu");
    var btn = document.getElementById("addStep");

    if (select.options[select.selectedIndex].value == "default")
        btn.disabled = true;
    else
        btn.disabled = false;
}

function readXpath(input_id){
    console.log("reading xpath for " + input_id);
}

function copyInputText(input_id){
    console.log("copying input from " + input_id);
}

function genId(length=8) {
    var result = '';
    var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
    var charactersLength = characters.length;
    for (var i = 0; i < length; i++) {
        result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    return "-" + result + "-";
}

function dedentStep(stepId){
    const parent_div = document.querySelector("#" + stepId + " > .indentContainer");
    const indentation_lvl = parent_div.childElementCount;

    if (indentation_lvl > 0) {
        const child = document.querySelector("#" + stepId + " > .indentContainer > div:nth-child(1)");
        child.parentNode.removeChild(child);
    }
}

function indentStep(stepId){
    const new_div = document.createElement("div");
    new_div.className += "indent";
    document.querySelector("#" + stepId + " > .indentContainer").appendChild(new_div);
}

function moveStepUp(stepId){
    var e = $("#" + stepId);
    console.log("Up")
    console.log(stepId)
    console.log(e.prev().attr("id"))
    e.prev().insertAfter(e);
}

function moveStepDown(stepId) {
    var e = $("#" + stepId);
    if (e.next().attr("id") == "stepMenuContainer")
        return;
    e.next().insertBefore(e);
}

function deleStep(stepId){
    const child = document.querySelector("#" + stepId);
    child.parentNode.removeChild(child);
}

function getXpathHtml(xpath_id="", new_id="", label=""){
    if(xpath_id == "" && new_id == "")
        throw new InvalidOperationException(errors.InvalidArgumentException );
    else if(xpath_id == "")
        xpath_id == new_id + "XpathInput";

    if(label == "")
        label = "xpath";

    var events = [
        [xpath_id + "SelectSpan", function () { readXpath(xpath_id); }, "click"],
        [xpath_id + "CopySpan", function () { copyInputText(xpath_id); }, "click"],
    ]

    document.getElementById("collectorName").value = "Xpath id: " + xpath_id + "SelectSpan";

    var html = `
        <!-- begin xpath -->
        <div class=\"row\">
            <div class=\"col\"><label>${label}:</label></div>
        </div>
        <form>
            <div class=\"form-row\">
                <div class=\"col-1\">
                    <span
                        class=\"badge badge-light clickableSpan\"
                        id=\"${xpath_id}SelectSpan\"
                    >
                        <img src=\"icons/mouse-pointer-gray.svg\" alt=\"Selecionar\">
                    </span>
                </div>
                <div class=\"col-6\">
                    <input type=\"text\" class=\"form-control\" placeholder=\"xpath para elemento\" id=\"${xpath_id}\">
                </div>
                <div class=\"col-1\">
                    <span
                        class=\"badge badge-primary clickableSpan\"
                        id=\"${xpath_id}CopySpan\"
                    >
                        Copiar
                    </span>
                </div>
                <div class=\"col-1\">
                    <span class=\"badge badge-light clickableSpan\" onClick=\"\">
                        <img src=\"icons/help-circle.svg\" alt=\"Como usar\">
                    </span>
                </div>
            </div>
        </form>
        <!-- end xpath -->
    `;

    return [html, events]
}

function getClickStepHtml(new_id){
    const [xpathHtml, xpathEvents] = getXpathHtml(new_id = new_id)

    // envent target, function, event type
    var events = [] + xpathEvents;

    var html = `
        <div class=\"col\">
            <div class=\"row\">
                <div class=\"col\"><strong>Clique em um elemento</strong></div>
            </div>
    ` + xpathHtml + `
        </div>    
    `;

    return [html, events];
}

function getSelectStepHtml(new_id){
    var is_filled_dynamically = new_id + "IsFilledDynamically";
    var filled_after_step = new_id + "FilledAfterStep";
    var manage_dynamic_options = new_id + "ManageDynamicOptions";
    var static_options_to_ignore = new_id + "OptionToIgnore";

    const [xpathHtml, xpathEvents] = getXpathHtml(new_id = new_id)

    // envent target, function, event type
    var events = [
        [is_filled_dynamically, function () {
            toggleElement(filled_after_step);
            toggleElement(manage_dynamic_options);
            toggleElement(static_options_to_ignore);
        }, "onChange"],
    ] + xpathEvents;

    var html = `
        <div class=\"col\">
            <div class=\"row\">
                <div class=\"col\">
                    <strong>Selecione opção</strong>
                </div>
            </div>
            ` + xpathHtml + `
            <div class=\"row\">
                <div class=\"col\">
                    <div class=\"custom-control custom-switch\">
                        <input type=\"checkbox\" class=\"custom-control-input\" id=\"${is_filled_dynamically}\">
                        <label class=\"custom-control-label\" for=\"${is_filled_dynamically}\">Preenchido dinamicamente?</label>
                    </div>
                </div>
            </div>
            <div class=\"row\" id=\"${filled_after_step}\" style=\"display: none;\">
                <label class=\"col-4\">
                    <img src=\"icons/corner-down-right.svg\" alt=\"\"> Preenchido depois do passo:
                </label>
                <input type=\"text\" class=\"form-control col-1\" placeholder=\"1xca13\">
            </div>
            <div class=\"row\" id=\"${static_options_to_ignore}\" style=\"display: block;\">
                <label class=\"col-3\">
                    <img src=\"icons/corner-down-right.svg\" alt=\"\">
                    Ignorar opções:
                </label>
                <input type=\"text\" class=\"form-control col\" placeholder=\"cidade 1;cidade 2;(...)\">
                <span class=\"badge badge-light col-1 clickableSpan\">
                    <img src=\"icons/help-circle.svg\" alt=\"Como usar\">
                </span>
            </div>

            <div class=\"dropdown row\" id=\"${manage_dynamic_options}\" style=\"display: none;\">
                <button class=\"btn btn-primary dropdown-toggle\" type=\"button\" data-toggle=\"dropdown\"
                    aria-haspopup=\"true\" aria-expanded=\"false\"
                >
                    Gerenciar opções:
                </button>
                <div class=\"dropdown-menu\" aria-labelledby=\"dropdownMenuButton\">
                    <div class=\"form-check\">
                        <input class=\"form-check-input\" type=\"checkbox\" value=\"\">
                        <label class=\"form-check-label\">
                            Amazonas
                        </label>
                    </div>
                    <div class=\"form-check\">
                        <input class=\"form-check-input\" type=\"checkbox\" value=\"\">
                        <label class=\"form-check-label\">
                            Minas Gerais
                        </label>
                    </div>
                    <div class=\"form-check\">
                        <input class=\"form-check-input\" type=\"checkbox\" value=\"\">
                        <label class=\"form-check-label\">
                            Sao Paulo
                        </label>
                    </div>
                </div>
            </div>    
        </div>   
    `;

    return [html, events];
}

function getSaveStepHtml(new_id){
    var xpath_as_first_matches = new_id + "FirstMatch";
    var xpath_as_all_matches = new_id + "AllMatches";
    var save_content_table = new_id + "SaveContentTable";
    var manage_table_columns = new_id + "ManageTableColumns";
    var file_name = new_id + "FileName";
    var overwrite_file = new_id + "OverwriteFile";
    var append_to_file = new_id + "AppendToFile";
    
    const [xpathHtml, xpathEvents] = getXpathHtml(new_id = new_id)

    // envent target, function, event type
    var events = [] + xpathEvents;

    var html = `
        <div class=\"col\">
            <div class=\"row\">
                <div class=\"col\">
                    <strong>Salve dados</strong>
                </div>
            </div>
            ` + xpathHtml + `
            <div class=\"row\">
                <div class=\"col\">
                    <label class=\"\">xpath para:</label>
                </div>
            </div>
            <div class=\"row\">
                <div class=\"col\">
                    <form>
                        <div class=\"custom-control custom-radio\">
                            <input type=\"radio\" id=\"${xpath_as_first_matches}\" name=\"customRadio\" class=\"custom-control-input\" checked>
                            <label class=\"custom-control-label\" for=\"${xpath_as_first_matches}\">O primeiro que case com xpath</label>
                        </div>
                        <div class=\"custom-control custom-radio\">
                            <input type=\"radio\" id=\"${xpath_as_all_matches}\" name=\"customRadio\" class=\"custom-control-input\">
                            <label class=\"custom-control-label\" for=\"${xpath_as_all_matches}\">Todos que casem com xpath,
                                adicionando [x], x
                                de 1 até onde casar </label>
                        </div>
                    </form>
                </div>
            </div>

            <div class=\"row\">
                <div class=\"col\">
                    Preview:
                </div>
            </div>
            <div class=\"row\">
                <div class=\"col\">
                    <div class=\"tableWrapperScrollY my-custom-scrollbar\">
                        <table class=\"table\" id=\"${save_content_table}\">
                            <thead>
                                <tr>
                                    <th scope=\"col\">#</th>
                                    <th scope=\"col\">First</th>
                                    <th scope=\"col\">Last</th>
                                    <th scope=\"col\">Handle</th>
                                    <th scope=\"col\">blabla</td>
                                    <th scope=\"col\">blabla</td>
                                    <th scope=\"col\">blabla</td>
                                    <th scope=\"col\">blabla</td>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <th scope=\"row\">1</th>
                                    <td>Mark</td>
                                    <td>Otto</td>
                                    <td>@mdo</td>
                                    <td>blabla</td>
                                    <td>blabla</td>
                                    <td>blabla</td>
                                    <td>blabla</td>
                                </tr>
                                <tr>
                                    <th scope=\"row\">2</th>
                                    <td>Jacob</td>
                                    <td>Thornton</td>
                                    <td>@fat</td>
                                    <td>blabla</td>
                                    <td>blabla</td>
                                    <td>blabla</td>
                                    <td>blabla</td>
                                </tr>
                                <tr>
                                    <th scope=\"row\">3</th>
                                    <td>Larry</td>
                                    <td>the Bird</td>
                                    <td>@twitter</td>
                                    <td>blabla</td>
                                    <td>blabla</td>
                                    <td>blabla</td>
                                    <td>blabla</td>
                                </tr>
                                <tr>
                                    <th scope=\"row\">4</th>
                                    <td>Larry</td>
                                    <td>the Bird</td>
                                    <td>@twitter</td>
                                    <td>blabla</td>
                                    <td>blabla</td>
                                    <td>blabla</td>
                                    <td>blabla</td>
                                </tr>
                                <tr>
                                    <th scope=\"row\">5</th>
                                    <td>Larry</td>
                                    <td>the Bird</td>
                                    <td>@twitter</td>
                                </tr>
                                <tr>
                                    <th scope=\"row\">6</th>
                                    <td>Larry</td>
                                    <td>the Bird</td>
                                    <td>@twitter</td>
                                    <td>blabla</td>
                                    <td>blabla</td>
                                    <td>blabla</td>
                                    <td>blabla</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div class=\"dropdown\">
                <button class=\"btn btn-primary dropdown-toggle\" type=\"button\" data-toggle=\"dropdown\" aria-haspopup=\"true\"
                    aria-expanded=\"false\" id=\"${manage_table_columns}\">
                    Gerenciar colunas da tabela:
                </button>
                <div class=\"dropdown-menu\" aria-labelledby=\"dropdownMenuButton\">
                    <div class=\"form-check\">
                        <input class=\"form-check-input\" type=\"checkbox\" value=\"\">
                        <label class=\"form-check-label\">
                            Amazonas
                        </label>
                    </div>
                    <div class=\"form-check\">
                        <input class=\"form-check-input\" type=\"checkbox\" value=\"\">
                        <label class=\"form-check-label\">
                            Minas Gerais
                        </label>
                    </div>
                    <div class=\"form-check\">
                        <input class=\"form-check-input\" type=\"checkbox\" value=\"\">
                        <label class=\"form-check-label\">
                            Sao Paulo
                        </label>
                    </div>
                </div>
            </div>

            <div class=\"row\">
                <div class=\"col\">
                    <label>Nome do arquivo</label>
                    <input type=\"text\" class=\"form-control\" placeholder=\"./(...)\" id=\"${file_name}\">
                </div>
            </div>

            <div class=\"row\">
                <div class=\"col\">
                    <form>
                        <div class=\"custom-control custom-radio\">
                            <input type=\"radio\" id=\"${overwrite_file}\" name=\"customRadio\" class=\"custom-control-input\" checked>
                            <label class=\"custom-control-label\" for=\"${overwrite_file}\">Sobrescrever arquivo se ja
                                existe</label>
                        </div>
                        <div class=\"custom-control custom-radio\">
                            <input type=\"radio\" id=\"${append_to_file}\" name=\"customRadio\" class=\"custom-control-input\">
                            <label class=\"custom-control-label\" for=\"${append_to_file}\">Adiiconar dados ao final do arquivo
                                (assume
                                que arquivo foi criado por outra execução deste coletor)</label>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    `;
    
    return [html, events];
}

function getIFrameStepHtml(new_id){
    const [xpathHtml, xpathEvents] = getXpathHtml(new_id = new_id)

    // envent target, function, event type
    var events = [] + xpathEvents;

    var html = `
        <div class=\"col\">
            <div class=\"row\">
                <div class=\"col\"><strong>Mude para o iframe</strong></div>
            </div>
            ` + xpathHtml + `
        </div>    
    `;

    return [html, events];
}

function getDownloadHtml(new_id){
    var file_name = new_id = "FileName";

    const [xpathHtml, xpathEvents] = getXpathHtml(new_id = new_id)

    // envent target, function, event type
    var events = [] + xpathEvents;

    var html = `
        <div class=\"col\">
            <div class=\"row\">
                <div class=\"col\">
                    <strong>Baixe o arquivo</strong>
                </div>
            </div>
            ` + xpathHtml + `
            <div class=\"row\">
                <div class=\"col\">
                    <label>Salvar na pasta</label>
                    <input type=\"text\" class=\"form-control\" placeholder=\"./(...)\" id=\"${file_name}\">
                </div>
            </div>
        </div>        
    `;

    return [html, events];
}

function getPaginationHtml(new_id){
    const [xpathHtmlNextPageBtn, xpathEventsNextPageBtn] = getXpathHtml(
        xpath_id = new_id + "NextPageBtn", label = "Xpath para botão de próxima página")
    const [xpathHtmlMaxPagesInfo, xpathEventsMaxPagesInfo] = getXpathHtml(
        xpath_id = new_id + "MaxPagesInfo", label = "Xpath para número máximo de páginas")

    // envent target, function, event type
    var events = [] + xpathEventsNextPageBtn + xpathEventsMaxPagesInfo;

    var html = `
        <div class=\"col\">
            <!--  -->
            <div class=\"row\">
                <div class=\"col\">
                    <strong>Para cada página</strong>
                </div>
            </div>
            ` + xpathHtmlNextPageBtn + `
            ` + xpathHtmlMaxPagesInfo + `
        </div>
    `;

    return [html, events];
}

function getCaptchaHtml(new_id) {
    const [xpathHtml, xpathEvents] = getXpathHtml(new_id = new_id)

    // envent target, function, event type
    var events = [] + xpathEvents;

    var html = `
        <div class=\"col\">
            <div class=\"row\">
                <div class=\"col\">
                    <strong>Quebre o captcha</strong>
                </div>
            </div>
            ` + xpathHtml + `
        </div>
    `;

    return [html, events];
}

function getIfHtml(new_id){
    const [xpathHtml, xpathEvents] = getXpathHtml(new_id = new_id)

    // envent target, function, event type
    var events = [] + xpathEvents;

    var html = `
        <div class=\"col\">
            <div class=\"row\">
                <div class=\"col\">
                    <strong>Se detectar elemento</strong>
                </div>
            </div>
            ` + xpathHtml + ` 
        </div>
    `;

    return [html, events];
}

function insertStep(new_id, step_type) {
    var innerElements = ""
    if (step_type == "default") {
        console.log("ERROR: Received default option. Should not fall here")
        return "";
    } else if (step_type == "click") {
        [innerElements, newEvents] = getClickStepHtml(new_id);
    } else if (step_type == "select") {
        [innerElements, newEvents] = getSelectStepHtml(new_id);
    } else if (step_type == "save") {
        [innerElements, newEvents] = getSaveStepHtml(new_id);
    } else if (step_type == "iframe") {
        [innerElements, newEvents] = getIFrameStepHtml(new_id);
    } else if (step_type == "download") {
        [innerElements, newEvents] = getDownloadHtml(new_id);
    } else if (step_type == "pages") {
        [innerElements, newEvents] = getPaginationHtml(new_id);
    } else if (step_type == "captcha") {
        [innerElements, newEvents] = getCaptchaHtml(new_id);
    } else if (step_type == "if") {
        [innerElements, newEvents] = getIfHtml(new_id);
    }
    document.querySelector("#" + new_id + "Container > div.col > div.stepStuff").innerHTML = innerElements.trim();

    for (var [id, fun, type] of newEvents) {
        addEventListener(id, fun, type);
    }
}

function getStepContainerHtml(new_id){
    const new_container_id = new_id + "Container";
    return [
        `
        <div class=\"stepContainer row\" id=\"${new_container_id}\">
            <div class=\"col-1 indentContainer\"></div>
            <div class=\"col\">
                <div class=\"stepStuff row\">
                </div>
                <div class=\"row justify-content-end manageSteps\">
                    <div class=\"col-2\">Gerenciar Passo:</div>
                    <div class=\"col-1\">
                        <span
                            id=\"dedent${new_container_id}\"
                            class=\"badge badge-light clickableSpan\"
                        >
                            <img src=\"icons/arrow-left-black.svg\" alt=\"Selecionar\">
                        </span>
                    </div>
                    <div class=\"col-1\">
                        <span
                            id=\"indent${new_container_id}\"
                            class=\"badge badge-light clickableSpan\"
                        >
                            <img src=\"icons/arrow-right-black.svg\" alt=\"Selecionar\">
                        </span>
                    </div>
                    <div class=\"col-1\">
                        <span
                            id=\"moveStepUp${new_container_id}\"
                            class=\"badge badge-light clickableSpan\"
                        >
                            <img src=\"icons/arrow-up-black.svg\" alt=\"Selecionar\">
                        </span>
                    </div>
                    <div class=\"col-1\">
                        <span
                            id=\"moveStepDown${new_container_id}\"
                            class=\"badge badge-light clickableSpan\"
                        >
                            <img src=\"icons/arrow-down-black.svg\" alt=\"Selecionar\">
                        </span>
                    </div>
                    <div class=\"col-1\">
                        <span
                            id=\"deleteStep${new_container_id}\"
                            class=\"badge badge-light clickableSpan\"
                        >
                            <img src=\"icons/x.svg\" alt=\"Selecionar\">
                        </span>
                    </div>
                </div>
            </div>
        </div>    
        `, 
        [
            ["dedent"+new_container_id, function(){dedentStep(new_container_id);}, "click"], 
            ["indent"+new_container_id, function(){indentStep(new_container_id);}, "click"], 
            ["moveStepUp"+new_container_id, function(){moveStepUp(new_container_id);}, "click"], 
            ["moveStepDown"+new_container_id, function(){moveStepDown(new_container_id);}, "click"], 
            ["deleteStep"+new_container_id, function(){deleStep(new_container_id);}, "click"], 

        ]
    ];
}

function insertContainer(new_id){
    const [htmlString, newEvents] = getStepContainerHtml(new_id);

    const div = document.createElement('div');
    div.innerHTML = htmlString.trim();

    const stepsContainer = document.getElementById("stepsContainer");
    const stepContainer = document.getElementById("stepMenuContainer");
    stepsContainer.insertBefore(div.firstChild, stepContainer);

    for (var [id, fun, type] of newEvents) {
        addEventListener(id, fun, type);
    }
}

function addStep() {
    const select = document.getElementById("stepMenu");
    const btn = document.getElementById("addStep");
    const new_id = "Step" + genId();
    const step_type = select.options[select.selectedIndex].value;
    if (step_type == "default"){
        return;
    }

    insertContainer(new_id);
    insertStep(new_id, step_type);    
    btn.disabled = true;
    select.value = "default";
}

function addEventListener(id, fun, type="click"){
    var iterations = 0;
    // waits until element is acessible, checks every 100ms
    var checkExist = setInterval(function () {
        if (document.getElementById(id)) {
            console.log("addEventListener: found " + id + "!!!! Creating event...");
            var el = document.getElementById(id);
            el.addEventListener(type, fun, false); 
            clearInterval(checkExist);
        }
        iterations++;
        if (iterations > 20){
            console.log("addEventListener: Unable to find " + id);
            clearInterval(checkExist);
        }
    }, 100); 
}

function load(){
    var el = document.getElementById("rotateAddress");

    addEventListener("rotateAddress", function () {
        toggleElement("maxCallsPerAddress");
    }); 

    addEventListener("stepMenu", function(){enableAddStep();}, "change")

    addEventListener("addStep", function () {
        addStep();
    }); 
}

// receives xpath of selected element from devtools.js
chrome.extension.onMessage.addListener(
    function (request, sender, sendResponse) {
        document.getElementById("collectorName").value = request.content;
    }
);

document.addEventListener("DOMContentLoaded", load, false);

// TODO:
// Make all in insertStep return a list of [html, events], turn all inline functions in event handlers, like in insert Container
// adicionar funcionalidade do clique no xpath DONE
//     mudar cor do icone de mouse quando ele for selecionado
// implementar funcionalidade de copiar xpath com o botao Copiar
// Select: implementar funcionalidade de detectar opções estaticas e inserir no gerenciador
// Select: implementar funcionalidade de marcar textos separados por ;
// Save: implementar funcionalidade de tentar casar elementos com xpath e detectar atributos
// checar todas as funcionalidades de cada passo
// xpath: highlight do elemento selecionado?

