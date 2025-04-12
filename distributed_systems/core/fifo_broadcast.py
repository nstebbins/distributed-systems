from dataclasses import dataclass
from typing import Dict, List, Optional, TypedDict, NewType

from rich.console import Console
from rich.table import Table


ProcessId = NewType("ProcessId", str)
SequenceNumber = NewType("SequenceNumber", int)


class PendingMessages(TypedDict):
    """Type for pending messages dictionary."""

    messages: Dict[SequenceNumber, "FIFOMessage"]


@dataclass
class FIFOMessage:
    """Represents a message in the FIFO broadcast system."""

    from_process: ProcessId
    sequence_number: SequenceNumber
    content: str


@dataclass
class ProcessState:
    """Represents the state of a process in the FIFO broadcast system."""

    sequence_number: SequenceNumber
    next_expected: SequenceNumber
    pending_messages: PendingMessages


class FIFOBroadcast:
    """Implementation of FIFO broadcast."""

    def __init__(self, process_id: ProcessId, known_processes: List[ProcessId]) -> None:
        self.process_id = process_id
        self.known_processes = known_processes
        self.process_states: Dict[ProcessId, ProcessState] = {
            pid: ProcessState(
                sequence_number=SequenceNumber(0),
                next_expected=SequenceNumber(1),
                pending_messages=PendingMessages(messages={}),
            )
            for pid in known_processes
        }
        self.message_history: List[FIFOMessage] = []
        self.console = Console()

    def broadcast(self, content: str) -> FIFOMessage:
        """Broadcast a message to all processes."""
        state = self.process_states[self.process_id]
        state.sequence_number = SequenceNumber(state.sequence_number + 1)
        message = FIFOMessage(
            from_process=self.process_id,
            sequence_number=state.sequence_number,
            content=content,
        )
        self.message_history.append(message)
        return message

    def deliver(self, message: FIFOMessage) -> None:
        """Deliver a message from another process."""
        sender = message.from_process
        state = self.process_states[sender]

        # Store the message in pending messages
        state.pending_messages["messages"][message.sequence_number] = message

        # Try to deliver any pending messages in order
        while state.next_expected in state.pending_messages["messages"]:
            msg = state.pending_messages["messages"].pop(state.next_expected)
            self.message_history.append(msg)
            state.next_expected = SequenceNumber(state.next_expected + 1)

    def display_history(self) -> None:
        """Display the message history in a formatted table."""
        table = Table(title=f"FIFO Broadcast History for Process {self.process_id}")
        table.add_column("Event Type", style="cyan")
        table.add_column("From", style="green")
        table.add_column("Sequence Number", style="yellow")
        table.add_column("Content", style="white")

        for msg in self.message_history:
            event_type = "BROADCAST" if msg.from_process == self.process_id else "DELIVER"
            table.add_row(
                event_type,
                msg.from_process,
                str(msg.sequence_number),
                msg.content,
            )

        self.console.print(table)


class DistributedSystemFIFO:
    """Manages multiple processes with FIFO broadcast."""

    def __init__(self) -> None:
        self.processes: Dict[ProcessId, FIFOBroadcast] = {}

    def create_process(self, process_id: ProcessId) -> None:
        """Create a new process with FIFO broadcast."""
        if process_id in self.processes:
            raise ValueError(f"Process {process_id} already exists")
        # Initialize with knowledge of all existing processes plus itself
        known_processes = list(self.processes.keys()) + [process_id]
        self.processes[process_id] = FIFOBroadcast(process_id, known_processes)
        # Update existing processes to know about the new process
        for proc in self.processes.values():
            if proc.process_id != process_id:
                proc.known_processes.append(process_id)
                proc.process_states[process_id] = ProcessState(
                    sequence_number=SequenceNumber(0),
                    next_expected=SequenceNumber(1),
                    pending_messages=PendingMessages(messages={}),
                )

    def broadcast_message(self, from_process: ProcessId, content: str) -> None:
        """Broadcast a message from a process to all other processes."""
        if from_process not in self.processes:
            raise ValueError(f"Process {from_process} does not exist")

        sender = self.processes[from_process]
        message = sender.broadcast(content)

        # Deliver the message to all other processes
        for process_id, process in self.processes.items():
            if process_id != from_process:
                process.deliver(message)

    def display_all_histories(self) -> None:
        """Display message histories for all processes."""
        for process in self.processes.values():
            process.display_history()
            self.processes[process.process_id].console.print("\n")
