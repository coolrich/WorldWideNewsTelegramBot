import concurrent.futures
import threading


class FunctionExecutor:
    def __init__(self, max_workers):
        self.max_workers = max_workers
        # self.interval = interval

    def execute_functions_periodically(self, *functions_with_args):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for func, args in functions_with_args:
                print("function:", func, "args:", args)
                if args is not None:
                    futures.append(executor.submit(func, *args))
                else:
                    futures.append(executor.submit(func))
            print("After for loop in execute_functions_periodically")
            concurrent.futures.wait(futures)
            print("After wait in execute_functions_periodically")
            # time.sleep(60)


class StartTheBot:
    def __init__(self):
        self.lock = threading.Lock()
        self.news_manager = NewsManager(self.lock)
        self.bot_controller = BotController(self.news_manager, self.lock)
        self.function_executor = FunctionExecutor(max_workers=3)

    def start(self):
        self.function_executor.execute_functions_periodically(
            (self.news_manager.get_ua_news, (self.bot_controller, 60,)),
            (self.news_manager.get_world_news, (self.bot_controller, 60,)),
            (self.bot_controller.start_bot_controller, (self.bot_controller,))
        )


if __name__ == "__main__":
    StartTheBot().start()
