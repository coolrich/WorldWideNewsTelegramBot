class ErrorHandler:
    @staticmethod
    def handle_read_timeout_error(e):
        print(e)