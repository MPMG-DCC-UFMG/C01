class RedirectMiddlewareC04:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        print('response Mid: ', response)
        # print('request: ', request)
        # print('response code: ', response.status_code)

        if response.status_code == 301 or response.status_code ==302:
            # print('header: ', response.headers)
            if 'text/html;' in str(response):
                return response
            else:
                url = str(response).split('url=')[1][:-1]
                print('ARQUIVO')
                self.feed_file_downloader(url, response)
                return 

        return response