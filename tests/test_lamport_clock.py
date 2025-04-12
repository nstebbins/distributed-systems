import pytest

from distributed_systems.core.lamport_clock import (
    DistributedSystem,
    LamportClock,
    Message,
)


def test_lamport_clock_initialization():
    clock = LamportClock("P1")
    assert clock.process_id == "P1"
    assert clock.timestamp == 0
    assert len(clock.message_history) == 0


def test_lamport_clock_increment():
    clock = LamportClock("P1")
    clock.increment()
    assert clock.timestamp == 1


def test_lamport_clock_update():
    clock = LamportClock("P1")
    clock.update(5)
    assert clock.timestamp == 6  # Max(0, 5) + 1


def test_send_message():
    clock = LamportClock("P1")
    message = clock.send_message("P2", "Hello")
    assert message.from_process == "P1"
    assert message.to_process == "P2"
    assert message.timestamp == 1
    assert message.content == "Hello"
    assert len(clock.message_history) == 1


def test_receive_message():
    clock = LamportClock("P2")
    message = Message(from_process="P1", to_process="P2", timestamp=5, content="Hello")
    clock.receive_message(message)
    assert clock.timestamp == 6
    assert len(clock.message_history) == 1


def test_receive_wrong_message():
    clock = LamportClock("P2")
    message = Message(from_process="P1", to_process="P3", timestamp=5, content="Hello")
    with pytest.raises(ValueError):
        clock.receive_message(message)


def test_distributed_system():
    system = DistributedSystem()

    # Create processes
    system.create_process("P1")
    system.create_process("P2")
    system.create_process("P3")

    # Send messages between processes
    system.send_message("P1", "P2", "Message 1")
    system.send_message("P2", "P3", "Message 2")
    system.send_message("P3", "P1", "Message 3")

    # Verify timestamps
    assert system.processes["P1"].timestamp == 2  # Sent 1, Received 1
    assert system.processes["P2"].timestamp == 2  # Received 1, Sent 1
    assert system.processes["P3"].timestamp == 3  # Received 1, Sent 1


def test_duplicate_process_creation():
    system = DistributedSystem()
    system.create_process("P1")
    with pytest.raises(ValueError):
        system.create_process("P1")


def test_invalid_message_sending():
    system = DistributedSystem()
    system.create_process("P1")
    with pytest.raises(ValueError):
        system.send_message("P1", "P2", "Invalid message")


def test_simple_message_exchange():
    """Test to verify correct timestamp behavior in a simple message exchange."""
    system = DistributedSystem()
    system.create_process("P1")
    system.create_process("P2")

    # When P1 sends to P2:
    # 1. P1 increments to 1
    # 2. P2 receives message with timestamp 1
    # 3. P2 should update to max(0,1) + 1 = 2
    system.send_message("P1", "P2", "Hello")

    assert system.processes["P1"].timestamp == 1  # Only incremented for send
    assert system.processes["P2"].timestamp == 2  # Should be max(0,1) + 1
