# Distributed Systems Algorithms

This package provides implementations of fundamental distributed systems algorithms and concepts:

## Implemented Algorithms

### Logical Clocks
1. **Lamport Clocks**
   - Simple scalar timestamps for partial ordering of events
   - Captures "happened-before" relationships
   - Useful for basic event ordering in distributed systems
   - Limitations: Cannot detect concurrent events

2. **Vector Clocks**
   - Vector timestamps for capturing causality
   - Detects concurrent events
   - Provides stronger consistency than Lamport clocks
   - Each process maintains a vector of timestamps
   - Features:
     - Causal ordering of events
     - Concurrent event detection
     - Perfect detection of "happened-before" relationships

3. **FIFO Broadcast**
   - Ensures messages from the same sender are delivered in order
   - Properties:
     - FIFO ordering: If a process broadcasts m1 before m2, no process delivers m2 before m1
     - Messages from different senders may be delivered in any order
     - Uses sequence numbers per sender
     - Buffers out-of-order messages until they can be delivered

## Features

- Beautiful terminal-based visualization of message passing
- Comprehensive test suite with edge cases
- Easy-to-use API for distributed system simulation
- Type-safe implementations with proper error handling
- Rich debugging and visualization tools

## Installation

This project uses Poetry for dependency management. To install:

1. Make sure you have Poetry installed:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Clone the repository and install dependencies:
```bash
git clone <repository-url>
cd distributed-systems
poetry install
```

## Usage Examples

### Lamport Clocks

```python
from distributed_systems.core.lamport_clock import DistributedSystem

# Create a distributed system
system = DistributedSystem()

# Create processes
system.create_process("P1")
system.create_process("P2")

# Send messages between processes
system.send_message("P1", "P2", "Hello!")

# Display message history for all processes
system.display_all_histories()
```

### Vector Clocks

```python
from distributed_systems.core.vector_clock import DistributedSystemVC

# Create a distributed system
system = DistributedSystemVC()

# Create processes
system.create_process("P1")
system.create_process("P2")

# Send messages and check concurrency
system.send_message("P1", "P2", "Hello!")
p1_state = system.processes["P1"].vector_timestamp
p2_state = system.processes["P2"].vector_timestamp
if p1_state.concurrent_with(p2_state):
    print("Events are concurrent!")

system.display_all_histories()
```

### FIFO Broadcast

```python
from distributed_systems.core.fifo_broadcast import DistributedSystemFIFO, ProcessId

# Create a distributed system
system = DistributedSystemFIFO()

# Create processes
system.create_process(ProcessId("P1"))
system.create_process(ProcessId("P2"))

# Broadcast messages
system.broadcast_message(ProcessId("P1"), "First message")
system.broadcast_message(ProcessId("P1"), "Second message")
# Second message guaranteed to be delivered after first

system.display_all_histories()
```

## Running Examples

```bash
# Lamport clock example
poetry run python examples/lamport_example.py

# Vector clock example
poetry run python examples/vector_clock_example.py

# FIFO broadcast example
poetry run python examples/fifo_broadcast_example.py
```

## Development

### Running Tests
```bash
poetry run pytest
```

### Code Quality
This project uses Ruff for linting:
```bash
poetry run ruff check .
```

## License

MIT 