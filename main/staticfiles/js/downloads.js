
var current_download = -1;

$(document).ready(function () {
    get_current_download();
    get_download_list();
    setInterval(
        function () {
            get_current_download();
            get_download_list();
            get_error_list();
        },
        1000
    );
});

function get_error_list(){
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText)["error"];

            document.getElementById("file_error").innerHTML = "";
            for (var i = 0; i < response.length; i++) {
                var curr = response[i];
                console.log(JSON.parse(curr["description"]));
                var url = JSON.parse(curr["description"])["url"];

                var slices = url.split("/")
                var file_name = slices[slices.length - 1];

                slices = file_name.split(".")
                var format = slices[slices.length - 1];
                if (format.length > 4) format = "???";

                var html = `
                    <div class="row download-item" id="file_${curr["id"]}_on_queue">
                        <div class="col-1 download-item-ext">${format}</div>
                        <div class="col download-item-links">
                            <div class="row">
                                <div class="col" style="padding: 10px 12px;">
                                    <p>${file_name}</p>
                                    <a href="${url}">${url}</a>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col" style="padding: 10px 12px;">
                                    <p>${curr["error_message"]}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                $('#file_error').append(html);
            }

        }
    };
    xhr.open("GET", "/api/downloads/error/", true);
    xhr.send();
}

function get_download_list(){
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText)["queue"];
        
            document.getElementById("file_queue").innerHTML = "";
            for (var i = 0; i < response.length; i++) {
                var curr = response[i];
                console.log(JSON.parse(curr["description"]));
                var url = JSON.parse(curr["description"])["url"];

                var slices = url.split("/")
                var file_name = slices[slices.length - 1];

                slices = file_name.split(".")
                var format = slices[slices.length - 1];
                if (format.length > 4) format = "???";

                var html = `
                    <div class="row download-item" id="file_${curr["id"]}_on_queue">
                        <div class="col-1 download-item-ext">${format}</div>
                        <div class="col download-item-links">
                            <div class="row">
                                <div class="col" style="padding: 10px 12px;">
                                    <p>${file_name}</p>
                                    <a href="${url}">${url}</a>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                $('#file_queue').append(html);
            }

        }
    };
    xhr.open("GET", "/api/downloads/queue/", true);
    xhr.send();
}

function get_current_download() {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);

            if (!("progress" in response)){
                return;
            }

            var download_progress = Math.round(100 * response["progress"] / response["size"]);
            var desc = JSON.parse(response["description"]);

            var url = desc["url"];
            var slices = url.split("/");
            var file_name = slices[slices.length - 1];

            slices = file_name.split(".");
            var format = slices[slices.length - 1];
            if (format.length > 4) format = "???";

            if (response["id"] != current_download) {
                response["id"] == current_download;

                current_download = response["id"];
                document.getElementById("file_downloading").innerHTML = "";
                html = `
                    <div class="row download-item" id="file_${response["id"]}">
                        <div class="col-1 download-item-ext">${format}</div>
                        <div class="col download-item-links">
                            <div class="row">
                                <div class="col" style="padding: 10px 12px;">
                                    <p>${file_name}</p>
                                    <a href="${url}">${url}</a>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col">
                                    <div class="progress">
                                        <div id="progress-bar" class="progress-bar bg-success" role="progressbar" style="width: ${download_progress}%;" 
                                            aria-valuenow="${download_progress}" aria-valuemin="0" aria-valuemax="100">
                                            ${download_progress}%
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="row download-item-btns" display=None>
                                <div class="col-2">
                                    <button type="button" class="btn btn-link">Mostrar na pasta</button>
                                </div>
                                <div class="col"></div>
                            </div>
                        </div>
                    </div>
                `;

                $("#file_downloading").append(html);
            }
            else {
                var div = document.getElementById('file_downloading');
                div = div.getElementsByClassName("progress-bar")[0];
                div.setAttribute("aria-valuenow", download_progress);
                div.style.width = `${download_progress}%`;
                div.innerHTML = `${download_progress}%`;
            }
        }
    };
    xhr.open("GET", "/api/downloads/progress/", true);
    xhr.send();
}
