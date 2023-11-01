class ErrorHandler:
    @staticmethod
    def handle_read_timeout_error(e, logger):
        logger.error(f"In ReadTimeout Exception handler of ErrorHandler class: {e}")