import time

from controllers.application_controller import ApplicationController

# Test the Application
if __name__ == "__main__":
    app = ApplicationController(True)
    app.start()
    time.sleep(60*6)
    print("Start program shutdown...")
    app.stop()
    print("The program has been finished.")
