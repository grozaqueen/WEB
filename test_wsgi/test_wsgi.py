import cgi

HELLO_WORLD = b"Hello world!\n"


def simple_app(environ, start_response):
    """Simplest possible application object"""
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    print(environ)

    if environ['REQUEST_METHOD'] == 'GET':
        query_string = environ['QUERY_STRING'].split('&')

        print("GET params:")
        print(*query_string)

    elif environ['REQUEST_METHOD'] == 'POST':
        query_string = environ['QUERY_STRING'].split('&')

        post = cgi.FieldStorage(
            fp=environ['wsgi.input'],
            environ=environ,
            keep_blank_values=True
        )
        values = post.value
        post_values = []
        for value in values:
            param = f'{value.name}={post.getvalue(value.name)}'
            if param not in query_string:
                post_values.append(param)

        print("GET params:")
        print(*query_string)
        print("POST params:")
        print(*post_values)

    return [HELLO_WORLD]


application = simple_app