import sys
import threading
import time

class LoadingSpinner():
    """
    A simple loading spinner class that displays an animated message 
    (with dots) in the console while background tasks are running.
    """

    def __init__(self):
        """
        Initializes the LoadingSpinner object.
        Sets the internal state and thread placeholder.
        """
        self.state = None
        self.thread = None

    def start(self, message: str):
        """
        Starts the loading spinner in a separate thread.
        
        Args:
            message (str): The message to display before the animated dots.
        """
        self.state = True
        self.thread = threading.Thread(target=self.__loading_message,
                                       args=(message,))
        self.thread.start()

    def end(self):
        """
        Stops the loading spinner and waits for the thread to finish.
        """
        self.state = False
        self.thread.join()

    def __loading_message(self, message: str):
        """
        Internal method that runs the spinner animation loop.
        
        Args:
            message (str): The message to display before the dots.
        """
        max_length = len(message) + 3
        while self.state:
            for i in range(3):
                display = f"\r{message}{'.' * (i + 1)}"
                padding = " " * (max_length - len(display))
                sys.stdout.write(f"{display}{padding}")
                sys.stdout.flush()
                time.sleep(0.5)
                if not self.state:
                    break
        # Erase the entire line when done
        sys.stdout.write("\r" + " " * max_length + "\r")
        sys.stdout.flush()
