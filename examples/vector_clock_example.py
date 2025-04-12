from distributed_systems.core.vector_clock import DistributedSystemVC


def main():
    # Create a distributed system
    system = DistributedSystemVC()

    # Create three processes
    print("Creating processes P1, P2, and P3...")
    system.create_process("P1")
    system.create_process("P2")
    system.create_process("P3")

    print("\nSimulating message passing with concurrent events...\n")

    # Scenario 1: Sequential message passing
    print("1. Sequential message passing:")
    system.send_message("P1", "P2", "Hello from P1!")
    system.send_message("P2", "P3", "P2 forwarding message...")
    print("Message histories after sequential messages:\n")
    system.display_all_histories()

    # Scenario 2: Concurrent events
    print("\n2. Concurrent events:")
    # P1 and P3 send messages to P2 concurrently
    system.send_message("P1", "P2", "Concurrent message from P1")
    system.send_message("P3", "P2", "Concurrent message from P3")
    print("Message histories after concurrent messages:\n")
    system.display_all_histories()

    # Scenario 3: Causal message passing
    print("\n3. Causal message passing:")
    # P2 responds after receiving both concurrent messages
    system.send_message("P2", "P1", "Response to P1")
    system.send_message("P2", "P3", "Response to P3")
    print("Final message histories:\n")
    system.display_all_histories()


if __name__ == "__main__":
    main()
