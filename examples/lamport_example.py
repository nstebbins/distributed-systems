from distributed_systems.core.lamport_clock import DistributedSystem


def main():
    # Create a distributed system
    system = DistributedSystem()

    # Create three processes
    system.create_process("P1")
    system.create_process("P2")
    system.create_process("P3")

    # Simulate message passing between processes
    print("Simulating message passing between processes...\n")

    # P1 sends a message to P2
    system.send_message("P1", "P2", "Hello from P1!")

    # P2 processes and sends a message to P3
    system.send_message("P2", "P3", "P2 forwarding message...")

    # P3 sends messages to both P1 and P2
    system.send_message("P3", "P1", "Response to P1")
    system.send_message("P3", "P2", "Response to P2")

    # P1 sends final message to P3
    system.send_message("P1", "P3", "Final message from P1")

    print("Message history for all processes:\n")
    system.display_all_histories()


if __name__ == "__main__":
    main()
