from jsonrpcserver import Success, method, serve

@method
def ping():
    return Success('pong')

if __name__ == '__main__':
    serve(port=5001)  # Specify your desired port here