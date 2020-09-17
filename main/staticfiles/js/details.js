statusInterval = null //global var to control call interval
document.addEventListener('DOMContentLoaded',
    function () {
        var instance_id = document.getElementById("last_instance_id").innerText.trim();
        var last_as_running = document.getElementById("instance_running").innerText.trim() == "True";
        
        if(instance_id != "None"){
            tail_logs(instance_id);
            status_instance(instance_id);
        }

        if(last_as_running){
            tail_f_logs(instance_id);
            status_f_instance(instance_id);
        }
    },
    false
);


function tail_logs(instance_id){
    // calls tail log view and set logs
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            console.log(response);

            if(response["out"].lenght != 0)
                document.getElementById("stdout_tail").innerText = response["out"]
            else
                document.getElementById("stdout_tail").innerText = "Empty file."

            if (response["out"].lenght != 0)
                document.getElementById("stderr_tail").innerText = response["err"]
            else
                document.getElementById("stderr_tail").innerText = "Empty file."

            document.getElementById("stdout_tail_update").innerText = "last update: " + response["time"]
            document.getElementById("stderr_tail_update").innerText = "last update: " + response["time"]
        }
    };
    xhr.open("GET", "/tail_log_file/"+instance_id, true);
    xhr.send();
}

function tail_f_logs(instance_id){
    // Calls tail_logs every 5 seconds
    setInterval(
        function(){ tail_logs(instance_id);},
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
                document.getElementById("crawler_ status").innerHTML = '<span class="badge badge-success">Running</span>'
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
                document.getElementById("crawler_ status").innerHTML = '<span class="badge badge-warning">Not running</span>'
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
    // Calls status_instance every 0.5 secondsa while running
    statusInterval=setInterval(
        function(){ status_instance(instance_id);},
        500
    ); 
}
