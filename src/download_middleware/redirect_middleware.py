zclass RedirectMiddlewareC04:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if response.status_code == 301 or response.status_code ==302:
            if 'text/html;' in str(response):
                return response
            else:
                url = str(response).split('url=')[1][:-1]
                self.feed_file_downloader(url, response)
                return 

        return response
