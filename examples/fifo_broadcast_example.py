from distributed_systems.core.fifo_broadcast import DistributedSystemFIFO, ProcessId


def main() -> None:
    # Create a distributed system
    system = DistributedSystemFIFO()

    # Create three processes
    print("Creating processes P1, P2, and P3...")
    system.create_process(ProcessId("P1"))
    system.create_process(ProcessId("P2"))
    system.create_process(ProcessId("P3"))

    print("\nSimulating FIFO broadcast with messages from different processes...\n")

    # Scenario 1: Sequential broadcasts from P1
    print("1. Sequential broadcasts from P1:")
    system.broadcast_message(ProcessId("P1"), "First message from P1")
    system.broadcast_message(ProcessId("P1"), "Second message from P1")
    print("Message histories after P1's broadcasts:\n")
    system.display_all_histories()

    # Scenario 2: Concurrent broadcasts from P2 and P3
    print("\n2. Concurrent broadcasts from P2 and P3:")
    system.broadcast_message(ProcessId("P2"), "First message from P2")
    system.broadcast_message(ProcessId("P3"), "First message from P3")
    print("Message histories after concurrent broadcasts:\n")
    system.display_all_histories()

    # Scenario 3: More sequential broadcasts from P1
    print("\n3. More sequential broadcasts from P1:")
    system.broadcast_message(ProcessId("P1"), "Third message from P1")
    system.broadcast_message(ProcessId("P1"), "Fourth message from P1")
    print("Final message histories:\n")
    system.display_all_histories()


if __name__ == "__main__":
    main()
