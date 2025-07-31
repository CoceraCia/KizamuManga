import threading
import time
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from time import sleep

class LoadingSpinner:
    """Console spinner for indicating loading state."""

    def __init__(self):
        """Initialize state and thread."""
        self.progress: Progress = None
        self.task = None
        self.state : bool = None
        self.thread : threading.Thread = None

    def start(self, message: str, total = None):
        """Start spinner with a message."""
        self.state = True
        if not total:
            self.thread = threading.Thread(target=self.__loading_message, args=(message,))
        else:
            self.thread = threading.Thread(target=self.__downloading_message, args=(message,total))
        self.thread.start()

    def end(self):
        """Stop spinner and join thread."""
        self.state = False
        if self.progress is not None:
            self.progress.stop()
        self.thread.join()

    def update(self):
        self.progress.update(self.task, advance=1)
    
    def __loading_message(self, message: str):
        """Internal loop to animate spinner while active."""
        console = Console()
        with console.status(f"[bold #9f25cc]{message}...", spinner="dots", spinner_style="#9f25cc"):
            while self.state:
                time.sleep(0.1)
    def __downloading_message(self, message:str, total : int):
        self.progress =  Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=40),
            "[progress.percentage]{task.percentage:>3.1f}%",
            TimeRemainingColumn()
        )
        console = Console()
        console.print(f"[bold]{message}[/bold]", end="")
        print("...")
        self.task = self.progress.add_task("",total = total)
        self.progress.start()