import pytest

from distributed_systems.core.vector_clock import (
    DistributedSystemVC,
    VectorClock,
    VectorMessage,
    VectorTimestamp,
)


def test_vector_timestamp_comparison():
    """Test vector timestamp comparison operations."""
    t1 = VectorTimestamp({"P1": 1, "P2": 0})
    t2 = VectorTimestamp({"P1": 2, "P2": 0})
    t3 = VectorTimestamp({"P1": 1, "P2": 1})

    # Test less than or equal
    assert t1 <= t2
    assert t1 <= t3
    assert not t2 <= t3

    # Test greater than or equal
    assert t2 >= t1
    assert t3 >= t1
    assert not t3 >= t2

    # Test concurrent events
    assert t2.concurrent_with(t3)
    assert t3.concurrent_with(t2)
    assert not t1.concurrent_with(t2)


def test_vector_timestamp_merge():
    """Test vector timestamp merging."""
    t1 = VectorTimestamp({"P1": 1, "P2": 0, "P3": 2})
    t2 = VectorTimestamp({"P1": 0, "P2": 2, "P3": 1})
    t1.merge(t2)

    assert t1.timestamps == {"P1": 1, "P2": 2, "P3": 2}


def test_vector_clock_initialization():
    """Test vector clock initialization."""
    clock = VectorClock("P1", ["P1", "P2", "P3"])
    assert clock.process_id == "P1"
    assert clock.vector_timestamp.timestamps == {"P1": 0, "P2": 0, "P3": 0}
    assert len(clock.message_history) == 0


def test_vector_clock_increment():
    """Test vector clock increment operation."""
    clock = VectorClock("P1", ["P1", "P2"])
    clock.increment()
    assert clock.vector_timestamp.timestamps == {"P1": 1, "P2": 0}


def test_vector_clock_update():
    """Test vector clock update with received timestamp."""
    clock = VectorClock("P1", ["P1", "P2"])
    received = VectorTimestamp({"P1": 0, "P2": 2})
    clock.update(received)
    # After update: merge timestamps and increment local
    assert clock.vector_timestamp.timestamps == {"P1": 1, "P2": 2}


def test_send_message():
    """Test sending a message with vector clock."""
    clock = VectorClock("P1", ["P1", "P2"])
    message = clock.send_message("P2", "Hello")
    assert message.from_process == "P1"
    assert message.to_process == "P2"
    assert message.vector_timestamp.timestamps == {"P1": 1, "P2": 0}
    assert message.content == "Hello"
    assert len(clock.message_history) == 1


def test_receive_message():
    """Test receiving a message with vector clock."""
    clock = VectorClock("P2", ["P1", "P2"])
    message = VectorMessage(
        from_process="P1",
        to_process="P2",
        vector_timestamp=VectorTimestamp({"P1": 2, "P2": 0}),
        content="Hello",
    )
    clock.receive_message(message)
    # After receive: merge timestamps and increment local
    assert clock.vector_timestamp.timestamps == {"P1": 2, "P2": 1}
    assert len(clock.message_history) == 1


def test_receive_wrong_message():
    """Test receiving a message intended for another process."""
    clock = VectorClock("P2", ["P1", "P2", "P3"])
    message = VectorMessage(
        from_process="P1",
        to_process="P3",
        vector_timestamp=VectorTimestamp({"P1": 1, "P2": 0, "P3": 0}),
        content="Hello",
    )
    with pytest.raises(ValueError):
        clock.receive_message(message)


def test_distributed_system_vc():
    """Test the distributed system with vector clocks."""
    system = DistributedSystemVC()

    # Create processes
    system.create_process("P1")
    system.create_process("P2")
    system.create_process("P3")

    # Send messages between processes
    system.send_message("P1", "P2", "Message 1")  # P1 -> P2
    system.send_message("P2", "P3", "Message 2")  # P2 -> P3
    system.send_message("P3", "P1", "Message 3")  # P3 -> P1

    # Verify vector timestamps
    p1_clock = system.processes["P1"]
    p2_clock = system.processes["P2"]
    p3_clock = system.processes["P3"]

    # Expected vector timestamps after all messages:
    # P1: {P1: 2, P2: 2, P3: 2}  # Has seen all events through transitive message passing
    # P2: {P1: 1, P2: 2, P3: 0}  # Only knows about P1's first message and its own send
    # P3: {P1: 1, P2: 2, P3: 2}  # Knows about P1->P2->P3 chain and its own send

    assert p1_clock.vector_timestamp.timestamps == {"P1": 2, "P2": 2, "P3": 2}
    assert p2_clock.vector_timestamp.timestamps == {"P1": 1, "P2": 2, "P3": 0}
    assert p3_clock.vector_timestamp.timestamps == {"P1": 1, "P2": 2, "P3": 2}


def test_concurrent_events():
    """Test detection of concurrent events in the system."""
    system = DistributedSystemVC()
    system.create_process("P1")
    system.create_process("P2")

    # P1 sends to P2 but P2 hasn't received it yet
    p1 = system.processes["P1"]
    p1.send_message("P2", "Message 1")
    p1_state = VectorTimestamp(p1.vector_timestamp.timestamps.copy())

    # P2 sends to P1 without having received P1's message
    p2 = system.processes["P2"]
    p2.send_message("P1", "Message 2")
    p2_state = VectorTimestamp(p2.vector_timestamp.timestamps.copy())

    # These events should be concurrent
    # P1: {P1: 1, P2: 0}
    # P2: {P1: 0, P2: 1}
    assert p1_state.concurrent_with(p2_state)


def test_duplicate_process_creation():
    """Test creating a process with an existing ID."""
    system = DistributedSystemVC()
    system.create_process("P1")
    with pytest.raises(ValueError):
        system.create_process("P1")


def test_invalid_message_sending():
    """Test sending a message to a non-existent process."""
    system = DistributedSystemVC()
    system.create_process("P1")
    with pytest.raises(ValueError):
        system.send_message("P1", "P2", "Invalid message")
