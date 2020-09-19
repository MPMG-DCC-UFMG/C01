document.addEventListener('DOMContentLoaded',
    function () {
        var instance_id = document.getElementById("last_instance_id").innerText.trim();
        var last_as_running = document.getElementById("instance_running").innerText.trim() == "True";
        
        if(instance_id != "None")
            tail_logs(instance_id);

        if(last_as_running)
            tail_f_logs(instance_id);
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
                document.getElementById("stdout_tail").innerText = "Arquivo em branco."

            if (response["out"].lenght != 0)
                document.getElementById("stderr_tail").innerText = response["err"]
            else
                document.getElementById("stderr_tail").innerText = "Arquivo em branco."

            document.getElementById("stdout_tail_update").innerText = "Última atualização: " + response["time"]
            document.getElementById("stderr_tail_update").innerText = "Última atualização: " + response["time"]
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
