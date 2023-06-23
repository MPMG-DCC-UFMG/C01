statusInterval = null //global var to control call interval
document.addEventListener('DOMContentLoaded',
    function () {
        var instance_id = document.getElementById("last_instance_id").innerText.trim();
        var last_as_running = document.getElementById("instance_running").innerText.trim() == "True";

        if(instance_id != "None"){
            tail_logs(instance_id);
            if (!WAITING_ON_QUEUE)
                status_instance(instance_id);
        }

        if(last_as_running){
            tail_f_logs(instance_id);
            if (!WAITING_ON_QUEUE)
                status_f_instance(instance_id);
        }
    },
    false
);

function show_hide_instances(){
    var instances_lines = Array.prototype.slice.apply(document.querySelectorAll(".multinstancias"));
    instances_lines.forEach((instance) => {
        instance.classList.toggle("hidden");
    });
}

function tail_logs(instance_id){
    let progress_file_failure = $('#progress-file-failure');
    let progress_file_success = $('#progress-file-success');
    let progress_file_previously_crawled = $('#progress-file-previously-crawled');

    let progress_page_success = $('#progress-page-success');
    let progress_page_failure = $('#progress-page-failure');
    let progress_page_duplicated = $('#progress-page-duplicated');
    let progress_page_previously_crawled = $('#progress-page-previously-crawled');

    // calls tail log view and set logs
    $.ajax("/tail_log_file/" + instance_id).done(function(data) {
            var response = data;
            
            if (response["files_found"] != 0) {

                let success_rate = (response["files_success"] / response["files_found"]) * 100;
                let error_rate = (response["files_error"] / response["files_found"]) * 100;
                let previously_crawled_rate = (response["files_previously_crawled"] / response["files_found"]) * 100;
                let total_processed = response["files_error"] + response["files_previously_crawled"] + response["files_success"];

                progress_file_success.css("width", `${success_rate.toFixed(2)}%`);
                progress_file_success.text(`${success_rate.toFixed(2)}%`);
                progress_file_success.prop('title', `${success_rate.toFixed(2)}% (${response["files_success"]}/${response["files_found"]}) de sucesso ao baixar os arquivos encontrados`);

                progress_file_failure.css("width", `${error_rate.toFixed(2)}%`);
                progress_file_failure.text(`${error_rate.toFixed(2)}%`);
                progress_file_failure.prop('title', `${error_rate.toFixed(2)}% (${response["files_error"]}/${response["files_found"]}) de erro ao baixar os arquivos encontrados`);

                progress_file_previously_crawled.css("width", `${previously_crawled_rate.toFixed(2)}%`);
                progress_file_previously_crawled.text(`${previously_crawled_rate.toFixed(2)}%`);
                progress_file_previously_crawled.prop('title', `${previously_crawled_rate.toFixed(2)}% (${response["files_previously_crawled"]}/${response["files_found"]}) de arquivos coletados em coletas anteriores (duplicados)`);

                let remaining_progress = (response['files_found'] - total_processed) / response['files_found'] * 100;

                $('#remaining-progress-file').prop('title', `Faltam ${remaining_progress.toFixed(2)}% dos arquivos para coletar.`);
                $('#progress-files-total').text(`${total_processed} de ${response["files_found"]}`);
            }
            
            if (response["pages_found"] != 0) {
                let success_rate = (response["pages_success"] / response["pages_found"]) * 100;
                let error_rate = (response["pages_error"] / response["pages_found"]) * 100;
                let duplicated_rate = (response["pages_duplicated"] / response["pages_found"]) * 100;
                let previously_crawled_rate = (response["pages_previously_crawled"] / response["pages_found"]) * 100;
                let total_processed = (response["pages_duplicated"] + response["pages_previously_crawled"] + response["pages_success"] + response["pages_error"]);

                progress_page_success.css("width", `${success_rate.toFixed(2)}%`);
                progress_page_success.text(`${success_rate.toFixed(2)}%`);
                progress_page_success.prop('title', `${success_rate.toFixed(2)}% (${response["pages_success"]}/${response["pages_found"]}) de sucesso ao coletar as páginas encontradas`);

                progress_page_failure.css("width", `${error_rate.toFixed(2)}%`);
                progress_page_failure.text(`${error_rate.toFixed(2)}%`);
                progress_page_failure.prop('title', `${error_rate.toFixed(2)}% (${response["pages_error"]}/${response["pages_found"]}) de erro ao coletar as páginas encontradas`);

                progress_page_duplicated.css("width", `${duplicated_rate.toFixed(2)}%`);
                progress_page_duplicated.text(`${duplicated_rate.toFixed(2)}%`);
                progress_page_duplicated.prop('title', `${duplicated_rate.toFixed(2)}% (${response["pages_duplicated"]}/${response["pages_found"]}) de páginas duplicadas encontradas`);

                progress_page_previously_crawled.css("width", `${previously_crawled_rate.toFixed(2)}%`);
                progress_page_previously_crawled.text(`${previously_crawled_rate.toFixed(2)}%`);
                progress_page_previously_crawled.prop('title', `${previously_crawled_rate.toFixed(2)}% (${response["pages_previously_crawled"]}/${response["pages_found"]}) de páginas coletadas em coletas anteriores (duplicadas)`);

                let remaining_progress = (response['pages_found'] - total_processed) / response['pages_found'] * 100;

                $('#remaining-progress-page').prop('title', `Faltam ${remaining_progress.toFixed(2)}% das páginas para coletar.`);
                $('#progress-pages-total').text(`${total_processed} de ${response["pages_found"]}`);
            }

            if(response["out"].length != 0)
                document.getElementById("stdout_tail").innerText = response["out"]
            else
                document.getElementById("stdout_tail").innerText = "Arquivo em branco."

            if (response["err"].length != 0)
                document.getElementById("stderr_tail").innerText = response["err"]
            
            else
                document.getElementById("stderr_tail").innerText = "Arquivo em branco."

            document.getElementById("stdout_tail_update").innerText = "Última atualização: " + response["time"]
            document.getElementById("stderr_tail_update").innerText = "Última atualização: " + response["time"]
        }
    );
}

