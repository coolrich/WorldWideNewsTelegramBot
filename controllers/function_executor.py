import concurrent.futures


class FunctionExecutor:
    def __init__(self, max_workers, logger):
        logger.debug("Start of the FunctionExecutor initialization")
        self.max_workers = max_workers
        self.logger = logger
        logger.debug("End of the FunctionExecutor initialization")

    def execute_functions_periodically(self, *functions_with_args):
        self.logger.debug("Start of the execute_functions_periodically() method in FunctionExecutor class")
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for func, args in functions_with_args:
                self.logger.debug("function:", func, "args:", args)
                if args is not None:
                    futures.append(executor.submit(func, *args))
                else:
                    futures.append(executor.submit(func))
            # concurrent.futures.wait(futures)
        self.logger.debug("End of the execute_functions_periodically() method in FunctionExecutor class")
