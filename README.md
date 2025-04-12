# Distributed Systems - Lamport Clocks

This package provides an implementation of Lamport logical clocks for distributed systems, with a focus on visualization and easy testing.

## Features

- Implementation of Lamport logical clocks
- Beautiful terminal-based visualization of message passing
- Comprehensive test suite
- Easy-to-use API for distributed system simulation

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

Here's a simple example of how to use the Lamport clock implementation:

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

To run the example:
```bash
poetry run python examples/lamport_example.py
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