function tail_f_logs(instance_id){
    // Calls tail_logs every 5 seconds
    setInterval(
        function(){tail_logs(instance_id);},
        5000
    );
}

function status_instance(instance_id){
    var xhr = new XMLHttpRequest();

    var stopBtn = document.getElementById("stopBtn")
    var runBtn = document.getElementById("runBtn")
    var testBtn = document.getElementById("testBtn")

    xhr.onreadystatechange = function () {
        // test finished
        if (RUNNING_TEST_MODE) {
            if (this.readyState == 4 && this.status == 404)
                location.reload();
        } else if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);

            if(response["running"] == true){
                document.getElementById("crawler_status").innerHTML = '<span class="badge badge-success">Rodando</span>'
                stopBtn.classList.remove("disabled")
                if (stopBtn.hasAttribute("dataref")){
                    stopBtn.setAttribute("href", stopBtn.getAttribute("dataref"))
                    stopBtn.removeAttribute("dataref")
                }
                runBtn.classList.add("disabled")
                if (runBtn.hasAttribute("href")){
                    runBtn.setAttribute("dataref", runBtn.getAttribute("href"))
                    runBtn.removeAttribute("href")
                }
            }else{
                clearInterval(statusInterval)
                document.getElementById("crawler_status").innerHTML = '<span class="badge badge-warning">Parado</span>'
                stopBtn.classList.add("disabled")
                if (stopBtn.hasAttribute("href")){
                    stopBtn.setAttribute("dataref", stopBtn.getAttribute("href"))
                    stopBtn.removeAttribute("href")
                }
                
                runBtn.classList.remove("disabled")
                testBtn.classList.remove("disabled")

                if (runBtn.hasAttribute("dataref")){
                    runBtn.setAttribute("href", runBtn.getAttribute("dataref"))
                    runBtn.removeAttribute("dataref")
                }
            }
        }
    };

    xhr.open("GET", "/api/instances/"+instance_id, true);
    xhr.send();
}

function status_f_instance(instance_id){
    // Calls status_instance every 0.5 seconds while running
    statusInterval=setInterval(
        function(){ status_instance(instance_id);},
        500
    );
}

function exit_crawler_queue(queue_item_id) {
    let remove_queue_item_address = CRAWLER_QUEUE_API_ADDRESS + `remove_item?queue_item_id=${queue_item_id}`;
    UPDATING_SCHEDULER_CONFIG = true;

    $.ajax({
        url: remove_queue_item_address,
        type: 'get',
        dataType: 'json',
        async: false,
        success: function (data) {
            location.reload();
        },
        error: function (data) {
            alert('Houve um erro ao remover o item da fila!');
        }
    });
}

function ms2text(ms) {
    let secs = Math.floor(ms / 1000);

    let hours = Math.floor(secs / 3600);
    secs -= hours * 3600;

    let minutes = Math.floor(secs / 60);
    secs -= minutes * 60;

    if (hours > 0)
        return `-${hours}h ${minutes}min ${secs}s`;
    
    if (minutes > 0)
        return `-${minutes}min ${secs}s`;

    return `-${secs}s`;
}

function update_test_runtime_label() {
    if (!RUNNING_TEST_MODE)
        return;

    let testing_crawler_info = $('#testing-crawler-info');

    let now = (new Date()).getTime();
    let remaing_time = TEST_RUNTIME - (now - TEST_STARTED_AT);

    setInterval(() => {
        if (remaing_time < 0)
            location.reload();

        testing_crawler_info.text(`Testando coletor (${ms2text(remaing_time)})`);

        now += 1000;
        remaing_time = TEST_RUNTIME - (now - TEST_STARTED_AT);

    }, 1000);
}

$(document).ready(function () {
    update_test_runtime_label();
});
// Initiates all popovers on the page
$(function () {
    $('[data-toggle="popover"]').popover()
})
