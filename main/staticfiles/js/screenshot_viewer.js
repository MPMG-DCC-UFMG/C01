function updateGallery(data) {
    const TMB_WIDTH = 150;
    const TMB_HEIGHT = 150;

    let data_list = [];

    for (let i = 0; i < data.length; i++) {
        let current = data[i];

        data_list.push({
            src: current['base64'],
            srct: current['base64'],
            title: current['title']
        });
    }

    $("#screenshot_modal .screenshot_list").nanogallery2( {
        itemsBaseURL: 'data:image/png;base64, ',
        thumbnailHeight: TMB_WIDTH,
        thumbnailWidth: TMB_HEIGHT,
        items: data_list,
        viewerTools:    {
            topLeft:   'label',
            topRight:  'zoomButton, closeButton'
        },
        galleryToolbarHideIcons: true
    });
}

function displayScreenshotModal(instance_id) {
    $("#screenshot_modal .spinner-border").show();
    $("#screenshot_modal .pagination").empty();
    $("#screenshot_modal .screenshot_list").empty();

    let server_address = window.location.origin;
    $("#screenshot_modal").modal("show");

    $.ajax({
        url: `${server_address}/api/instance/${instance_id}/debug/screenshots`,
        type: 'get',
        dataType: 'json',
        // async: false,
        success: function (data) {
            let items_per_page = data["data"].length;

            $("#screenshot_modal .pagination").paging(data['total_screenshots'], {
                format: '[< ncnnn >]',
                perpage: items_per_page,
                lapping: 0,
                page: 1,
                onSelect: function (page) {
                    $("#screenshot_modal .spinner-border").show();
                    $("#screenshot_modal .screenshot_list").nanogallery2('destroy');
                    $("#screenshot_modal .screenshot_list").empty();
                    $.ajax(`${server_address}/api/instance/${instance_id}/debug/screenshots?page=${page}&imgs_per_page=${items_per_page}`)
                        .done(function (new_data) {
                            updateGallery(new_data["data"]);
                            $("#screenshot_modal .spinner-border").hide();
                        });
                },
                onFormat: function (type) {
                    switch (type) {
                        case 'block': // n and c
                            return '<a href="#" class="paging_entry_number">' + this.value + '</a>';
                        case 'next': // >
                            return '<a href="#" class="paging_entry_arrow"><i class="fa fa-step-forward"></i></a>';
                        case 'prev': // <
                            return '<a href="#" class="paging_entry_arrow"><i class="fa fa-step-backward"></i></a>';
                        case 'first': // [
                            return '<a href="#" class="paging_entry_arrow"><i class="fa fa-fast-backward"></i></a>';
                        case 'last': // ]
                            return '<a href="#" class="paging_entry_arrow"><i class="fa fa-fast-forward"></i></a>';
                    }
                }
            });

            $("#screenshot_modal .spinner-border").hide();
        },
        error: function (data) {
            data = data.responseJSON;
            $("#screenshot_modal .screenshot_list").append(`
                <div class="alert alert-danger w-100 mt-2" role="alert">
                    <h4 class="alert-heading">Erro</h4>
                    <p>${data.error}</p>
                </div>
            `);
            $("#screenshot_modal .spinner-border").hide();
            // $("#screenshot_modal").modal("hide");
        }
    });
}

$('#screenshot_modal').on('hidden.bs.modal', function () {
    $("#screenshot_modal .screenshot_list").nanogallery2('destroy');
});
