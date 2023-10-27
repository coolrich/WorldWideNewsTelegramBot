import time

from application_controller import ApplicationController

# Test the Application
if __name__ == "__main__":
    app = ApplicationController()
    app.start()
    time.sleep(10)
    print("Start program shutdown...")
    app.stop()
    print("The program has been finished.")
