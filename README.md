# Distributed Systems - Logical Clocks

This package provides implementations of logical clocks for distributed systems:
- Lamport Clocks: Simple scalar timestamps for partial ordering of events
- Vector Clocks: Vector timestamps for capturing causality and detecting concurrent events

## Features

- Implementation of Lamport and Vector logical clocks
- Beautiful terminal-based visualization of message passing
- Comprehensive test suite
- Easy-to-use API for distributed system simulation
- Detection of concurrent events (Vector Clocks)
- Causal ordering of events

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

## Usage

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

# Send messages between processes
system.send_message("P1", "P2", "Hello!")

# Check for concurrent events
p1_state = system.processes["P1"].vector_timestamp
p2_state = system.processes["P2"].vector_timestamp
if p1_state.concurrent_with(p2_state):
    print("Events are concurrent!")

# Display message history for all processes
system.display_all_histories()
```

To run the examples:
```bash
# Lamport clock example
poetry run python examples/lamport_example.py

# Vector clock example
poetry run python examples/vector_clock_example.py
```

## Running Tests

To run the test suite:
```bash
poetry run pytest
```

## Development

This project uses Ruff for linting. To run the linter:
```bash
poetry run ruff check .
```

## License

MIT 