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
    // calls tail log view and set logs
    $.ajax("/tail_log_file/" + instance_id).done(function(data) {
            var response = data;
            
            if (response["files_found"] != 0) {

                let success_rate = (response["files_success"] / response["files_found"]) * 100;
                let error_rate = (response["files_error"] / response["files_found"]) * 100;
                let total_processed = response["files_error"] + response["files_success"];

                $('#progress-file-success').css("width", `${success_rate.toFixed(2)}%`);
                $('#progress-file-success').text(`${success_rate.toFixed(2)}%`);
                $('#progress-file-success').prop('title', `${success_rate.toFixed(2)}% (${response["files_success"]}/${response["files_found"]}) de sucesso ao baixar os arquivos encontrados`);

                $('#progress-file-failure').css("width", `${error_rate.toFixed(2)}%`);
                $('#progress-file-failure').text(`${error_rate.toFixed(2)}%`);
                $('#progress-file-failure').prop('title', `${error_rate.toFixed(2)}% (${response["files_error"]}/${response["files_found"]}) de erro ao baixar os arquivos encontrados`);


                let remaining_progress = (response['files_found'] - total_processed) / response['files_found'] * 100;

                $('#remaining-progress-file').prop('title', `Faltam ${remaining_progress.toFixed(2)}% dos arquivos para coletar.`);
                $('#progress-files-total').text(`${total_processed} de ${response["files_found"]}`);
            }
            
            if (response["pages_found"] != 0) {
                let success_rate = (response["pages_success"] / response["pages_found"]) * 100;
                let error_rate = (response["pages_error"] / response["pages_found"]) * 100;
                let duplicated_rate = (response["pages_duplicated"] / response["pages_found"]) * 100;
                let total_processed = (response["pages_duplicated"] + response["pages_success"] + response["pages_error"]);

                $('#progress-page-success').css("width", `${success_rate.toFixed(2)}%`);
                $('#progress-page-success').text(`${success_rate.toFixed(2)}%`);
                $('#progress-page-success').prop('title', `${success_rate.toFixed(2)}% (${response["pages_success"]}/${response["pages_found"]}) de sucesso ao coletar as páginas encontradas`);

                $('#progress-page-failure').css("width", `${error_rate.toFixed(2)}%`);
                $('#progress-page-failure').text(`${error_rate.toFixed(2)}%`);
                $('#progress-page-failure').prop('title', `${error_rate.toFixed(2)}% (${response["pages_error"]}/${response["pages_found"]}) de erro ao coletar as páginas encontradas`);

                $('#progress-page-duplicated').css("width", `${duplicated_rate.toFixed(2)}%`);
                $('#progress-page-duplicated').text(`${duplicated_rate.toFixed(2)}%`);
                $('#progress-page-duplicated').prop('title', `${duplicated_rate.toFixed(2)}% (${response["pages_duplicated"]}/${response["pages_found"]}) de páginas duplicadas encontradas`);

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
    xhr.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            var stopBtn = document.getElementById("stopBtn")
            var runBtn = document.getElementById("runBtn")
            if(response["running"] == true){
                document.getElementById("crawler_ status").innerHTML = '<span class="badge badge-success">Rodando</span>'
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
                document.getElementById("crawler_ status").innerHTML = '<span class="badge badge-warning">Parado</span>'
                stopBtn.classList.add("disabled")
                if (stopBtn.hasAttribute("href")){
                    stopBtn.setAttribute("dataref", stopBtn.getAttribute("href"))
                    stopBtn.removeAttribute("href")
                }
                runBtn.classList.remove("disabled")
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


