import time

from controllers.application_controller import ApplicationController

# Test the Application
if __name__ == "__main__":
    app = ApplicationController(True, 50)
    app.start(15)
    time.sleep(60*3)
    print("Start program shutdown...")
    app.stop()
    print("The program has been finished.")
