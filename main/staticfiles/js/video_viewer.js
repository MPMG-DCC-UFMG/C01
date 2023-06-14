function displayVideo(url) {
    $("#video_player_modal .modal-body").append(`
        <video id="video_player" class="w-100 rounded border mt-1" controls autoplay>
            <source src="${url}" type="video/mp4">
        </video>
    `);
}

function displayVideoPlayerModal(instance_id) {
    let server_address = window.location.origin;
    let url = `${server_address}/api/instance/${instance_id}/debug/video`;

    $("#video_player_modal .modal-body").empty();

    // sends a head request to check if the video exists
    $.ajax({
        url: url,
        type: 'head',
        dataType: 'json',
        success: function (data) {
            // if the video exists, display it
            displayVideo(url);

            // display the modal but do not allow the user to close it without stopping the video
            $("#video_player_modal").modal({
                backdrop: 'static',
                keyboard: false
            });
            // $("#video_player_modal").modal("show");
        },
        error: function (data) {
            // if the video does not exist, display an error message
            $("#video_player_modal .modal-body").append(`
                <div class="alert alert-danger w-100 mt-2" role="alert">
                    <h4 class="alert-heading">Erro</h4>
                    <p>Não há video para essa instância.</p>
                </div>
            `);
            $("#video_player_modal").modal("show");
        }
    });
}

function closeVideoPlayerModal() {
    // stop the video from playing
    if ($("#video_player").length > 0) 
        $("#video_player")[0].pause();

    $("#video_player_modal .modal-body").empty();
    $("#video_player_modal").modal("hide");
}