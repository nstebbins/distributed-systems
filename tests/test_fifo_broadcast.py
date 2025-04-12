import pytest

from distributed_systems.core.fifo_broadcast import (
    DistributedSystemFIFO,
    FIFOBroadcast,
    FIFOMessage,
    ProcessId,
    SequenceNumber,
)


def test_fifo_broadcast_initialization() -> None:
    """Test initialization of FIFO broadcast."""
    broadcast = FIFOBroadcast(ProcessId("P1"), [ProcessId("P1"), ProcessId("P2")])
    assert broadcast.process_id == ProcessId("P1")
    assert broadcast.known_processes == [ProcessId("P1"), ProcessId("P2")]
    assert broadcast.process_states[ProcessId("P1")].sequence_number == SequenceNumber(0)
    assert broadcast.process_states[ProcessId("P1")].next_expected == SequenceNumber(1)
    assert len(broadcast.message_history) == 0


def test_broadcast() -> None:
    """Test broadcasting a message."""
    broadcast = FIFOBroadcast(ProcessId("P1"), [ProcessId("P1"), ProcessId("P2")])
    message = broadcast.broadcast("Hello")
    assert message.from_process == ProcessId("P1")
    assert message.sequence_number == SequenceNumber(1)
    assert message.content == "Hello"
    assert len(broadcast.message_history) == 1


def test_deliver_in_order() -> None:
    """Test delivering messages in order."""
    broadcast = FIFOBroadcast(ProcessId("P2"), [ProcessId("P1"), ProcessId("P2")])

    # Create messages from P1
    msg1 = FIFOMessage(ProcessId("P1"), SequenceNumber(1), "First")
    msg2 = FIFOMessage(ProcessId("P1"), SequenceNumber(2), "Second")

    # Deliver in order
    broadcast.deliver(msg1)
    broadcast.deliver(msg2)

    assert len(broadcast.message_history) == 2
    assert broadcast.message_history[0].sequence_number == SequenceNumber(1)
    assert broadcast.message_history[1].sequence_number == SequenceNumber(2)


def test_deliver_out_of_order() -> None:
    """Test delivering messages out of order."""
    broadcast = FIFOBroadcast(ProcessId("P2"), [ProcessId("P1"), ProcessId("P2")])

    # Create messages from P1
    msg1 = FIFOMessage(ProcessId("P1"), SequenceNumber(1), "First")
    msg2 = FIFOMessage(ProcessId("P1"), SequenceNumber(2), "Second")

    # Deliver out of order
    broadcast.deliver(msg2)
    assert len(broadcast.message_history) == 0  # Should not be delivered yet

    broadcast.deliver(msg1)
    assert len(broadcast.message_history) == 2  # Both should be delivered now
    assert broadcast.message_history[0].sequence_number == SequenceNumber(1)
    assert broadcast.message_history[1].sequence_number == SequenceNumber(2)


def test_distributed_system_fifo() -> None:
    """Test the distributed system with FIFO broadcast."""
    system = DistributedSystemFIFO()

    # Create processes
    system.create_process(ProcessId("P1"))
    system.create_process(ProcessId("P2"))
    system.create_process(ProcessId("P3"))

    # Broadcast messages
    system.broadcast_message(ProcessId("P1"), "Message 1")
    system.broadcast_message(ProcessId("P1"), "Message 2")
    system.broadcast_message(ProcessId("P2"), "Message 3")

    # Verify message histories
    p1_history = system.processes[ProcessId("P1")].message_history
    p2_history = system.processes[ProcessId("P2")].message_history
    p3_history = system.processes[ProcessId("P3")].message_history

    # P1 should have its own broadcasts and receive P2's message
    assert len(p1_history) == 3
    p1_sent_messages = [msg for msg in p1_history if msg.from_process == ProcessId("P1")]
    assert len(p1_sent_messages) == 2

    # P2 and P3 should have received all messages
    assert len(p2_history) == 3
    assert len(p3_history) == 3

    # Verify FIFO ordering for P1's messages in P2's history
    p1_messages_in_p2 = [msg for msg in p2_history if msg.from_process == ProcessId("P1")]
    assert p1_messages_in_p2[0].sequence_number == SequenceNumber(1)
    assert p1_messages_in_p2[1].sequence_number == SequenceNumber(2)

    # Verify FIFO ordering for P1's messages in P3's history
    p1_messages_in_p3 = [msg for msg in p3_history if msg.from_process == ProcessId("P1")]
    assert p1_messages_in_p3[0].sequence_number == SequenceNumber(1)
    assert p1_messages_in_p3[1].sequence_number == SequenceNumber(2)


def test_duplicate_process_creation() -> None:
    """Test creating a process with an existing ID."""
    system = DistributedSystemFIFO()
    system.create_process(ProcessId("P1"))
    with pytest.raises(ValueError):
        system.create_process(ProcessId("P1"))


def test_invalid_broadcast() -> None:
    """Test broadcasting from a non-existent process."""
    system = DistributedSystemFIFO()
    system.create_process(ProcessId("P1"))
    with pytest.raises(ValueError):
        system.broadcast_message(ProcessId("P2"), "Invalid message")
