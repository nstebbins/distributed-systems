from dataclasses import dataclass
from typing import Self

from rich.console import Console
from rich.table import Table


@dataclass
class VectorTimestamp:
    """Represents a vector timestamp in the distributed system."""

    timestamps: dict[str, int]

    def __ge__(self, other: Self) -> bool:
        """Check if this timestamp happens after or concurrent with another timestamp."""
        return all(
            self.timestamps.get(k, 0) >= other.timestamps.get(k, 0)
            for k in set(self.timestamps) | set(other.timestamps)
        )

    def __le__(self, other: Self) -> bool:
        """Check if this timestamp happens before or concurrent with another timestamp."""
        return all(
            self.timestamps.get(k, 0) <= other.timestamps.get(k, 0)
            for k in set(self.timestamps) | set(other.timestamps)
        )

    def concurrent_with(self, other: Self) -> bool:
        """Check if this timestamp is concurrent with another timestamp."""
        return not (self <= other or other <= self)

    def merge(self, other: Self) -> None:
        """Merge another vector timestamp into this one."""
        all_processes = set(self.timestamps) | set(other.timestamps)
        for process in all_processes:
            self.timestamps[process] = max(
                self.timestamps.get(process, 0),
                other.timestamps.get(process, 0),
            )


@dataclass
class VectorMessage:
    """Represents a message in the distributed system with vector timestamps."""

    from_process: str
    to_process: str
    vector_timestamp: VectorTimestamp
    content: str


class VectorClock:
    """Implementation of Vector clock."""

    def __init__(self, process_id: str, known_processes: list[str]):
        self.process_id = process_id
        self.vector_timestamp = VectorTimestamp({p: 0 for p in known_processes})
        self.message_history: list[VectorMessage] = []
        self.console = Console()

    def increment(self) -> None:
        """Increment the local timestamp."""
        self.vector_timestamp.timestamps[self.process_id] += 1

    def update(self, received_timestamp: VectorTimestamp) -> None:
        """Update local timestamp based on received vector timestamp."""
        # First merge the received timestamp
        for process, timestamp in received_timestamp.timestamps.items():
            self.vector_timestamp.timestamps[process] = max(
                self.vector_timestamp.timestamps.get(process, 0),
                timestamp,
            )
        # Then increment local process timestamp
        self.increment()

    def send_message(self, to_process: str, content: str) -> VectorMessage:
        """Send a message to another process."""
        self.increment()
        message = VectorMessage(
            from_process=self.process_id,
            to_process=to_process,
            vector_timestamp=VectorTimestamp(self.vector_timestamp.timestamps.copy()),
            content=content,
        )
        self.message_history.append(message)
        return message

    def receive_message(self, message: VectorMessage) -> None:
        """Receive a message from another process."""
        if message.to_process != self.process_id:
            raise ValueError(
                f"Message intended for {message.to_process}, but received by {self.process_id}"
            )
        self.update(message.vector_timestamp)
        self.message_history.append(message)

    def display_history(self) -> None:
        """Display the message history in a formatted table."""
        table = Table(title=f"Vector Clock History for Process {self.process_id}")
        table.add_column("Event Type", style="cyan")
        table.add_column("From", style="green")
        table.add_column("To", style="green")
        table.add_column("Vector Timestamp", style="yellow")
        table.add_column("Process Vector", style="yellow")
        table.add_column("Content", style="white")

        current_vector = VectorTimestamp({p: 0 for p in self.vector_timestamp.timestamps})
        for msg in self.message_history:
            event_type = "SEND" if msg.from_process == self.process_id else "RECEIVE"

            if event_type == "SEND":
                current_vector.timestamps[self.process_id] += 1
            else:
                # For RECEIVE, first merge the message timestamp
                for process, timestamp in msg.vector_timestamp.timestamps.items():
                    current_vector.timestamps[process] = max(
                        current_vector.timestamps.get(process, 0),
                        timestamp,
                    )
                # Then increment local timestamp
                current_vector.timestamps[self.process_id] += 1

            table.add_row(
                event_type,
                msg.from_process,
                msg.to_process,
                str(dict(sorted(msg.vector_timestamp.timestamps.items()))),
                str(dict(sorted(current_vector.timestamps.items()))),
                msg.content,
            )

        self.console.print(table)


class DistributedSystemVC:
    """Manages multiple processes with Vector clocks."""

    def __init__(self):
        self.processes: dict[str, VectorClock] = {}

    def create_process(self, process_id: str) -> None:
        """Create a new process with a Vector clock."""
        if process_id in self.processes:
            raise ValueError(f"Process {process_id} already exists")
        # Initialize with knowledge of all existing processes plus itself
        known_processes = list(self.processes.keys()) + [process_id]
        self.processes[process_id] = VectorClock(process_id, known_processes)
        # Update existing processes to know about the new process
        for proc in self.processes.values():
            proc.vector_timestamp.timestamps[process_id] = 0

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
