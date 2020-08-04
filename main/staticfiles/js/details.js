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
    // calls tail log view and set logs, while also getting the progress status
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);

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

            prog_bar = document.getElementById("last_instance_progress")
            prog_bar.value = response["collected"]
            prog_bar.max = response["scheduled"]

            prop = parseInt(response["collected"]) / parseInt(response["scheduled"])
            percentage = Math.round(prop * 100, 2)
            prog_bar.innerText = percentage + " %"

            document.getElementById("last_collected").innerText = response["collected"]
            document.getElementById("last_scheduled").innerText = response["scheduled"]
        }
    };
    xhr.open("GET", "/tail_log_file/" + instance_id, true);
    xhr.send();
}

function tail_f_logs(instance_id){
    // Calls tail_logs every 5 seconds
    setInterval(
        function(){ tail_logs(instance_id);},
        5000
    ); 
}
