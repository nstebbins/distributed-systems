from dataclasses import dataclass

from rich.console import Console
from rich.table import Table


@dataclass
class Message:
    """Represents a message in the distributed system."""

    from_process: str
    to_process: str
    timestamp: int
    content: str


class LamportClock:
    """Implementation of Lamport's logical clock."""

    def __init__(self, process_id: str):
        self.process_id = process_id
        self.timestamp = 0
        self.message_history: list[Message] = []
        self.console = Console()

    def increment(self) -> None:
        """Increment the local timestamp."""
        self.timestamp += 1

    def update(self, received_timestamp: int) -> None:
        """Update local timestamp based on received message timestamp."""
        self.timestamp = max(self.timestamp, received_timestamp) + 1

    def send_message(self, to_process: str, content: str) -> Message:
        """Send a message to another process."""
        self.increment()
        message = Message(
            from_process=self.process_id,
            to_process=to_process,
            timestamp=self.timestamp,
            content=content,
        )
        self.message_history.append(message)
        return message

    def receive_message(self, message: Message) -> None:
        """Receive a message from another process."""
        if message.to_process != self.process_id:
            raise ValueError(
                f"Message intended for {message.to_process}, but received by {self.process_id}"
            )
        self.update(message.timestamp)
        self.message_history.append(message)

    def display_history(self) -> None:
        """Display the message history in a formatted table."""
        table = Table(title=f"Message History for Process {self.process_id}")
        table.add_column("Event Type", style="cyan")
        table.add_column("From", style="green")
        table.add_column("To", style="green")
        table.add_column("Message Timestamp", style="yellow")
        table.add_column("Process Timestamp", style="yellow")
        table.add_column("Content", style="white")

        current_timestamp = 0
        for msg in self.message_history:
            event_type = "SEND" if msg.from_process == self.process_id else "RECEIVE"
            if event_type == "SEND":
                current_timestamp = msg.timestamp
                process_timestamp = msg.timestamp
            else:
                current_timestamp = max(current_timestamp, msg.timestamp) + 1
                process_timestamp = current_timestamp

            table.add_row(
                event_type,
                msg.from_process,
                msg.to_process,
                str(msg.timestamp),
                str(process_timestamp),
                msg.content,
            )

        self.console.print(table)


class DistributedSystem:
    """Manages multiple processes with Lamport clocks."""

    def __init__(self):
        self.processes: dict[str, LamportClock] = {}

    def create_process(self, process_id: str) -> None:
        """Create a new process with a Lamport clock."""
        if process_id in self.processes:
            raise ValueError(f"Process {process_id} already exists")
        self.processes[process_id] = LamportClock(process_id)

    def send_message(self, from_process: str, to_process: str, content: str) -> None:
        """Send a message between processes."""
        if from_process not in self.processes or to_process not in self.processes:
            raise ValueError("Invalid process ID")

        sender = self.processes[from_process]
        receiver = self.processes[to_process]

        message = sender.send_message(to_process, content)
        receiver.receive_message(message)

    def display_all_histories(self) -> None:
        """Display message histories for all processes."""
        for process in self.processes.values():
            process.display_history()
            self.processes[process.process_id].console.print("\n")
